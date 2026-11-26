# BitStudio Audio Models Hub

A curated hub of ONNX-packaged audio models for real-time enhancement and music source separation, with automated export, verification, hashing, and release packaging.

| Model | Task | Spec | License |
| --- | --- | --- | --- |
| [DeepFilterNet 3](docs/MODEL_SPEC.md#deepfilternet-3) | Real-time 48 kHz denoising | 48 kHz mono, 480-sample hop frames, real-time capable | MIT / Apache-2.0 |
| [HTDemucs v4](docs/MODEL_SPEC.md#htdemucs-v4) | 4-stem separation | 44.1 kHz stereo, `[1,2,343980] → [1,4,2,343980]`, stems `["drums","bass","other","vocals"]` | MIT |

## Windows Execution Providers

Both models run on Windows with ONNX Runtime execution providers:

- **CPUExecutionProvider** — CPU-only fallback, works everywhere.
- **DmlExecutionProvider** — DirectML GPU acceleration on Windows, recommended for real-time use.
- **CUDAExecutionProvider** — NVIDIA GPU acceleration (HTDemucs v4 only).

See [docs/MODEL_SPEC.md](docs/MODEL_SPEC.md) for exact tensor and audio contracts, SHA-256 verification rules, and the commercially safe license requirements enforced by the catalog.

## Repository Structure

- `models/catalog.json` — machine-readable model catalog (schema version 1).
- `tools/prepare_models.py` — export, verify, hash, and write back `models/catalog.json`.
- `.github/workflows/release-models.yml` — automated ONNX packaging, release creation, and catalog commit.
- `.github/workflows/validate-catalog.yml` — catalog schema, license, and SHA-256 validation on every push/PR.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the step-by-step export → verify → hash → PR workflow.
