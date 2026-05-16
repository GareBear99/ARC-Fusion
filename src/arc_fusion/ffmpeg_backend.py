from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import json, shutil, subprocess, tempfile

def has_tool(name: str) -> bool:
    return shutil.which(name) is not None

def ffprobe(path: Path) -> Dict[str, Any]:
    if not has_tool("ffprobe"):
        return {"ok": False, "available": False, "error": "ffprobe not found", "input": str(path)}
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {"ok": False, "available": True, "stderr": p.stderr, "input": str(path)}
    data = json.loads(p.stdout or "{}")
    data["ok"] = True
    data["available"] = True
    data["input"] = str(path)
    return data

def extract_frames(path: Path, out_dir: Path, fps: str = "1", limit: int = 12) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    if not has_tool("ffmpeg"):
        return {"ok": False, "available": False, "frames": [], "error": "ffmpeg not found"}
    pattern = out_dir / "frame_%06d.png"
    vf = f"fps={fps}"
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(path), "-vf", vf, "-frames:v", str(limit), str(pattern)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    frames = sorted(str(x) for x in out_dir.glob("frame_*.png"))
    return {"ok": p.returncode == 0, "available": True, "cmd": cmd, "stderr": p.stderr[-4000:], "frames": frames}

def extract_audio_preview(path: Path, out_path: Path, seconds: int = 30) -> Dict[str, Any]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not has_tool("ffmpeg"):
        return {"ok": False, "available": False, "output": None, "error": "ffmpeg not found"}
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(path), "-t", str(seconds), "-ac", "1", "-ar", "16000", str(out_path)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": p.returncode == 0 and out_path.exists(), "available": True, "cmd": cmd, "stderr": p.stderr[-4000:], "output": str(out_path) if out_path.exists() else None}

def scene_index_from_probe(probe: Dict[str, Any], frames: List[Dict[str, Any]]) -> Dict[str, Any]:
    duration = None
    try:
        duration = float(probe.get("format", {}).get("duration"))
    except Exception:
        duration = None
    return {
        "schema": "arc-fusion.scene-index.v1",
        "source": probe.get("input"),
        "duration_seconds": duration,
        "method": "sampled_keyframe_index_v0",
        "note": "This is a deterministic sampled frame index, not semantic scene understanding.",
        "items": [
            {"frame_index": i, "manifest_hash": f.get("manifest_hash"), "payload_hash": f.get("payload_hash"), "label": f.get("label")}
            for i, f in enumerate(frames)
        ],
    }


def tool_version(name: str) -> str | None:
    import subprocess
    if not has_tool(name):
        return None
    try:
        p = subprocess.run([name, "-version"], capture_output=True, text=True, timeout=10)
        first = (p.stdout or p.stderr).splitlines()[0] if (p.stdout or p.stderr) else ""
        return first.strip() or None
    except Exception:
        return None

def run_ffmpeg_plan(args: list[str]) -> dict:
    import subprocess, time
    if not args or args[0] != "ffmpeg":
        return {"ok": False, "error": "plan must start with ffmpeg"}
    if not has_tool("ffmpeg"):
        return {"ok": False, "available": False, "error": "ffmpeg not found"}
    started = int(time.time())
    p = subprocess.run(args, capture_output=True, text=True)
    return {"ok": p.returncode == 0, "available": True, "returncode": p.returncode, "started_at_unix": started, "completed_at_unix": int(time.time()), "stdout_tail": (p.stdout or "")[-4000:], "stderr_tail": (p.stderr or "")[-4000:]}
