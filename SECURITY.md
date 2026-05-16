# Security

ARC-Fusion uses SHA-256 hashes, Merkle roots, and optional Ed25519 receipt signing.

## Current security boundary

- Hashes detect mutation.
- Merkle roots summarize chunk sets.
- Signatures verify receipt authorship.
- Raw media bytes are not stored in ARC-Core.

## Not yet complete

- AES-GCM payload encryption is planned for v0.4.
- Remote trust federation is not implemented.
- Do not treat unsigned receipts as privileged authority.
