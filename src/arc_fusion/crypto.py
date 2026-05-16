from __future__ import annotations
import base64, hashlib, json, os
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
except Exception:  # pragma: no cover
    Ed25519PrivateKey = None
    Ed25519PublicKey = None
    serialization = None

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_json(obj: Any) -> str:
    return sha256_bytes(canonical_json_bytes(obj))

def merkle_root(hex_hashes: List[str]) -> str:
    if not hex_hashes:
        return sha256_bytes(b"")
    level = [bytes.fromhex(h) for h in hex_hashes]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(hashlib.sha256(left + right).digest())
        level = nxt
    return level[0].hex()

def keygen(private_path: Path, public_path: Path) -> Dict[str, str]:
    if Ed25519PrivateKey is None:
        raise RuntimeError("cryptography is required for Ed25519 key generation")
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    public_path.write_bytes(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    return {"private_key": str(private_path), "public_key": str(public_path)}

def sign_json(obj: Dict[str, Any], private_key_path: Path) -> Dict[str, Any]:
    if Ed25519PrivateKey is None:
        raise RuntimeError("cryptography is required for Ed25519 signing")
    key = serialization.load_pem_private_key(private_key_path.read_bytes(), password=None)
    unsigned = dict(obj)
    unsigned.pop("signature", None)
    unsigned.pop("public_key", None)
    payload = canonical_json_bytes(unsigned)
    sig = key.sign(payload)
    signed = dict(unsigned)
    signed["signature"] = "ed25519:" + base64.b64encode(sig).decode("ascii")
    return signed

def verify_json(obj: Dict[str, Any], public_key_path: Path) -> bool:
    if Ed25519PublicKey is None:
        raise RuntimeError("cryptography is required for Ed25519 verification")
    sig_value = obj.get("signature", "")
    if not sig_value.startswith("ed25519:"):
        return False
    sig = base64.b64decode(sig_value.split(":", 1)[1])
    unsigned = dict(obj)
    unsigned.pop("signature", None)
    unsigned.pop("public_key", None)
    payload = canonical_json_bytes(unsigned)
    key = serialization.load_pem_public_key(public_key_path.read_bytes())
    try:
        key.verify(sig, payload)
        return True
    except Exception:
        return False
