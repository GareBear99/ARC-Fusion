from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List


def has_binary(name: str) -> bool:
    return shutil.which(name) is not None


def ffmpeg_versions() -> Dict[str, Any]:
    out = {}
    for bin_name in ['ffmpeg', 'ffprobe']:
        if not has_binary(bin_name):
            out[bin_name] = {'available': False}
            continue
        p = subprocess.run([bin_name, '-version'], capture_output=True, text=True, timeout=15)
        first = (p.stdout or p.stderr).splitlines()[0] if (p.stdout or p.stderr) else ''
        out[bin_name] = {'available': p.returncode == 0, 'version_line': first}
    return out


def probe(input_path: Path) -> Dict[str, Any]:
    if not has_binary('ffprobe'):
        return {'ok': False, 'error': 'ffprobe not found', 'input_path': str(input_path)}
    cmd = ['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', str(input_path)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        return {'ok': False, 'error': p.stderr, 'cmd': cmd}
    data = json.loads(p.stdout or '{}')
    data['ok'] = True
    data['cmd'] = cmd
    return data


def extract_frames(input_path: Path, out_dir: Path, fps: float = 1.0) -> Dict[str, Any]:
    if not has_binary('ffmpeg'):
        return {'ok': False, 'error': 'ffmpeg not found'}
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / 'frame_%06d.png'
    cmd = ['ffmpeg', '-y', '-i', str(input_path), '-vf', f'fps={fps}', str(pattern)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    frames = sorted(out_dir.glob('frame_*.png'))
    return {'ok': p.returncode == 0, 'cmd': cmd, 'stderr_tail': p.stderr[-4000:], 'frames': [str(x) for x in frames]}


def extract_audio_preview(input_path: Path, out_wav: Path) -> Dict[str, Any]:
    if not has_binary('ffmpeg'):
        return {'ok': False, 'error': 'ffmpeg not found'}
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-y', '-i', str(input_path), '-vn', '-ac', '2', '-ar', '48000', str(out_wav)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return {'ok': p.returncode == 0 and out_wav.exists(), 'cmd': cmd, 'stderr_tail': p.stderr[-4000:], 'audio_path': str(out_wav) if out_wav.exists() else None}
