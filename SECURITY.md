# Security Policy

ARC-Fusion treats media, logs, and model artifacts as untrusted input. Do not execute payload contents. Verify manifests before using restored artifacts. Receipt signing proves the signer controlled the private key at signing time; it does not prove semantic correctness of the media.

## Current cryptography

- SHA-256 for payload and chunk identity
- Merkle root for chunk-set integrity
- Ed25519 for receipt signatures

Encryption is planned but should not be claimed until a reviewed AEAD implementation lands.
