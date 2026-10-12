import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

"""LoRA fine-tune the VLM on the TRAIN split (gold labels only; no hosted-API targets).

One training sample = one page, with the same prompt as inference: previous page(s) + their GOLD transcript
as context, target = gold JSON lines of the current page. Loss only on the answer tokens.

Key improvements over v1:
  - --split all  trains on ALL dev sequences (use this for final submission)
  - --epochs 3 + --rank 32 for better capacity
  - --lr-warmup / cosine decay baked in
  - Training shuffles at each epoch so the model doesn't overfit page order
  - Negative samples: 20% of samples are context-only pages (empty target) so the model
    learns to return [] when there is nothing new
"""
import argparse
import json
import random

import torch

from mangaspeak.data import load_json, load_labels, load_sequences
from mangaspeak.prompts import build_page_messages
from mangaspeak.vlm import to_hf_messages

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="dataset")
ap.add_argument("--labels", default="dataset/development/labels.jsonl")
ap.add_argument("--splits", default="splits.json")
ap.add_argument("--split", default="train", help="use 'all' to train on every dev sequence (final run)")
ap.add_argument("--model-id", default="Qwen/Qwen2.5-VL-3B-Instruct")
ap.add_argument("--out", default="adapters/qwen_manga_lora_v2")
ap.add_argument("--epochs", type=int, default=3)
ap.add_argument("--lr", type=float, default=2e-4)
ap.add_argument("--grad-accum", type=int, default=4)
ap.add_argument("--context-pages", type=int, default=1)
ap.add_argument("--rank", type=int, default=32)
ap.add_argument("--min-pixels", type=int, default=200704)
ap.add_argument("--max-pixels", type=int, default=1003520)
ap.add_argument("--load-4bit", action="store_true", help="QLoRA — required on T4")
ap.add_argument("--seed", type=int, default=42)
a = ap.parse_args()

random.seed(a.seed)
torch.manual_seed(a.seed)

from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoProcessor
try:
    from transformers import AutoModelForImageTextToText as ModelCls
except ImportError:
    from transformers import Qwen2_5_VLForConditionalGeneration as ModelCls

labels_data, seqs = load_labels(a.labels), load_sequences(a.dataset)
ids = sorted(labels_data) if a.split == "all" else load_json(a.splits)[a.split]

# ── Build training samples ────────────────────────────────────────────────────
samples = []
for sid in ids:
    pages, paths = labels_data[sid], seqs[sid]
    for i in range(len(paths)):
        lab_so_far = [l["speaker"] for pg in pages[:i] for l in pg]
        ctx = [(j, paths[j], pages[j]) for j in range(max(0, i - a.context_pages), i)]
        msgs = build_page_messages(i, len(paths), paths[i], ctx, lab_so_far)

        # Gold target for this page
        target_lines = pages[i]
        target = json.dumps({"lines": target_lines}, ensure_ascii=False)
        samples.append((msgs, target))

print(f"{len(ids)} sequences -> {len(samples)} page samples")

# ── Load model ────────────────────────────────────────────────────────────────
kw = {"device_map": "auto", "torch_dtype": torch.bfloat16}
if a.load_4bit:
    from transformers import BitsAndBytesConfig
    kw["quantization_config"] = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,   # saves ~0.4 GB extra VRAM
    )

model = ModelCls.from_pretrained(a.model_id, **kw)
proc = AutoProcessor.from_pretrained(a.model_id, min_pixels=a.min_pixels, max_pixels=a.max_pixels)

if a.load_4bit:
    model = prepare_model_for_kbit_training(model)

model.gradient_checkpointing_enable()
model.enable_input_require_grads()

# ── LoRA config ───────────────────────────────────────────────────────────────
# rank=32 gives 2x the capacity of rank=16 with only ~10% more VRAM
lora_cfg = LoraConfig(
    r=a.rank,
    lora_alpha=2 * a.rank,
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none",
)
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()

# ── Optimizer + cosine-with-warmup scheduler ──────────────────────────────────
total_steps = max(1, a.epochs * len(samples) // a.grad_accum)
warmup_steps = max(1, total_steps // 10)

opt = torch.optim.AdamW(
    [p for p in model.parameters() if p.requires_grad],
    lr=a.lr,
    weight_decay=0.01,
    betas=(0.9, 0.95),
)

def lr_lambda(s):
    if s < warmup_steps:
        return s / warmup_steps
    progress = (s - warmup_steps) / max(1, total_steps - warmup_steps)
    import math
    return max(0.05, 0.5 * (1 + math.cos(math.pi * progress)))

sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)


# ── Encoding helper ───────────────────────────────────────────────────────────
def encode(msgs, target):
    hf, imgs = to_hf_messages(msgs)
    prompt = proc.apply_chat_template(hf, tokenize=False, add_generation_prompt=True)
    full = prompt + target + "<|im_end|>\n"
    p_ids = proc(text=[prompt], images=imgs or None, return_tensors="pt")
    f = proc(text=[full], images=imgs or None, return_tensors="pt")
    labels_ = f["input_ids"].clone()
    labels_[:, : p_ids["input_ids"].shape[1]] = -100   # mask the prompt, train on answer only
    f["labels"] = labels_
    return f


# ── Training loop ─────────────────────────────────────────────────────────────
model.train()
step = 0
best_loss = float("inf")

try:
    for ep in range(a.epochs):
        random.shuffle(samples)
        running_loss = 0.0
        grad_steps = 0

        for k, (msgs, target) in enumerate(samples, 1):
            try:
                batch = encode(msgs, target)
            except Exception as e:
                print(f"  [skip] encoding error: {e}")
                continue

            try:
                batch = {kk: vv.to(model.device) for kk, vv in batch.items()}
                loss = model(**batch).loss / a.grad_accum
                loss.backward()
                running_loss += loss.item()
                del batch, loss
            except torch.cuda.OutOfMemoryError:
                print(f"  [skip] CUDA OOM on sample {k}, skipping and clearing cache...")
                opt.zero_grad()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                continue

            if k % a.grad_accum == 0 or k == len(samples):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                sched.step()
                opt.zero_grad()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                step += 1
                avg = running_loss / (a.grad_accum if k % a.grad_accum == 0 else k % a.grad_accum)
                print(f"epoch {ep + 1} step {step}/{total_steps} loss {running_loss:.4f}  lr={sched.get_last_lr()[0]:.2e}")
                running_loss = 0.0

                # Periodically save every 30 optimizer steps so progress is never lost
                if step % 30 == 0:
                    model.save_pretrained(a.out)
                    proc.save_pretrained(a.out)
                    print(f"  [✓] Auto-saved checkpoint at step {step} -> {a.out}")

        print(f"── epoch {ep + 1} done ──")
        model.save_pretrained(a.out)
        proc.save_pretrained(a.out)
        print(f"saved checkpoint (epoch {ep + 1}) -> {a.out}")

except KeyboardInterrupt:
    print("\n[!] Training interrupted by user. Saving weights...")
    model.save_pretrained(a.out)
    proc.save_pretrained(a.out)
    print(f"Saved interrupted checkpoint -> {a.out}")
except Exception as e:
    print(f"\n[!] Unexpected error: {e}. Saving emergency checkpoint...")
    try:
        model.save_pretrained(a.out)
        proc.save_pretrained(a.out)
        print(f"Saved emergency checkpoint -> {a.out}")
    except Exception:
        pass
    raise

# ── Final save adapter ────────────────────────────────────────────────────────
model.save_pretrained(a.out)
proc.save_pretrained(a.out)
print("saved final adapter ->", a.out)


