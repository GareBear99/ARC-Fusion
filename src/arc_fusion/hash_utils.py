from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, List

DEFAULT_CHUNK_SIZE = 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()


def merkle_root(hex_hashes: Iterable[str]) -> str:
    level: List[bytes] = [bytes.fromhex(h) for h in hex_hashes]
    if not level:
        return sha256_bytes(b'')
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(hashlib.sha256(level[i] + level[i+1]).digest())
        level = nxt
    return level[0].hex()
