import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    mo.md(
        r"""
        # Manga Speaker — Training on Molab (marimo + CoreWeave)

        ### Steps to run:
        1. **Select GPU**: Click the hardware/specs badge in the top bar → Select GPU (e.g., NVIDIA RTX Pro 6000 or available GPU).
        2. **Upload Files**: In the left sidebar, click the **Files** icon (📁) and upload:
           - `manga_speaker_code.zip` (zipped project scripts, configs, splits)
           - `BYTE ML Task Data-20261012T094429Z-1-001.zip` (dataset zip)
        3. Run each cell sequentially.
        """
    )
    return (mo,)


@app.cell
def __():
    # Check GPU availability
    import subprocess
    gpu_info = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    print(gpu_info.stdout if gpu_info.returncode == 0 else "No GPU detected! Please select a GPU in the top hardware menu.")
    return (subprocess, gpu_info)


@app.cell
def __(subprocess):
    # Install required dependencies
    print("Installing packages...")
    cmd = [
        "pip", "install", "-q",
        "transformers>=4.49",
        "peft>=0.10",
        "bitsandbytes>=0.43",
        "accelerate>=0.28",
        "qwen-vl-utils",
        "langgraph",
        "pillow",
        "pyyaml"
    ]
    subprocess.run(cmd, check=True)
    print("Dependencies installed successfully!")
    return (cmd,)


@app.cell
def __():
    # Extract project code
    import os, zipfile, glob

    work_dir = os.path.abspath("manga_speaker")
    os.makedirs(work_dir, exist_ok=True)

    code_zips = glob.glob("*code*.zip") + glob.glob("manga_speaker*.zip")
    if code_zips:
        print(f"Extracting code from {code_zips[0]}...")
        with zipfile.ZipFile(code_zips[0], "r") as z:
            z.extractall(work_dir)
        print("Code extracted to:", work_dir)
    else:
        print("Note: If code was uploaded directly into current directory, continuing...")

    os.chdir(work_dir)
    print("Current working directory:", os.getcwd())
    print("Files:", os.listdir("."))
    return (code_zips, glob, os, work_dir, zipfile)


@app.cell
def __(os, zipfile):
    # Extract manga dataset
    dataset_dir = os.path.join(os.getcwd(), "dataset")
    os.makedirs(dataset_dir, exist_ok=True)

    # If dataset images aren't extracted yet:
    if not os.path.exists(os.path.join(dataset_dir, "development", "images")):
        data_zips = [f for f in os.listdir("..") if f.endswith(".zip") and ("BYTE" in f or "dataset" in f)] + \
                    [f for f in os.listdir(".") if f.endswith(".zip") and ("BYTE" in f or "dataset" in f)]
        
        # If not present locally in Molab, download via gdown from your Google Drive link
        if not data_zips:
            print("Dataset zip not found locally. If you uploaded it to Google Drive, enter the share link below:")
            # Replace with your Google Drive share link if using Drive:
            GDRIVE_LINK = ""  # e.g., "https://drive.google.com/file/d/XXXXX/view?usp=sharing"
            if GDRIVE_LINK:
                import subprocess
                subprocess.run(["pip", "install", "-q", "gdown"], check=True)
                import gdown
                gdown.download(GDRIVE_LINK, "dataset.zip", fuzzy=True)
                data_zips = ["dataset.zip"]
        
        if data_zips:
            zip_path = data_zips[0] if os.path.exists(data_zips[0]) else os.path.join("..", data_zips[0])
            print(f"Extracting dataset from {zip_path}...")
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(os.getcwd())
            print("Dataset extracted successfully!")
        else:
            print("Dataset zip not found! Please download or upload your dataset zip.")
    else:
        print("Dataset already present.")
    return (data_zips, dataset_dir)


@app.cell
def __(os):
    # Verify dataset & splits
    import json
    if os.path.exists("splits.json") and os.path.exists("dataset/development/labels.jsonl"):
        with open("splits.json") as f:
            splits = json.load(f)
        with open("dataset/development/labels.jsonl") as f:
            labels = [json.loads(line) for line in f]
        print(f"Train sequences: {len(splits['train'])} | Val sequences: {len(splits['val'])} | Total labels: {len(labels)}")
    else:
        print("Waiting for files to be extracted...")
    return (json, labels, splits)


@app.cell
def __(subprocess):
    # Run LoRA Training
    # Detect GPU memory size to choose full 16-bit or 4-bit quantization
    gpu_check = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
        capture_output=True, text=True
    )
    gpu_desc = gpu_check.stdout.strip()
    print("Hardware:", gpu_desc)

    import sys
    train_cmd = [
        sys.executable, "scripts/train_lora.py",
        "--dataset", "dataset",
        "--labels", "dataset/development/labels.jsonl",
        "--splits", "splits.json",
        "--split", "all",
        "--model-id", "Qwen/Qwen2.5-VL-3B-Instruct",
        "--out", "adapters/qwen_manga_lora_v2",
        "--epochs", "3",
        "--lr", "2e-4",
        "--grad-accum", "4",
        "--rank", "32",
        "--context-pages", "1",
        "--load-4bit",  # Keeps memory lean and fast
        "--seed", "42"
    ]

    print("Launching training with command:\n", " ".join(train_cmd))
    proc = subprocess.Popen(train_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line, end="", flush=True)
    proc.wait()
    print(f"\nTraining finished with exit code {proc.returncode}")
    return (gpu_check, gpu_desc, line, proc, sys, train_cmd)


@app.cell
def __(subprocess, sys):
    # Run Inference on Test Set
    inf_cmd = [
        sys.executable, "scripts/run_inference.py",
        "--dataset", "dataset",
        "--ids-from", "dataset/sample_submission.jsonl",
        "--out", "test_predictions_v2.jsonl",
        "--config", "configs/default.yaml",
        "--adapter", "adapters/qwen_manga_lora_v2",
        "--set", "model.load_4bit=true", "model.model_id=Qwen/Qwen2.5-VL-3B-Instruct"
    ]

    print("Running inference on test sequences...")
    proc_inf = subprocess.Popen(inf_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line_inf in proc_inf.stdout:
        print(line_inf, end="", flush=True)
    proc_inf.wait()
    print(f"\nInference complete! Predictions written to test_predictions_v2.jsonl")
    return (inf_cmd, line_inf, proc_inf)


@app.cell
def __(os):
    # Verify outputs and instructions to download
    print("Output files generated:")
    for out_name in ["test_predictions_v2.jsonl", "adapters/qwen_manga_lora_v2"]:
        if os.path.exists(out_name):
            print(f"  [OK] {out_name}")
        else:
            print(f"  [MISSING] {out_name}")

    print("\nTo download:")
    print("1. Open the Files panel (folder icon on the left).")
    print("2. Right-click 'test_predictions_v2.jsonl' -> Download.")
    return (out_name,)


if __name__ == "__main__":
    app.run()
