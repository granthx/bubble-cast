"""Open-weight vision-language model backends. NO hosted inference APIs (Groq, DashScope, OpenAI, ...) allowed."""
import base64
import ipaddress
import mimetypes
from urllib.parse import urlparse

from PIL import Image


def to_hf_messages(messages):
    """Replace {"type":"image","path":p} with HF placeholders and collect PIL images in order."""
    images, out = [], []
    for m in messages:
        content = m["content"]
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        parts = []
        for c in content:
            if c["type"] == "image":
                parts.append({"type": "image"})
                images.append(Image.open(c["path"]).convert("RGB"))
            else:
                parts.append({"type": "text", "text": c["text"]})
        out.append({"role": m["role"], "content": parts})
    return out, images


class BaseVLM:
    def generate(self, messages, max_new_tokens=1536, temperature=0.0):
        raise NotImplementedError


class TransformersVLM(BaseVLM):
    def __init__(self, model_id, adapter=None, load_4bit=False, min_pixels=None, max_pixels=None):
        import torch
        from transformers import AutoProcessor
        try:
            from transformers import AutoModelForImageTextToText as ModelCls
        except ImportError:  # older transformers
            from transformers import Qwen2_5_VLForConditionalGeneration as ModelCls
        kw = {"device_map": "auto"}
        if torch.cuda.is_available():
            kw["torch_dtype"] = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        if load_4bit:
            from transformers import BitsAndBytesConfig
            kw["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
        self.model = ModelCls.from_pretrained(model_id, **kw)
        if adapter:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter)
        self.model.eval()
        pkw = {}
        if min_pixels:
            pkw["min_pixels"] = min_pixels
        if max_pixels:
            pkw["max_pixels"] = max_pixels
        self.processor = AutoProcessor.from_pretrained(model_id, **pkw)

    def generate(self, messages, max_new_tokens=1536, temperature=0.0):
        import torch
        hf_msgs, images = to_hf_messages(messages)
        text = self.processor.apply_chat_template(hf_msgs, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=images or None, return_tensors="pt").to(self.model.device)
        gen = {"max_new_tokens": max_new_tokens, "do_sample": temperature > 0}
        if temperature > 0:
            gen.update(temperature=temperature, top_p=0.9)
        with torch.no_grad():
            out = self.model.generate(**inputs, **gen)
        new = out[:, inputs["input_ids"].shape[1]:]
        return self.processor.batch_decode(new, skip_special_tokens=True)[0]


def _assert_local(url):
    host = urlparse(url).hostname or ""
    if host in ("localhost", "host.docker.internal"):
        return
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_loopback or ip.is_private:
            return
    except ValueError:
        pass
    raise ValueError(f"Refusing non-local endpoint '{url}'. The task forbids hosted inference APIs; "
                     "run the open-weight model yourself (vLLM / Ollama / llama.cpp server on localhost).")


class OpenAILocalVLM(BaseVLM):
    """Talks to YOUR OWN OpenAI-compatible server (vLLM, Ollama, LM Studio) hosting open weights."""

    def __init__(self, base_url, model):
        _assert_local(base_url)
        from openai import OpenAI
        self.client = OpenAI(base_url=base_url, api_key="local")
        self.model = model

    @staticmethod
    def _data_url(path):
        mime = mimetypes.guess_type(path)[0] or "image/png"
        with open(path, "rb") as f:
            return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

    def generate(self, messages, max_new_tokens=1536, temperature=0.0):
        msgs = []
        for m in messages:
            if isinstance(m["content"], str):
                msgs.append(m)
                continue
            parts = [{"type": "image_url", "image_url": {"url": self._data_url(c["path"])}}
                     if c["type"] == "image" else {"type": "text", "text": c["text"]} for c in m["content"]]
            msgs.append({"role": m["role"], "content": parts})
        r = self.client.chat.completions.create(model=self.model, messages=msgs,
                                                max_tokens=max_new_tokens, temperature=temperature)
        return r.choices[0].message.content or ""


def build_vlm(cfg):
    m = cfg["model"]
    if m["backend"] == "transformers":
        return TransformersVLM(m["model_id"], m.get("adapter"), m.get("load_4bit", False),
                               m.get("min_pixels"), m.get("max_pixels"))
    if m["backend"] == "openai_local":
        return OpenAILocalVLM(m["base_url"], m["api_model"])
    raise ValueError(f"Unknown backend {m['backend']}")
