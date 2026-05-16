from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any
from .hash_utils import sha256_bytes


def canonical_hash(obj: Dict[str, Any]) -> str:
    tmp = dict(obj)
    tmp.pop('receipt_hash', None)
    raw = json.dumps(tmp, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return sha256_bytes(raw)


def make_receipt(event_type: str, status: str, data: Dict[str, Any]) -> Dict[str, Any]:
    receipt = {
        'schema': 'arc-fusion.receipt.v1',
        'event_type': event_type,
        'status': status,
        'created_unix': int(time.time()),
        'data': data,
    }
    receipt['receipt_hash'] = canonical_hash(receipt)
    return receipt


def write_receipt(receipt: Dict[str, Any], receipts_dir: Path) -> Path:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    p = receipts_dir / f'{receipt["receipt_hash"]}.receipt.json'
    p.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding='utf-8')
    return p
