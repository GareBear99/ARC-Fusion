# Architecture

ARC-Fusion sits between normal media files and the ARC ecosystem.

```text
media file
  -> FFprobe / FFmpeg planner
  -> extracted artifacts
  -> binary object store
  -> manifests + Merkle roots
  -> receipts
  -> ARC-Core authority registration
  -> StreamMemory / LLMBuilder / Proto-Synth views
```

## Core modules

- `store.py` — binary object packing, verification, restoration, receipts
- `crypto.py` — SHA-256, canonical JSON, Merkle roots, Ed25519 signing
- `ffmpeg_backend.py` — FFprobe/FFmpeg capability layer
- `pipeline.py` — probe, ingest, SURE recipe flows
- `cli.py` — public command surface

## Binary-first model

Every durable artifact gets converted into bytes and packed:

- original media
- ffprobe JSON
- extracted frames
- audio preview WAV
- sampled scene index
- StreamMemory timeline
- generated recipes
- LLMBuilder lineage records

ARC-Core should only store references, not heavy bytes.
