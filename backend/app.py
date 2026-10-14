"""
FastAPI Backend Server for Manga Speaker Studio.
Provides REST API endpoints for manga reading, multilingual analysis, uploads, and deliverable exports.
"""
import io
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, Response

from .data import DATASET_DIR, README_FILE, TEST_PRED_FILE, repo
from .exports import generate_screenplay_script, get_sequence_json_string
from .inference import analyze_uploaded_images
from .multilingual import MULTILINGUAL_TRADITIONS

app = FastAPI(
    title="Manga Speaker API",
    description="Multimodal Manga Reader & Dialogue Intelligence Backend API",
    version="2.0.0",
)

# CORS setup for local React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def get_health():
    """Health check and model status."""
    return {
        "status": "ok",
        "service": "Manga Speaker Dialogue Intelligence",
        "model": "Qwen2-VL-7B-LoRA",
        "test_sequences": len(repo.test_predictions),
        "dev_sequences": len(repo.dev_labels),
        "total_metadata": len(repo.sequences_meta),
    }


@app.get("/api/sources")
def get_sources():
    """Returns available data sources (Test Predictions vs Development Archive)."""
    return repo.get_sources()


@app.get("/api/sequences")
def get_sequences(source: str = Query("test", pattern="^(test|dev)$")):
    """Returns list of sequences for the selected source with metadata."""
    return repo.list_sequences(source=source)


@app.get("/api/sequences/{sequence_id}")
def get_sequence_detail(
    sequence_id: str,
    source: str = Query("test", pattern="^(test|dev)$"),
):
    """Returns complete sequence details, pages, dialogues, and active characters."""
    seq = repo.get_sequence_detail(sequence_id=sequence_id, source=source)
    if not seq:
        raise HTTPException(status_code=404, detail=f"Sequence '{sequence_id}' not found in source '{source}'.")
    return seq


@app.get("/api/images/{image_path:path}")
def serve_image(image_path: str):
    """Safely serves manga artwork page images from the dataset folder."""
    # Prevent directory traversal
    clean_path = Path(image_path).as_posix()
    if ".." in clean_path or clean_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid image path.")

    full_path = (DATASET_DIR / clean_path).resolve()
    # Ensure resolved path is inside DATASET_DIR
    if not str(full_path).startswith(str(DATASET_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Image file not found.")

    suffix = full_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    media_type = media_types.get(suffix, "application/octet-stream")

    return FileResponse(full_path, media_type=media_type)


@app.get("/api/multilingual")
def get_multilingual_traditions():
    """Returns 4 comic traditions with architectural reading flow and bilingual panels."""
    return MULTILINGUAL_TRADITIONS


@app.post("/api/analyze")
async def analyze_manga_upload(
    files: List[UploadFile] = File(...),
    reading_flow: str = Form("Japanese Manga (Right-to-Left)"),
    language_mode: str = Form("Auto-Detect"),
):
    """Uploads 1 to 3 sequential manga page images and runs dialogue extraction."""
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    if len(files) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 sequential pages allowed.")

    temp_dir = tempfile.mkdtemp(prefix="manga_upload_")
    try:
        saved_paths = []
        for idx, file in enumerate(files):
            # Validate extension
            ext = Path(file.filename or f"page{idx}.png").suffix.lower()
            if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
                raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Use PNG, JPG, or WEBP.")

            dest = Path(temp_dir) / f"page_{idx + 1}{ext}"
            content = await file.read()
            with open(dest, "wb") as f:
                f.write(content)
            saved_paths.append(dest)

        result = analyze_uploaded_images(
            image_paths=saved_paths,
            reading_flow=reading_flow,
            language_mode=language_mode,
        )
        return result
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/api/exports/predictions")
def download_predictions():
    """Direct download for official benchmark predictions JSONL."""
    if not TEST_PRED_FILE.exists():
        raise HTTPException(status_code=404, detail="Predictions file test_predictions_7b.jsonl not found.")
    return FileResponse(
        TEST_PRED_FILE,
        filename="test_predictions_7b.jsonl",
        media_type="application/jsonl",
    )


@app.get("/api/exports/readme")
def download_readme():
    """Direct download for technical methodology report README.md."""
    if not README_FILE.exists():
        raise HTTPException(status_code=404, detail="README.md not found.")
    return FileResponse(
        README_FILE,
        filename="README.md",
        media_type="text/markdown",
    )


@app.get("/api/exports/sequence/{sequence_id}/json")
def download_sequence_json(
    sequence_id: str,
    source: str = Query("test", pattern="^(test|dev)$"),
):
    """Direct download for formatted JSON object of a single sequence."""
    json_str = get_sequence_json_string(sequence_id=sequence_id, source=source)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{sequence_id}.json"'},
    )


@app.get("/api/exports/sequence/{sequence_id}/script")
def download_sequence_script(
    sequence_id: str,
    source: str = Query("test", pattern="^(test|dev)$"),
):
    """Direct download for plain-text graphic novel screenplay script."""
    data_source = repo.test_predictions if source == "test" else repo.dev_labels
    pages = data_source.get(sequence_id, [[], [], []])
    script_str = generate_screenplay_script(sequence_id=sequence_id, pages_dialogues=pages)
    return PlainTextResponse(
        content=script_str,
        headers={"Content-Disposition": f'attachment; filename="{sequence_id}_script.txt"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
