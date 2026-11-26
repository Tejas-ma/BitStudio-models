# Contributing to the BitStudio Audio Models Hub

This guide walks through exporting an ONNX audio model, verifying it, hashing it, and submitting it via Pull Request.

## Prerequisites

- Python 3.11
- A working ONNX Runtime installation for verification
- Write access to this repository (fork + PR for external contributors)

## Step 1 — Export the model to ONNX

Place export code under `tools/` or a dedicated export script, and write the resulting `.onnx` into `release_assets/`.

For HTDemucs v4, the hub uses `demucs_onnx.export.export_to_onnx("htdemucs", target)` and the existing automation script `tools/prepare_models.py` already performs this export. If you are adding a different model, write an equivalent export that produces a valid ONNX file in `release_assets/`.

## Step 2 — Verify the exported ONNX

Before packaging, run a real inference probe with ONNX Runtime:

1. Load the model with `onnxruntime.InferenceSession(path, providers=["CPUExecutionProvider"])`.
2. Build a dummy `float32` input matching the model's documented input shape.
3. Run inference and assert:
   - The output shape matches the documented output shape.
   - `np.isfinite(output).all()` is true (no NaNs/Infs).
4. For DeepFilterNet 3, verify against the 48 kHz mono / 480-sample frame contract.
5. For HTDemucs v4, verify the `[1,2,343980] → [1,4,2,343980]` contract with stems in the documented order.

If the probe fails, do not package the model. Fix the export first.

## Step 3 — Hash and record size

Compute the exact artifacts for the final released file:

- **size_bytes:** `os.path.getsize(path)`
- **sha256:** lowercase hex SHA-256 of the exact file bytes, 64 characters

Update `models/catalog.json`:

- Set `size_bytes` to the computed value.
- Set `sha256` to the computed hex digest (replace the `<AUTO_FILLED_BY_SCRIPT>` sentinel).

## Step 4 — Validate the catalog locally

Before opening a PR, run the catalog validation:

```bash
python - <<'EOF'
import json, re, sys
from pathlib import Path
catalog = json.loads(Path("models/catalog.json").read_text(encoding="utf-8"))
assert isinstance(catalog.get("schema_version"), int)
models = catalog["models"]
assert isinstance(models, list) and len(models) > 0
required = {"id","name","category","version","license","size_bytes","sha256","download_url","audio_spec"}
blocked = ("nc","non-commercial","noncommercial","gpl","agpl")
seen = set()
sha_re = re.compile(r"^[a-f0-9]{64}$")
for m in models:
    missing = required - set(m.keys())
    assert not missing, f"{m.get('id')} missing: {missing}"
    mid = m["id"]
    assert mid not in seen, f"Duplicate id: {mid}"
    seen.add(mid)
    tokens = re.split(r"[\s/\-,]+", m["license"].lower())
    for bad in blocked:
        assert bad not in tokens, f"Disallowed license '{m['license']}' on {mid}"
    assert m["download_url"].startswith("https://"), f"Non-HTTPS url on {mid}"
    sha = m["sha256"]
    if sha != "<AUTO_FILLED_BY_SCRIPT>":
        assert sha_re.match(sha), f"Invalid sha256 on {mid}: {sha}"
        assert isinstance(m["size_bytes"], int) and m["size_bytes"] > 0, f"Invalid size_bytes on {mid}"
print(f"OK: {len(models)} models validated.")
EOF
```

## Step 5 — Package and submit

1. Run `tools/prepare_models.py` (or your own equivalent) to regenerate `release_assets/` and rewrite `models/catalog.json` with final `size_bytes` and `sha256`.
2. Commit the updated catalog and any new assets that belong in version control.
3. Open a Pull Request targeting `main`.
4. The `validate-catalog.yml` workflow will run automatically on the PR once `models/catalog.json` is touched.
5. Releases are created by the maintainer via `release-models.yml` (workflow dispatch).

## License checklist

Before submitting, confirm the model's license is one of:

- MIT
- Apache-2.0
- BSD-3-Clause

Do not submit models under `CC-BY-NC`, `GPL`, `AGPL`, or any non-commercial/copyleft terms. Mixed licenses are allowed only when every component is on the permitted list.
