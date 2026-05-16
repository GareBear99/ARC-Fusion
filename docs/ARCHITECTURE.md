# Architecture

ARC-Fusion has four layers:

1. **Media backend**: FFprobe/FFmpeg execution and planning.
2. **Binary memory**: chunked object store, SHA-256 hashes, Merkle roots, manifests.
3. **Receipt layer**: job receipts and optional Ed25519 signatures.
4. **ARC views**: StreamMemory timelines, SURE recipes, Language Module mirrors, LLMBuilder exports.

Canonical truth is binary-first. Human-readable JSON is a view that is itself packed as a binary object when it must persist.
