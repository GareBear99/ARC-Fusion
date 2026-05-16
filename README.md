# ARC-Fusion

**ARC-Fusion** is an ARC-native, FFmpeg-backed media proof runtime.

It is not trying to replace FFmpeg on day one. It uses FFmpeg/FFprobe as proven backend tools while adding the layers FFmpeg does not provide by itself:

- binary-first media memory
- chunked object storage
- SHA-256 payload identity
- Merkle roots
- signed receipts
- StreamMemory timelines
- scene/keyframe indexes
- SURE seeded media recipes
- ARC Language Module mirroring
- LLMBuilder dataset lineage
- ARC-Core authority registration stubs

## Doctrine

```text
media information -> deterministic binary object -> hash -> Merkle root -> manifest -> receipt -> ARC authority reference
```

Human-readable JSON is a projection. The durable truth is the binary object plus cryptographic proof.

## Install

```bash
python -m pip install -e .
```

## CLI

```bash
arc-fusion doctor
arc-fusion init-store --store .arc_fusion_store
arc-fusion pack ./video.mp4 --store .arc_fusion_store
arc-fusion ingest ./video.mp4 --store .arc_fusion_store --fps 1 --frame-limit 12
arc-fusion keygen --store .arc_fusion_store
arc-fusion sign-receipt .arc_fusion_store/receipts/<hash>.receipt.json .arc_fusion_store/keys/arc_fusion_ed25519_private.pem
arc-fusion verify-receipt .arc_fusion_store/receipts/<hash>.receipt.json .arc_fusion_store/keys/arc_fusion_ed25519_public.pem
```

## Current capability

v0.3.0 can:

- pack arbitrary files into ARC-compatible binary manifests
- verify and restore binary payloads
- run ffprobe when available
- extract sampled frames and audio previews when FFmpeg is available
- generate StreamMemory timeline manifests
- generate scene/keyframe index manifests
- create and sign receipts
- mirror ARC Language Module files into binary storage
- emit LLMBuilder lineage placeholder rows without inventing labels
- provide ARC-Core route and SQLite migration stubs

## Honest boundary

ARC-Fusion is not a codec library yet. It is a media memory, proof, and lineage runtime that uses FFmpeg as the execution backend. The long-term path is to replace selected modules only after the proof plane, timeline model, and ARC authority integration are stable.
