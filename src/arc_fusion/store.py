from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json, mimetypes, os, shutil, time
from .crypto import sha256_bytes, sha256_json, merkle_root, canonical_json_bytes

DEFAULT_CHUNK_SIZE = 1024 * 1024

def init_store(store: Path) -> Dict[str, str]:
    for sub in ["objects/sha256", "manifests", "receipts", "restored", "jobs", "keys", "indexes"]:
        (store / sub).mkdir(parents=True, exist_ok=True)
    return {"store": str(store), "status": "ok"}

def _chunk_path(store: Path, h: str) -> Path:
    return store / "objects" / "sha256" / h[:2] / h[2:4] / f"{h}.bin"

def pack_bytes(data: bytes, store: Path, label: str = "payload", mime: str = "application/octet-stream", chunk_size: int = DEFAULT_CHUNK_SIZE) -> Dict[str, Any]:
    init_store(store)
    chunk_hashes: List[str] = []
    size = len(data)
    for offset in range(0, size, chunk_size):
        chunk = data[offset:offset+chunk_size]
        h = sha256_bytes(chunk)
        cp = _chunk_path(store, h)
        cp.parent.mkdir(parents=True, exist_ok=True)
        if not cp.exists():
            cp.write_bytes(chunk)
        chunk_hashes.append(h)
    payload_hash = sha256_bytes(data)
    manifest = {
        "schema": "arc-fusion.binary-manifest.v1",
        "label": label,
        "mime_type": mime,
        "size_bytes": size,
        "payload_hash": "sha256:" + payload_hash,
        "chunk_size": chunk_size,
        "chunk_count": len(chunk_hashes),
        "chunk_hashes": ["sha256:" + h for h in chunk_hashes],
        "merkle_root": "sha256:" + merkle_root(chunk_hashes),
        "created_at_unix": int(time.time())
    }
    manifest["manifest_hash"] = "sha256:" + sha256_json({k:v for k,v in manifest.items() if k != "manifest_hash"})
    mp = store / "manifests" / f"{manifest['manifest_hash'].split(':')[1]}.manifest.json"
    mp.write_bytes(canonical_json_bytes(manifest))
    manifest["manifest_path"] = str(mp)
    return manifest

def pack_file(path: Path, store: Path, label: str | None = None, chunk_size: int = DEFAULT_CHUNK_SIZE) -> Dict[str, Any]:
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return pack_bytes(path.read_bytes(), store, label or path.name, mime, chunk_size)

def load_manifest(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def verify_manifest(manifest_path: Path, store: Path) -> Dict[str, Any]:
    m = load_manifest(manifest_path)
    chunks = []
    missing = []
    for item in m.get("chunk_hashes", []):
        h = item.split(":",1)[1]
        cp = _chunk_path(store, h)
        if not cp.exists():
            missing.append(h)
            continue
        data = cp.read_bytes()
        if sha256_bytes(data) != h:
            missing.append(h + ":mismatch")
        chunks.append(data)
    restored = b"".join(chunks)
    payload_ok = ("sha256:" + sha256_bytes(restored)) == m.get("payload_hash") if not missing else False
    merkle_ok = ("sha256:" + merkle_root([x.split(":",1)[1] for x in m.get("chunk_hashes", [])])) == m.get("merkle_root")
    return {"ok": bool(payload_ok and merkle_ok and not missing), "payload_ok": payload_ok, "merkle_ok": merkle_ok, "missing": missing}

def restore_manifest(manifest_path: Path, store: Path, output: Path) -> Dict[str, Any]:
    m = load_manifest(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as f:
        for item in m.get("chunk_hashes", []):
            h = item.split(":",1)[1]
            f.write(_chunk_path(store, h).read_bytes())
    return {"output": str(output), "sha256": "sha256:" + sha256_bytes(output.read_bytes())}

def write_receipt(store: Path, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    init_store(store)
    r = {
        "schema": "arc-fusion.receipt.v1",
        "event_type": event_type,
        "created_at_unix": int(time.time()),
        "payload": payload,
    }
    r["receipt_hash"] = "sha256:" + sha256_json(r)
    rp = store / "receipts" / f"{r['receipt_hash'].split(':')[1]}.receipt.json"
    rp.write_bytes(canonical_json_bytes(r))
    r["receipt_path"] = str(rp)
    return r
