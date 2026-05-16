# ARC-Fusion v0.4

I built ARC-Fusion as an ARC-native media proof runtime: FFmpeg-backed today, ARC-native over time.

It does not pretend to replace FFmpeg overnight. Instead, it adds the missing proof plane around media:

- binary-first media storage
- SHA-256 + Merkle manifests
- deterministic command plans
- signed receipts
- StreamMemory timelines
- SURE seeded reconstruction recipes
- ARC Language Module and LLMBuilder lineage hooks

v0.4 adds deterministic transcode planning, a proof-backed transcode command, a local SQLite index, and documented codec replacement boundaries.

The goal is not just to convert media. The goal is to make media provable, replayable, AI-readable, and safe to attach to long-term ARC memory.
