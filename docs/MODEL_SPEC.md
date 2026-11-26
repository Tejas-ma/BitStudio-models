# Model Specification (MODEL_SPEC.md)

This document defines the exact tensor, audio, verification, and licensing contracts that every model in this hub must satisfy.

## Tensor & Audio Contracts

### DeepFilterNet 3 — Real-time Denoising

- **Sample rate:** 48000 Hz
- **Channels:** 1 (mono)
- **Frame samples:** 480 (10 ms frames at 48 kHz)
- **Hop:** 480 samples (frame-level, real-time streaming)
- **Realtime capable:** yes
- **Runtime contract:** the model is intended for streaming/frame-by-frame inference on mono 48 kHz audio using 480-sample frames. Consumers must feed contiguous 480-sample frames; there is no fixed-length segment window.

### HTDemucs v4 — 4-Stem Separation

- **Sample rate:** 44100 Hz
- **Channels:** 2 (stereo)
- **Segment samples:** 343980 (exactly 7.8 seconds at 44.1 kHz)
- **Realtime capable:** no
- **Input tensor:**
  - name: `mix`
  - shape: `[1, 2, 343980]`
  - dtype: `float32`
- **Output tensor:**
  - name: `stems`
  - shape: `[1, 4, 2, 343980]`
  - dtype: `float32`
- **Stem order (axis 1 of output):** `["drums", "bass", "other", "vocals"]`

The output tensor layout is `[batch, stem, channel, sample]` where `stem` is indexed by the stem order above. Consumers must remap stems by that order, not by positional assumptions from other implementations.

## SHA-256 Verification Rules

Every distributed artifact in `release_assets/` must be verifiable by its SHA-256 digest recorded in `models/catalog.json`.

1. Compute the SHA-256 digest of the exact released file bytes (lowercase hex, 64 characters).
2. Record the digest in the model's `sha256` field.
3. Record the exact byte size in the model's `size_bytes` field.
4. Any consumer verifying a download must compute `sha256(file_bytes)` and compare it to the catalog value, and must also confirm `len(file_bytes) == size_bytes`.
5. Until a release workflow populates a value, `sha256` may be the sentinel `"<AUTO_FILLED_BY_SCRIPT>"` and `size_bytes` may be `0`. Those sentinel values are not valid for a released artifact and the validation workflow rejects them.

## Commercially Safe License Requirements

Only the following licenses are permitted for model weights and packages in this hub:

- **MIT**
- **Apache-2.0**
- **BSD-3-Clause**

The following are explicitly **not** permitted:

- Any non-commercial / NC license, including `CC-BY-NC` and derivatives.
- Any copyleft weight license, including `GPL` and `AGPL` (and any variant spelling).

The catalog validation workflow enforces these rules automatically by rejecting any model whose `license` field contains the blocked terms. Mixed/compound licenses (for example `MIT / Apache-2.0`) are allowed only when every component is on the permitted list.
