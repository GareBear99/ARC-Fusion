# ARC-Fusion

**ARC-Fusion** is an ARC-native, FFmpeg-backed, binary-first cryptographic media runtime.

It is the first practical step toward an ARC media engine: keep FFmpeg as the proven backend while adding deterministic command plans, binary object storage, Merkle manifests, signed receipts, StreamMemory timelines, SURE recipes, ARC Language Module hooks, and LLMBuilder lineage.

## Doctrine

```text
media/runtime information -> deterministic binary object -> hash -> Merkle root -> manifest -> receipt -> ARC authority reference
```

Human-readable JSON is a projection. The durable truth is the binary object plus cryptographic proof.

## What v0.4.0 can do

- Pack arbitrary files into ARC-compatible chunked binary manifests.
- Verify and restore binary payloads.
- Probe media with `ffprobe` when available.
- Ingest media through FFmpeg-backed frame/audio extraction.
- Generate StreamMemory timeline manifests and scene/keyframe index manifests.
- Generate deterministic command plans for FFmpeg-backed transcodes.
- Execute transcodes through the proof plane, with input, plan, output, execution log, and receipt.
- Generate and verify Ed25519-signed receipts.
- Mirror ARC Language Module files into binary storage.
- Export LLMBuilder lineage rows without inventing labels.
- Maintain a local SQLite index of manifests, receipts, and media jobs.
- Publish ARC-Core authority route/migration stubs.

## Install

```bash
python -m pip install -e .
```

## CLI

```bash
arc-fusion doctor
arc-fusion init-store --store .arc_fusion_store
arc-fusion pack ./video.mp4 --store .arc_fusion_store
arc-fusion verify .arc_fusion_store/manifests/<hash>.manifest.json --store .arc_fusion_store
arc-fusion restore .arc_fusion_store/manifests/<hash>.manifest.json ./restored.bin --store .arc_fusion_store
arc-fusion probe ./video.mp4 --store .arc_fusion_store
arc-fusion ingest ./video.mp4 --store .arc_fusion_store --fps 1 --frame-limit 12
arc-fusion plan-transcode ./input.mov ./output.mp4 --store .arc_fusion_store
arc-fusion transcode ./input.mov ./output.mp4 --store .arc_fusion_store
arc-fusion keygen --store .arc_fusion_store
arc-fusion sign-receipt .arc_fusion_store/receipts/<hash>.receipt.json .arc_fusion_store/keys/arc_fusion_ed25519_private.pem
arc-fusion verify-receipt .arc_fusion_store/receipts/<hash>.receipt.json .arc_fusion_store/keys/arc_fusion_ed25519_public.pem
arc-fusion index-summary --store .arc_fusion_store
arc-fusion codec-boundaries
```

## Honest boundary

ARC-Fusion is **not a full FFmpeg replacement yet**. It is a media memory, proof, and lineage runtime that uses FFmpeg as the backend. The long-term replacement path starts with stable adapter boundaries: WAV/PCM, image sequences, filtergraph planning, and selected deterministic transforms before any serious codec work.

## Public positioning

> ARC-Fusion is a binary-first cryptographic media runtime for ARC systems: FFmpeg-backed today, ARC-native over time, with verifiable media memory, deterministic receipts, StreamMemory timelines, seeded reconstruction recipes, and AI dataset lineage.
