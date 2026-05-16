from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Iterable, Any

CHUNK_SIZE_DEFAULT = 1024 * 1024

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: str | Path, chunk_size: int = CHUNK_SIZE_DEFAULT) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()

def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def merkle_root_hex(hashes: Iterable[str]) -> str:
    level = [bytes.fromhex(x) for x in hashes]
    if not level:
        return sha256_bytes(b'')
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(hashlib.sha256(left + right).digest())
        level = nxt
    return level[0].hex()
