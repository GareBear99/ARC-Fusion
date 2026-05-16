# ARC-Fusion

**ARC-Fusion** is an ARC-native, binary-first cryptographic media runtime. It uses FFmpeg/FFprobe as the backend media engine while adding deterministic binary storage, Merkle manifests, receipts, StreamMemory timelines, SURE seed recipes, language hooks, and LLMBuilder lineage exports.

> Honest status: ARC-Fusion is not a full FFmpeg replacement yet. It is the correct first production layer: a media cognition and proof runtime that can later replace selected FFmpeg subsystems with ARC-native modules.

## Why this exists

FFmpeg transforms media. ARC-Fusion transforms media **and proves what happened**. Every durable artifact can be stored as a binary object first, then referenced by cryptographic manifests and receipts.

```text
media input -> ffprobe/ffmpeg plan -> binary object store -> manifest -> receipt -> StreamMemory / ARC-Core / LLMBuilder
```

## Capabilities in v0.2

- FFprobe-backed media probe command
- FFmpeg-backed frame extraction and audio-preview extraction
- Binary object packing with chunk hashes, SHA-256 payload hashes, and Merkle roots
- Restore and verification commands
- Receipt creation for media jobs
- Ed25519 key generation, receipt signing, and receipt verification
- StreamMemory timeline generation
- SURE media recipe generation
- ARC Language Module mirroring into binary objects
- LLMBuilder JSONL export scaffold for verified media-derived dataset rows
- Public-facing docs, schemas, tests, and GitHub Actions smoke workflow

## Install locally

```bash
python3 -m pip install -e .
arc-fusion doctor
```

FFmpeg is optional for packaging, tests, and binary proof commands, but required for real media frame/audio extraction.

## Quickstart

```bash
arc-fusion init-store --store .arc_fusion_store
arc-fusion pack ./input.mp4 --store .arc_fusion_store --media-type video/mp4
arc-fusion verify .arc_fusion_store/manifests/<manifest>.manifest.json --store .arc_fusion_store
```

Media ingest:

```bash
arc-fusion ingest ./input.mp4 --store .arc_fusion_store --work .arc_fusion_work --fps 1 --frame-limit 12
```

Receipt signing:

```bash
arc-fusion keygen --private-key private.pem --public-key public.pem
arc-fusion sign-receipt .arc_fusion_store/receipts/<receipt>.receipt.json --private-key private.pem
arc-fusion verify-receipt .arc_fusion_store/receipts/<receipt>.receipt.json --public-key public.pem
```

## ARC ecosystem role

- **ARC-Apache**: binary memory substrate and receipt doctrine
- **ARC-Core**: authority registration layer
- **ARC-StreamMemory**: visual/time memory consumer
- **SURE**: deterministic seed-recipe reconstruction model
- **ARC Language Module**: lexical and metadata spine
- **ARC-Neuron LLMBuilder**: verified dataset/model lineage consumer
- **Proto-Synth Grid Engine**: future visual graph/shell

## Public positioning

ARC-Fusion should be described as an **FFmpeg-compatible ARC media runtime**, not as a completed FFmpeg clone. This protects credibility while making the ambition clear.
