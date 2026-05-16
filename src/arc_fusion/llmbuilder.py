from __future__ import annotations
import json
from pathlib import Path

def export_dataset_rows(timeline: dict, out_path: str | Path) -> dict:
    rows = []
    src = timeline.get('source_payload_hash')
    for frame in timeline.get('frames', []):
        rows.append({
            'source_payload_hash': src,
            'frame_payload_hash': frame.get('payload_hash'),
            'frame_manifest_hash': frame.get('manifest_hash'),
            'caption': '',
            'ocr_text': '',
            'transcript_segment': '',
            'review_status': 'unlabeled',
        })
    out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(json.dumps(r, sort_keys=True) for r in rows), encoding='utf-8')
    return {'ok': True, 'rows': len(rows), 'path': str(out_path)}
