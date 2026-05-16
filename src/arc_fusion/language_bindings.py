from __future__ import annotations
from pathlib import Path
from .binary_store import BinaryStore

def mirror_language_path(store_root: str | Path, language_path: str | Path) -> dict:
    store = BinaryStore(Path(store_root))
    path = Path(language_path)
    manifests = []
    if path.is_file():
        manifests.append(store.pack_file(path, logical_name=f'language/{path.name}', media_type='application/octet-stream', source='arc-language-module'))
    else:
        for p in sorted(path.rglob('*')):
            if p.is_file() and not any(part.startswith('.git') for part in p.parts):
                rel = p.relative_to(path).as_posix()
                manifests.append(store.pack_file(p, logical_name=f'language/{rel}', source='arc-language-module'))
    return {'ok': True, 'count': len(manifests), 'manifest_hashes': [m['manifest_hash'] for m in manifests]}
