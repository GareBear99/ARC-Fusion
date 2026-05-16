from __future__ import annotations
import base64, json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from .hash_utils import canonical_json_bytes

def keygen(private_path: str | Path, public_path: str | Path) -> dict:
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    Path(private_path).write_bytes(priv.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    Path(public_path).write_bytes(pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    return {'private_key': str(private_path), 'public_key': str(public_path)}

def sign_json(obj: dict, private_path: str | Path) -> dict:
    priv = serialization.load_pem_private_key(Path(private_path).read_bytes(), password=None)
    if not isinstance(priv, Ed25519PrivateKey):
        raise ValueError('expected Ed25519 private key')
    unsigned = {k: v for k, v in obj.items() if k != 'signature'}
    sig = priv.sign(canonical_json_bytes(unsigned))
    out = dict(unsigned)
    out['signature'] = {'algorithm': 'ed25519', 'value_b64': base64.b64encode(sig).decode('ascii')}
    return out

def verify_signed_json(obj: dict, public_path: str | Path) -> dict:
    pub = serialization.load_pem_public_key(Path(public_path).read_bytes())
    if not isinstance(pub, Ed25519PublicKey):
        raise ValueError('expected Ed25519 public key')
    sig_obj = obj.get('signature') or {}
    sig = base64.b64decode(sig_obj.get('value_b64', ''))
    unsigned = {k: v for k, v in obj.items() if k != 'signature'}
    try:
        pub.verify(sig, canonical_json_bytes(unsigned))
        return {'ok': True, 'algorithm': 'ed25519'}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'algorithm': 'ed25519'}
