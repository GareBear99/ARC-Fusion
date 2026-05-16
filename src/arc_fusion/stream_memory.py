from __future__ import annotations
import time
from typing import Any

def build_timeline(input_manifest: dict, probe_manifest: dict | None = None, frame_manifests: list[dict] | None = None, audio_manifest: dict | None = None) -> dict[str, Any]:
    frames = frame_manifests or []
    return {
        'schema': 'arc-fusion.stream_timeline.v0.2',
        'created_unix': int(time.time()),
        'source_payload_hash': input_manifest.get('payload_hash'),
        'source_manifest_hash': input_manifest.get('manifest_hash'),
        'probe_manifest_hash': (probe_manifest or {}).get('manifest_hash'),
        'audio_manifest_hash': (audio_manifest or {}).get('manifest_hash'),
        'frames': [
            {'index': i, 'payload_hash': f.get('payload_hash'), 'manifest_hash': f.get('manifest_hash'), 'logical_name': f.get('logical_name')}
            for i, f in enumerate(frames)
        ],
    }
