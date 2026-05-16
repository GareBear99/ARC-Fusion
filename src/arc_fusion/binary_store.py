from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json, shutil, time
from .hash_utils import sha256_file, sha256_bytes, canonical_json_bytes, merkle_root_hex, CHUNK_SIZE_DEFAULT

@dataclass
class BinaryStore:
    root: Path
    chunk_size: int = CHUNK_SIZE_DEFAULT

    def __post_init__(self):
        self.root = Path(self.root)
        for name in ['objects/sha256', 'manifests', 'receipts', 'restored', 'indexes']:
            (self.root / name).mkdir(parents=True, exist_ok=True)

    def _chunk_path(self, chunk_hash: str) -> Path:
        return self.root / 'objects' / 'sha256' / chunk_hash[:2] / chunk_hash[2:4] / f'{chunk_hash}.bin'

    def write_bytes_as_object(self, data: bytes, logical_name: str, media_type: str = 'application/octet-stream', source: str = 'memory') -> dict[str, Any]:
        tmp = self.root / 'objects' / f'.tmp_{sha256_bytes(data)}'
        tmp.write_bytes(data)
        try:
            return self.pack_file(tmp, logical_name=logical_name, media_type=media_type, source=source)
        finally:
            tmp.unlink(missing_ok=True)

    def write_json_as_object(self, obj: Any, logical_name: str, source: str = 'canonical-json') -> dict[str, Any]:
        return self.write_bytes_as_object(canonical_json_bytes(obj), logical_name, 'application/json', source)

    def pack_file(self, path: str | Path, logical_name: str | None = None, media_type: str = 'application/octet-stream', source: str = 'file') -> dict[str, Any]:
        path = Path(path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(path)
        chunk_hashes = []
        size = path.stat().st_size
        with path.open('rb') as f:
            for idx, chunk in enumerate(iter(lambda: f.read(self.chunk_size), b'')):
                ch = sha256_bytes(chunk)
                chunk_hashes.append(ch)
                dst = self._chunk_path(ch)
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    dst.write_bytes(chunk)
        payload_hash = sha256_file(path, self.chunk_size)
        manifest = {
            'schema': 'arc-fusion.binary_manifest.v0.2',
            'logical_name': logical_name or path.name,
            'source': source,
            'media_type': media_type,
            'size_bytes': size,
            'chunk_size': self.chunk_size,
            'payload_hash': payload_hash,
            'chunk_hashes': chunk_hashes,
            'merkle_root': merkle_root_hex(chunk_hashes),
            'created_unix': int(time.time()),
        }
        manifest['manifest_hash'] = sha256_bytes(canonical_json_bytes(manifest))
        out = self.root / 'manifests' / f"{manifest['manifest_hash']}.manifest.json"
        out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding='utf-8')
        manifest['manifest_path'] = str(out)
        return manifest

    def load_manifest(self, manifest_path: str | Path) -> dict[str, Any]:
        return json.loads(Path(manifest_path).read_text(encoding='utf-8'))

    def verify_manifest(self, manifest: dict[str, Any]) -> dict[str, Any]:
        missing = []
        for ch in manifest.get('chunk_hashes', []):
            p = self._chunk_path(ch)
            if not p.exists() or sha256_file(p) != ch:
                missing.append(ch)
        merkle_ok = merkle_root_hex(manifest.get('chunk_hashes', [])) == manifest.get('merkle_root')
        payload_ok = False
        if not missing:
            restored = self.restore_manifest(manifest, self.root / 'restored' / f".verify_{manifest['payload_hash']}")
            payload_ok = sha256_file(restored) == manifest.get('payload_hash')
            Path(restored).unlink(missing_ok=True)
        return {'ok': not missing and merkle_ok and payload_ok, 'missing_chunks': missing, 'merkle_ok': merkle_ok, 'payload_ok': payload_ok}

    def restore_manifest(self, manifest: dict[str, Any], output_path: str | Path | None = None) -> str:
        output_path = Path(output_path or (self.root / 'restored' / manifest.get('logical_name', manifest['payload_hash'])))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('wb') as out:
            for ch in manifest.get('chunk_hashes', []):
                p = self._chunk_path(ch)
                if not p.exists():
                    raise FileNotFoundError(f'missing chunk {ch}')
                out.write(p.read_bytes())
        return str(output_path)
