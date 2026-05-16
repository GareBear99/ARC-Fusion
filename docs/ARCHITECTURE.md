# ARC-Fusion Architecture v0.4

ARC-Fusion adds a proof and memory plane around media operations.

```text
Input media
  -> binary packer
  -> deterministic command plan
  -> FFmpeg/FFprobe backend
  -> artifact packer
  -> StreamMemory timeline
  -> receipt/signature
  -> ARC-Core authority registration
```

## Core layers

1. **Binary Store** — chunked payload storage with SHA-256, Merkle roots, manifests, and restore verification.
2. **Command Planner** — canonical FFmpeg command plans hashed before execution.
3. **Backend Adapter** — FFmpeg/FFprobe execution boundary. Current backend, not final identity.
4. **Media Pipeline** — probe, ingest, transcode, scene index, timeline.
5. **Index Plane** — SQLite index for local discovery of manifests, receipts, and jobs.
6. **Receipt Plane** — event receipts with optional Ed25519 signatures.
7. **ARC Integration Plane** — ARC-Core stubs, Language Module mirror, LLMBuilder lineage, SURE recipes.

## DARPA-grade coherence rule

No large media artifact is considered durable ARC truth until it has:

- a binary payload identity
- chunk hashes
- a Merkle root
- a manifest hash
- a receipt hash
- optional signature
- source lineage

## Why this is better than a plain FFmpeg wrapper

A plain wrapper runs a command. ARC-Fusion preserves the evidence trail:

```text
what was input
what plan was used
what backend version ran
what artifacts came out
what hashes prove them
what receipt authorizes them
what dataset/runtime record can cite them
```
