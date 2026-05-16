from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def export_llmbuilder_dataset(timeline: Dict[str, Any], out: Path) -> Dict[str, Any]:
    """Export placeholder lineage rows for future captions/OCR/transcripts.

    This intentionally does not invent labels. It creates source-backed rows ready for
    later annotation by OCR, captioning, transcription, or human review.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out.open('w', encoding='utf-8') as f:
        for frame in timeline.get('frames', []):
            row = {
                'schema': 'arc-fusion.llmbuilder-row.v1',
                'modality': 'video_frame',
                'source_payload_hash': timeline.get('source_payload_hash'),
                'frame_index': frame.get('index'),
                'frame_payload_hash': frame.get('payload_hash'),
                'annotation': None,
                'status': 'awaiting_annotation'
            }
            f.write(json.dumps(row, sort_keys=True) + '\n')
            count += 1
    return {'ok': True, 'rows': count, 'out': str(out)}
