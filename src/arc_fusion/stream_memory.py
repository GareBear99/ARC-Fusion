from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List


def build_timeline(input_manifest: Dict[str, Any], probe_manifest: Dict[str, Any], frame_objects: List[Dict[str, Any]], audio_object: Dict[str, Any] | None) -> Dict[str, Any]:
    return {
        'schema': 'arc-fusion.stream-timeline.v1',
        'source_payload_hash': input_manifest['payload_hash'],
        'probe_manifest_hash': probe_manifest.get('manifest_hash'),
        'frame_count': len(frame_objects),
        'frames': frame_objects,
        'audio': audio_object,
    }
