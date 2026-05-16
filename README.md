# ARC-Fusion

**ARC-Fusion** is a binary-first, cryptographic media runtime for ARC systems. It uses normal FFmpeg/FFprobe as the backend in the first implementation phase, then wraps every media operation in deterministic manifests, ARC-Apache-compatible binary payload storage, cryptographic receipts, StreamMemory timelines, SURE media recipes, Language Module bindings, and LLMBuilder lineage contracts.

> ARC-Fusion is not claiming to replace FFmpeg yet. It is an ARC-native media memory and transformation layer that makes FFmpeg-class work provable, replayable, and useful to AI/runtime memory systems.

## Core doctrine

```text
media input -> ffprobe/ffmpeg plan -> binary payloads -> manifests -> receipts -> ARC authority reference
```

Every durable artifact should be representable as binary truth:

- original video/audio/image files
- FFprobe metadata
- extracted keyframes
- extracted audio previews/stems
- stream timelines
- filter graph plans
- command logs
- generated visualization recipes
- dataset export rows

Human-readable JSON is a projection. The durable truth is the binary object plus its hashes, manifest, Merkle root, and receipt chain.

## What it does now

The repo contains a runnable Python CLI scaffold with these commands:

```bash
arc-fusion doctor
arc-fusion probe input.mp4 --store .arc_fusion_store
arc-fusion ingest input.mp4 --store .arc_fusion_store --fps 1 --audio --receipt
arc-fusion receipt --job path/to/job.json --store .arc_fusion_store
arc-fusion sure-recipe --generator voxel-waveform --seed 1337 --params examples/sure_params.json
arc-fusion export-llmbuilder --timeline path/to/timeline.json --out dataset.jsonl
arc-fusion smoke
```

If FFmpeg is installed, `ingest` can extract frames/audio. If not installed, the system still writes deterministic plans and safe failure receipts, so the repo remains testable.

## System role

ARC-Fusion is the media lane inside the broader ARC stack:

```text
ARC-Apache      binary payload store + cryptographic manifests
ARC-Core        authority receipts and event registration
StreamMemory    visual/time memory from frames and timelines
SURE            seeded reconstruction recipes for generated media states
Language Module captions, transcripts, OCR, lexical/media labels
LLMBuilder      verified dataset rows from media lineage
Proto-Synth     visual cognition shell for timelines, hashes, scenes, receipts
Arc-RAR         portable bundles for payloads, receipts, and restore plans
```

## Public positioning

This project is best described as:

> A cryptographic media cognition runtime: FFmpeg-compatible media processing with binary-first memory, deterministic receipts, StreamMemory extraction, and AI-ready lineage.

## Install for development

```bash
git clone https://github.com/GareBear99/ARC-Fusion.git
cd ARC-Fusion
python3 -m pip install -e .[dev]
arc-fusion smoke
```

FFmpeg/FFprobe are optional for basic smoke tests, but required for real media extraction.

## First real milestone

The first complete runtime milestone is:

```text
ingest -> probe -> extract keyframes/audio -> pack outputs -> write timeline -> write receipt -> verify stored payloads
```

This repo implements that structure in a clean, extensible way.

## Safety and honesty

ARC-Fusion does not contain custom codecs yet. It does not replace FFmpeg yet. It wraps FFmpeg-class execution with ARC-grade binary proof, provenance, replay, and memory extraction.
