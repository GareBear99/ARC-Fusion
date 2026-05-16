# ARC-Apache Integration

ARC-Fusion expects ARC-Apache to provide binary object storage and receipts. This repo includes a local compatible store for development.

## ARC-Core route target

```http
POST /arc-apache/payloads/register
POST /arc-fusion/media/receipts/register
GET  /arc-fusion/media/{receipt_hash}
```

## Registration payload

```json
{
  "source": "arc-fusion",
  "event_type": "arc_fusion.media.ingest",
  "input_payload_hash": "sha256...",
  "timeline_manifest_hash": "sha256...",
  "receipt_hash": "sha256...",
  "merkle_root": "sha256..."
}
```

ARC-Core remains authority. ARC-Fusion remains a media worker and memory producer.
