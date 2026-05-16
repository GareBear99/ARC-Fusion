from __future__ import annotations
import json
from pathlib import Path

def make_arc_core_payload_registration(manifest: dict, receipt: dict | None = None, source: str = 'arc-fusion') -> dict:
    return {
        'event_type': 'arc_apache.payload.registered',
        'source': source,
        'payload_hash': manifest.get('payload_hash'),
        'manifest_hash': manifest.get('manifest_hash'),
        'merkle_root': manifest.get('merkle_root'),
        'size_bytes': manifest.get('size_bytes'),
        'receipt_hash': (receipt or {}).get('receipt_hash'),
    }
