import copy
import yaml

DEFAULTS = {
    "model": {"backend": "transformers", "model_id": "Qwen/Qwen2.5-VL-7B-Instruct", "adapter": None,
              "load_4bit": False, "min_pixels": 200704, "max_pixels": 1254400,
              "base_url": "http://localhost:8000/v1", "api_model": "Qwen/Qwen2.5-VL-7B-Instruct"},
    "pipeline": {"context_pages": 1, "retries": 2, "max_new_tokens": 1536, "reconcile": False,
                 "verify_ocr": False, "verify_threshold": 55},
}


def load_config(path=None, overrides=None):
    cfg = copy.deepcopy(DEFAULTS)
    if path:
        with open(path) as f:
            user = yaml.safe_load(f) or {}
        for sec, vals in user.items():
            cfg.setdefault(sec, {}).update(vals or {})
    for ov in overrides or []:  # e.g. pipeline.reconcile=true
        key, val = ov.split("=", 1)
        sec, name = key.split(".", 1)
        cfg[sec][name] = yaml.safe_load(val)
    return cfg
