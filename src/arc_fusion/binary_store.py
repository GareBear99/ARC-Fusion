from __future__ import annotations

import json
import mimetypes
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional

from .hash_utils import DEFAULT_CHUNK_SIZE, sha256_file, sha256_bytes, merkle_root


@dataclass
class PackedObject:
    payload_hash: str
    manifest_hash: str
    merkle_root: str
    manifest_path: Path
    size_bytes: int
    chunk_count: int


class BinaryStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.objects = self.root / 'objects' / 'sha256'
        self.manifests = self.root / 'manifests'
        self.receipts = self.root / 'receipts'
        self.jobs = self.root / 'jobs'
        self.tmp = self.root / 'tmp'

    def init(self) -> None:
        for p in [self.objects, self.manifests, self.receipts, self.jobs, self.tmp]:
            p.mkdir(parents=True, exist_ok=True)

    def _chunk_path(self, h: str) -> Path:
        return self.objects / h[:2] / h[2:4] / f'{h}.bin'

    def write_bytes_object(self, data: bytes, logical_name: str = 'memory.bin', content_type: str = 'application/octet-stream') -> PackedObject:
        self.init()
        h = sha256_bytes(data)
        cp = self._chunk_path(h)
        cp.parent.mkdir(parents=True, exist_ok=True)
        if not cp.exists():
            cp.write_bytes(data)
        manifest = {
            'schema': 'arc-fusion.binary-manifest.v1',
            'logical_name': logical_name,
            'content_type': content_type,
            'size_bytes': len(data),
            'payload_hash': h,
            'chunk_size': len(data) if data else 0,
            'chunks': [{'index': 0, 'sha256': h, 'size_bytes': len(data), 'object_path': str(cp.relative_to(self.root))}],
            'merkle_root': merkle_root([h]),
        }
        return self._write_manifest(manifest)

    def pack_file(self, path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE, logical_name: Optional[str] = None) -> PackedObject:
        self.init()
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        chunks: List[Dict[str, Any]] = []
        payload_hash = sha256_file(path, chunk_size)
        size = path.stat().st_size
        with path.open('rb') as f:
            idx = 0
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                h = sha256_bytes(data)
                cp = self._chunk_path(h)
                cp.parent.mkdir(parents=True, exist_ok=True)
                if not cp.exists():
                    cp.write_bytes(data)
                chunks.append({'index': idx, 'sha256': h, 'size_bytes': len(data), 'object_path': str(cp.relative_to(self.root))})
                idx += 1
        mroot = merkle_root([c['sha256'] for c in chunks])
        manifest = {
            'schema': 'arc-fusion.binary-manifest.v1',
            'logical_name': logical_name or path.name,
            'source_path_hint': str(path),
            'content_type': mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
            'size_bytes': size,
            'payload_hash': payload_hash,
            'chunk_size': chunk_size,
            'chunks': chunks,
            'merkle_root': mroot,
        }
        return self._write_manifest(manifest)

    def _write_manifest(self, manifest: Dict[str, Any]) -> PackedObject:
        raw = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode('utf-8')
        mh = sha256_bytes(raw)
        manifest['manifest_hash'] = mh
        raw = json.dumps(manifest, indent=2, sort_keys=True).encode('utf-8')
        mp = self.manifests / f'{mh}.manifest.json'
        mp.write_bytes(raw)
        return PackedObject(
            payload_hash=manifest['payload_hash'],
            manifest_hash=mh,
            merkle_root=manifest['merkle_root'],
            manifest_path=mp,
            size_bytes=manifest['size_bytes'],
            chunk_count=len(manifest['chunks']),
        )

    def verify_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
        chunk_hashes = []
        total = 0
        for c in manifest['chunks']:
            cp = self.root / c['object_path']
            if not cp.exists():
                return {'ok': False, 'error': f'missing chunk {c["sha256"]}'}
            actual = sha256_file(cp)
            if actual != c['sha256']:
                return {'ok': False, 'error': f'chunk mismatch {c["sha256"]} != {actual}'}
            total += cp.stat().st_size
            chunk_hashes.append(actual)
        if merkle_root(chunk_hashes) != manifest['merkle_root']:
            return {'ok': False, 'error': 'merkle root mismatch'}
        return {'ok': True, 'payload_hash': manifest['payload_hash'], 'manifest_hash': manifest.get('manifest_hash'), 'chunk_count': len(chunk_hashes), 'size_bytes': total}

    def restore(self, manifest_path: Path, out: Path) -> Dict[str, Any]:
        manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('wb') as w:
            for c in sorted(manifest['chunks'], key=lambda x: x['index']):
                w.write((self.root / c['object_path']).read_bytes())
        actual = sha256_file(out)
        return {'ok': actual == manifest['payload_hash'], 'restored_path': str(out), 'payload_hash': actual}
