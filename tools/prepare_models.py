import hashlib
import json
import os
import sys
from pathlib import Path

REPO_NAME = "BitStudio-models"
CATALOG_PATH = Path("models/catalog.json")
RELEASE_DIR = Path("release_assets")
DEEPFILTERSRC = "https://github.com/Rikorose/DeepFilterNet/raw/main/models/DeepFilterNet3_onnx.tar.gz"

HTDEMUCHS_ONNX = "htdemucs.onnx"
DEEPFILTER_TAR = "DeepFilterNet3_onnx.tar.gz"


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_size_bytes(path: Path) -> int:
    return path.stat().st_size


def ensure_release_dir() -> Path:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    return RELEASE_DIR


def export_htdemucs(target_dir: Path) -> Path:
    import demucs_onnx.export

    target = target_dir / HTDEMUCHS_ONNX
    demucs_onnx.export.export_to_onnx("htdemucs", str(target))
    return target


def verify_htdemucs_onnx(path: Path) -> None:
    import numpy as np
    import onnxruntime as ort

    input_shape = (1, 2, 343980)
    dummy = np.zeros(input_shape, dtype=np.float32)
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: dummy})
    stems = outputs[0]
    assert stems.shape == (1, 4, 2, 343980), f"Bad output shape: {stems.shape}"
    assert np.isfinite(stems).all(), "Output contains NaN/Inf"


def download_deepfilter_net(target_dir: Path) -> Path:
    import requests

    target = target_dir / DEEPFILTER_TAR
    resp = requests.get(DEEPFILTERSRC, stream=True, timeout=60)
    resp.raise_for_status()
    target.write_bytes(resp.content)
    return target


FILENAME_MAP = {
    "deepfilternet3-denoise": "DeepFilterNet3_onnx.tar.gz",
    "htdemucs-4stem-v4": "htdemucs.onnx",
}


def release_download_url(tag: str, github_repo: str, filename: str) -> str:
    return f"https://github.com/{github_repo}/releases/download/{tag}/{filename}"


def rewrite_catalog(tag: str, github_repo: str) -> dict:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    for model in data["models"]:
        filename = FILENAME_MAP[model["id"]]
        model["download_url"] = release_download_url(tag, github_repo, filename)

    data["updated_at"] = (
        __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    CATALOG_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def main() -> None:
    ensure_release_dir()

    github_repo = os.environ.get("GITHUB_REPOSITORY", f"Tejas-ma/{REPO_NAME}")
    tag = os.environ.get("RELEASE_TAG", "models-v0.1")

    htdemucs_path = export_htdemucs(RELEASE_DIR)
    verify_htdemucs_onnx(htdemucs_path)

    deepfilter_path = download_deepfilter_net(RELEASE_DIR)

    catalog = rewrite_catalog(tag, github_repo)

    for model in catalog["models"]:
        path = RELEASE_DIR / FILENAME_MAP[model["id"]]
        model["size_bytes"] = file_size_bytes(path)
        model["sha256"] = sha256_hex(path)

    CATALOG_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    print("Prepared release assets and updated models/catalog.json")
    for model in catalog["models"]:
        print(
            f"  {model['id']}: {model['size_bytes']} bytes, sha256={model['sha256']}"
        )


if __name__ == "__main__":
    main()
