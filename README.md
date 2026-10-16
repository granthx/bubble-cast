#  Bubblecast — Multimodal Manga Reader & Dialogue Intelligence

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0%2B-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Model](https://img.shields.io/badge/Model-Qwen2.5--VL-blueviolet)](https://github.com/QwenLM/Qwen2.5-VL)

**Bubblecast** is an end-to-end multimodal intelligence platform and interactive reader designed for manga, webtoons, and graphic novels. Built on open-weight Vision-Language Models (**Qwen2.5-VL**), it performs sequential speech balloon extraction, reading-order reconstruction, and cross-panel speaker identification across 3-page spreads.

---

##  Architecture & Multi-Agent Pipeline

To prevent identity scrambling across panel borders, Bubblecast utilizes a stateful **multi-agent pipeline** with continuous carry-forward visual memory.

```
       [Page 1 Image] ──► Agent 1: VLM Reader ──► Agent 2: Normalizer ──► [Transcript 1]
                                 │                                               │
                                 ▼ (Carry-forward Visual Context)                ▼
       [Page 2 Image] ──► Agent 1: VLM Reader ──► Agent 2: Normalizer ──► [Transcript 2]
                                 │                                               │
                                 ▼ (Carry-forward Visual Context)                ▼
       [Page 3 Image] ──► Agent 1: VLM Reader ──► Agent 2: Normalizer ──► [Transcript 3]
                                                                                 │
                                                                                 ▼
                                            Agent 3: Schema Guard & Finalizer ──► Output Script
```

### Core Engine Modules

1. **Sequential Memory Reader (`src/mangaspeak/graph.py`, `prompts.py`)**  
   Processes sequential spreads conditioned on previous visual context and transcripts to maintain consistent character tags (`char1`, `char2`, `NARRATION`) across page turns.
2. **Deterministic Text Normalizer (`src/mangaspeak/clean.py`)**  
   Filters background sound effects (SFX) and scanlator artifacts while preserving stutters, repeated letters, and emotional punctuation balloons (`...`, `?!`).
3. **Schema Guard & Finalizer (`src/mangaspeak/graph.py`)**  
   Enforces strict JSON schema guarantees and gracefully handles silent pages and splash spreads without spurious hallucinations.

---

##  Adaptation & Parameter-Efficient Fine-Tuning

In strict compliance with open-weight and open-source standards, Bubblecast relies exclusively on local, open-access tools:

- **Base VLM**: `Qwen/Qwen2.5-VL-3B-Instruct` / `Qwen2-VL-7B`
- **Fine-Tuning Method**: Parameter-Efficient Fine-Tuning (**PEFT LoRA**) with 4-bit NF4 quantization (`bitsandbytes`).
- **Target Attention Modules**: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`.
- **LoRA Configuration**: Rank $r = 32$, Alpha $\alpha = 64$, dropout $0.05$.
- **Loss Masking**: Gradients computed exclusively on structured answer JSON tokens.

###  Trained Model Checkpoints & Verification

The trained PEFT LoRA adapter configurations, tokenizers, and processor artifacts are committed directly in the repository under [`adapters/`](file:///c:/Users/Granth/All%20project/manga_speaker/adapters):

| Checkpoint Name | Directory | Base Architecture | LoRA Capacity | Status |
| :--- | :--- | :--- | :---: | :--- |
| **Qwen Manga LoRA v2** (Newly Trained) | `adapters/qwen_manga_lora_v2/` | Qwen2.5-VL | **Rank 32, Alpha 64** | **Committed in repo** |
| **Qwen Manga LoRA v1** (Baseline) | `adapters/v1/` | Qwen2.5-VL | **Rank 16, Alpha 32** | **Committed in repo** |
| **Complete Weights Package** | `new trained model/` | Qwen2.5-VL | Safetensors (297 MB) | Packed for release / drive |

#### Verifying & Loading the Trained Adapter:
```python
from peft import PeftConfig, PeftModel
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

# 1. Load the committed LoRA adapter configuration
config = PeftConfig.from_pretrained("adapters/qwen_manga_lora_v2")
print(f"Base model: {config.base_model_name_or_path} | LoRA Rank: {config.r} | Alpha: {config.lora_alpha}")

# 2. Attach trained LoRA adapter to base model
base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    config.base_model_name_or_path,
    torch_dtype="auto",
    device_map="auto"
)
model = PeftModel.from_pretrained(base_model, "adapters/qwen_manga_lora_v2")
```

---

##  Repository Structure

```
bubble-cast/
├── adapters/                 # Trained LoRA adapters & model metadata
│   ├── qwen_manga_lora_v2/   # Newly trained model (Rank 32, Alpha 64)
│   │   ├── adapter_config.json
│   │   ├── tokenizer.json
│   │   ├── tokenizer_config.json
│   │   ├── processor_config.json
│   │   ├── chat_template.jinja
│   │   └── README.md
│   └── v1/                   # Baseline LoRA adapter checkpoint (Rank 16)
│       └── adapter_config.json
├── new trained model/        # Release archive for full weights package
│   └── qwen_manga_lora_v2.zip
├── backend/                  # FastAPI REST API & domain services
│   ├── app.py                # Route controllers & CORS config
│   ├── data.py               # Sequence repository & character profiles
│   ├── exports.py            # Screenplay & JSON export generators
│   ├── inference.py          # Multimodal image upload pipeline
│   └── multilingual.py       # 4 Comic traditions & reading flows
├── frontend/                 # React 19 + TypeScript + Vite web studio
│   ├── src/
│   │   ├── api/              # Strongly typed API client
│   │   ├── components/       # Reader, Multilingual, Upload, Export
│   │   └── styles/           # Dark Editorial Studio design system
│   ├── package.json
│   └── vite.config.ts
├── src/mangaspeak/           # Core AI pipeline & agent graph
│   ├── clean.py              # Text normalizer & SFX filter
│   ├── graph.py              # LangGraph multi-agent orchestrator
│   ├── prompts.py            # Context-aware sequential prompt templates
│   └── vlm.py                # Local VLM loader with 4-bit quantization
├── scripts/                  # Training, evaluation & inference runners
│   ├── train_lora.py         # PEFT LoRA fine-tuning script
│   ├── run_inference.py      # End-to-end batch inference
│   ├── evaluate.py           # Evaluation runner
│   └── make_split.py         # Sequence dataset splitter
├── configs/                  # Model & runtime configuration
│   └── default.yaml
├── dataset/                  # Metadata, schemas & scoring harness
│   ├── sequences.json        # Sequence metadata index
│   └── score.py              # Competition evaluation metric
├── test_predictions_7b.jsonl # 15-sequence test benchmark predictions
└── README.md
```

---

##  Web Studio Quickstart

Bubblecast features a dedicated production web studio powered by a **FastAPI** backend and a **React 19 + TypeScript** frontend.

### 1. Launch the FastAPI Backend Server
```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/health`

### 2. Launch the React Web Studio
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

### 3. Studio Workspaces
- **Sequential Reader (`/reader`)**: Interactive 3-page manga spread with bounding boxes, speech bubble highlights, and speaker badges.
- **Multilingual Studio (`/multilingual`)**: Architectural reading flow and bilingual panel comparison across 4 comic traditions (Japanese Manga RTL, Korean Webtoon Vertical, American Comics LTR, Franco-Belgian BD).
- **Upload & Analysis (`/upload`)**: Direct upload of 1–3 custom manga pages with live multimodal dialogue extraction.
- **Deliverables & Export (`/export`)**: Direct downloads of formatted screenplay scripts (`.txt`), sequence annotations (`.json`), and submission predictions (`.jsonl`).

---

##  Citations & External References

- **Base Vision-Language Models**:
  - *Qwen2.5-VL / Qwen2-VL*: Alibaba Cloud, Qwen Team (2024). Open-weight multimodal model. [Qwen2.5-VL GitHub](https://github.com/QwenLM/Qwen2.5-VL).
- **Parameter-Efficient Adaptation & Quantization**:
  - *PEFT (Parameter-Efficient Fine-Tuning)*: Hugging Face (2023). [PEFT GitHub](https://github.com/huggingface/peft).
  - *QLoRA / bitsandbytes*: Dettmers et al. (2023). *QLoRA: Efficient Finetuning of Quantized LLMs*. [bitsandbytes GitHub](https://github.com/bitsandbytes-foundation/bitsandbytes).
  - *Transformers & Accelerate*: Hugging Face (2020). [Transformers GitHub](https://github.com/huggingface/transformers).
- **Multi-Agent Orchestration & Frameworks**:
  - *LangGraph*: LangChain AI (2024). Graph-based stateful agent orchestration.
  - *FastAPI*: Tiangolo (2018). Modern, high-performance web API framework for Python.
  - *React & Vite*: React Team & Evan You (2024). Modern frontend component architecture.
