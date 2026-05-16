# ARC-Core Integration

ARC-Core is the authority layer. It should not store media bytes.

Use:

- `integrations/arc_core/routes_arc_fusion.py`
- `integrations/arc_core/migrations/003_arc_fusion_payloads.sql`

The route records:

```json
{
  "source_system": "arc-fusion",
  "payload_hash": "sha256:...",
  "manifest_hash": "sha256:...",
  "merkle_root": "sha256:...",
  "receipt_hash": "sha256:...",
  "label": "video.mp4",
  "mime_type": "video/mp4",
  "size_bytes": 123
}
```

Required invariants:

1. ARC-Core never stores the raw bytes.
2. Receipt hashes are immutable.
3. Payload registration is idempotent.
4. Source systems are policy-gated.
5. Signed receipts become mandatory for privileged lanes.
