from __future__ import annotations
import json, time
from pathlib import Path
from .hash_utils import sha256_bytes, canonical_json_bytes

def make_receipt(event_type: str, payload: dict, status: str = 'ok') -> dict:
    r = {
        'schema': 'arc-fusion.receipt.v0.2',
        'event_type': event_type,
        'status': status,
        'created_unix': int(time.time()),
        'payload': payload,
    }
    r['receipt_hash'] = sha256_bytes(canonical_json_bytes(r))
    return r

def write_receipt(store_root: str | Path, receipt: dict) -> str:
    p = Path(store_root) / 'receipts' / f"{receipt['receipt_hash']}.receipt.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding='utf-8')
    return str(p)
