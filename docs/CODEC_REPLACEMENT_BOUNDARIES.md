# Codec Replacement Boundaries

ARC-Fusion does not attempt full FFmpeg parity in early releases. That would be strategically wrong.

## Replacement order

1. **Proof plane first** — binary store, manifests, receipts, signatures.
2. **Plans second** — deterministic command and filtergraph plans.
3. **Native simple formats third** — WAV/PCM, image sequences, metadata envelopes.
4. **Filter primitives fourth** — selected deterministic operations with golden vectors.
5. **Codec replacement last** — only where ARC has test vectors, receipts, and clear reason.

## Initial native candidates

- PCM/WAV parser/writer
- image sequence indexer
- waveform summary encoder
- deterministic thumbnail grid generator
- ARC filtergraph DSL

## Explicit non-goals right now

- Full H.264 encoder replacement
- Full HEVC encoder replacement
- Hardware acceleration parity
- Every muxer/demuxer
- Network protocol parity

This makes the project credible: FFmpeg is respected while ARC-Fusion adds a new cryptographic memory layer that FFmpeg does not provide.
