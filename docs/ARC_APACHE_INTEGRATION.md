# ARC-Apache Integration

ARC-Core should register ARC-Fusion outputs as authority events using payload hash, manifest hash, Merkle root, and receipt hash.

Suggested event:

```json
{
  "event_type": "arc_apache.payload.registered",
  "source": "arc-fusion",
  "payload_hash": "...",
  "manifest_hash": "...",
  "merkle_root": "...",
  "receipt_hash": "..."
}
```

ARC-Core should not store massive media blobs. It should store authority references and policy decisions.
