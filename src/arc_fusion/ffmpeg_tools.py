from __future__ import annotations
from pathlib import Path
import json, shutil, subprocess, os

def which_ffmpeg() -> dict:
    return {'ffmpeg': shutil.which('ffmpeg'), 'ffprobe': shutil.which('ffprobe')}

def run_cmd(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, text=True, capture_output=True)
    return {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'cmd': cmd}

def probe_media(path: str | Path) -> dict:
    bins = which_ffmpeg()
    path = str(path)
    if not bins['ffprobe']:
        return {'ok': False, 'ffprobe_available': False, 'path': path, 'error': 'ffprobe not found'}
    cmd = [bins['ffprobe'], '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', path]
    res = run_cmd(cmd)
    if res['returncode'] != 0:
        return {'ok': False, 'ffprobe_available': True, 'path': path, 'error': res['stderr'], 'cmd': cmd}
    data = json.loads(res['stdout'] or '{}')
    data.update({'ok': True, 'ffprobe_available': True, 'path': path, 'cmd': cmd})
    return data

def plan_ingest(path: str | Path, fps: float = 1.0, extract_audio: bool = True) -> dict:
    path = str(path)
    return {
        'schema': 'arc-fusion.media_plan.v0.2',
        'input': path,
        'steps': [
            {'name': 'probe', 'tool': 'ffprobe', 'args': ['-show_format', '-show_streams']},
            {'name': 'extract_frames', 'tool': 'ffmpeg', 'fps': fps, 'pattern': 'frames/frame_%06d.jpg'},
        ] + ([{'name': 'extract_audio_preview', 'tool': 'ffmpeg', 'args': ['-vn', '-ac', '2', '-ar', '48000', 'audio_preview.wav']}] if extract_audio else [])
    }

def extract_frames(path: str | Path, out_dir: str | Path, fps: float = 1.0, limit: int | None = 12) -> dict:
    bins = which_ffmpeg(); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    if not bins['ffmpeg']:
        return {'ok': False, 'ffmpeg_available': False, 'frames': [], 'error': 'ffmpeg not found'}
    vf = f'fps={fps}' + (f',trim=end_frame={limit}' if limit else '')
    pattern = str(out_dir / 'frame_%06d.jpg')
    cmd = [bins['ffmpeg'], '-y', '-i', str(path), '-vf', vf, '-q:v', '2', pattern]
    res = run_cmd(cmd)
    frames = sorted(str(p) for p in out_dir.glob('frame_*.jpg'))
    return {'ok': res['returncode'] == 0, 'ffmpeg_available': True, 'frames': frames, 'cmd': cmd, 'stderr': res['stderr'][-2000:]}

def extract_audio_preview(path: str | Path, output: str | Path) -> dict:
    bins = which_ffmpeg(); output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    if not bins['ffmpeg']:
        return {'ok': False, 'ffmpeg_available': False, 'output': None, 'error': 'ffmpeg not found'}
    cmd = [bins['ffmpeg'], '-y', '-i', str(path), '-vn', '-ac', '2', '-ar', '48000', str(output)]
    res = run_cmd(cmd)
    return {'ok': res['returncode'] == 0 and output.exists(), 'ffmpeg_available': True, 'output': str(output) if output.exists() else None, 'cmd': cmd, 'stderr': res['stderr'][-2000:]}
