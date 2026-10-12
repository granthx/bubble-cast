"""LangGraph multi-agent pipeline for one 3-page sequence.

read_page -> verify_clean -> advance -> (more pages? yes: read_page | no: reconcile) -> finalize
"""
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from .clean import apply_merge, clean_lines, parse_lines, refine_sequence
from .jsonutil import extract_json
from .prompts import build_page_messages, build_reconcile_messages
from .verify import filter_by_ocr


class SeqState(TypedDict, total=False):
    sequence_id: str
    image_paths: List[str]
    page_idx: int
    current: List[Dict[str, str]]
    pages: List[List[Dict[str, str]]]
    log: List[str]
    result: Dict[str, Any]


def build_graph(vlm, cfg):
    p = cfg["pipeline"]

    # ---- Agent 1: page reader (VLM) ----
    def read_page(state: SeqState):
        i, paths, pages = state["page_idx"], state["image_paths"], state["pages"]
        labels = [l["speaker"] for pg in pages for l in pg]
        lo = max(0, i - p["context_pages"])
        ctx = [(j, paths[j], pages[j]) for j in range(lo, i)]
        msgs = build_page_messages(i, len(paths), paths[i], ctx, labels)
        lines, log = None, list(state.get("log", []))

        # Try greedy first, then with temperature for diversity
        temperatures = [0.0] + [0.3] * p["retries"]
        for attempt, temp in enumerate(temperatures):
            raw = vlm.generate(msgs, p["max_new_tokens"], temp)
            lines = parse_lines(extract_json(raw))
            if lines is not None:
                break
            log.append(f"page{i + 1}: unparsable output, retry {attempt + 1}")

        if lines is None:
            log.append(f"page{i + 1}: giving up -> empty page")
            lines = []

        return {"current": lines, "log": log}

    # ---- Agent 2: cleaner / verifier (rules + optional OCR) ----
    def verify_clean(state: SeqState):
        i = state["page_idx"]
        lines = clean_lines(state["current"])
        if p["verify_ocr"] and lines:
            lines = filter_by_ocr(lines, state["image_paths"][i], p["verify_threshold"])
        return {"pages": state["pages"] + [lines]}

    def advance(state: SeqState):
        return {"page_idx": state["page_idx"] + 1}

    def route(state: SeqState):
        return "read_page" if state["page_idx"] < len(state["image_paths"]) else "reconcile"

    # ---- Agent 3: identity reconciler (VLM sees all pages, merges duplicate labels) ----
    def reconcile(state: SeqState):
        pages = state["pages"]
        labels = {l["speaker"] for pg in pages for l in pg if l["speaker"] != "NARRATION"}
        if not p["reconcile"] or len(labels) < 2:
            return {}
        raw = vlm.generate(build_reconcile_messages(state["image_paths"], pages), 256, 0.0)
        obj = extract_json(raw) or {}
        merge = obj.get("merge") if isinstance(obj, dict) else None
        if not isinstance(merge, dict):
            return {}
        return {"pages": apply_merge(pages, merge), "log": state.get("log", []) + [f"merge: {merge}"]}

    # ---- Agent 4: finalizer / schema guard ----
    def finalize(state: SeqState):
        # Strip raw to just speaker+text
        pages = [[{"speaker": l["speaker"], "text": l["text"]} for l in pg] for pg in state["pages"]]
        # Apply dedup + speaker refinement
        pages = refine_sequence(pages)
        # Pad to expected number of pages
        while len(pages) < len(state["image_paths"]):
            pages.append([])
        return {"result": {"sequence_id": state["sequence_id"], "pages": pages[:len(state["image_paths"])]}}

    g = StateGraph(SeqState)
    for name, fn in [("read_page", read_page), ("verify_clean", verify_clean), ("advance", advance),
                     ("reconcile", reconcile), ("finalize", finalize)]:
        g.add_node(name, fn)
    g.set_entry_point("read_page")
    g.add_edge("read_page", "verify_clean")
    g.add_edge("verify_clean", "advance")
    g.add_conditional_edges("advance", route, {"read_page": "read_page", "reconcile": "reconcile"})
    g.add_edge("reconcile", "finalize")
    g.add_edge("finalize", END)
    return g.compile()


def run_sequence(app, sequence_id, image_paths):
    out = app.invoke({"sequence_id": sequence_id, "image_paths": image_paths,
                      "page_idx": 0, "pages": [], "current": [], "log": []})
    return out["result"], out.get("log", [])
