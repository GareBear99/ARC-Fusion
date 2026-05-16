from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import json, shlex, time
from .crypto import sha256_json, canonical_json_bytes
from .store import pack_bytes, write_receipt, init_store

SUPPORTED_OPERATIONS = {
    "probe": "ffprobe metadata inspection",
    "ingest": "pack original, probe, frames, audio preview, timeline, receipt",
    "transcode": "FFmpeg-backed deterministic transcode plan",
    "extract-frames": "FFmpeg-backed deterministic frame extraction plan",
    "extract-audio": "FFmpeg-backed deterministic audio extraction plan",
}

@dataclass(frozen=True)
class CommandPlan:
    schema: str
    operation: str
    input_path: str
    output_path: Optional[str]
    ffmpeg_args: List[str]
    ffprobe_args: List[str]
    policy: Dict[str, Any]
    created_at_unix: int
    deterministic_notes: List[str]

    def canonical(self) -> Dict[str, Any]:
        return asdict(self)

    def plan_hash(self) -> str:
        return "sha256:" + sha256_json(self.canonical())


def make_transcode_plan(input_path: Path, output_path: Path, *, vcodec: str = "libx264", acodec: str = "aac", preset: str = "medium", crf: int = 18, extra_args: Optional[List[str]] = None) -> Dict[str, Any]:
    extra_args = extra_args or []
    ffmpeg_args = ["ffmpeg", "-hide_banner", "-y", "-i", str(input_path), "-c:v", vcodec, "-preset", preset, "-crf", str(crf), "-c:a", acodec, *extra_args, str(output_path)]
    plan = CommandPlan(
        schema="arc-fusion.command-plan.v1",
        operation="transcode",
        input_path=str(input_path),
        output_path=str(output_path),
        ffmpeg_args=ffmpeg_args,
        ffprobe_args=["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(input_path)],
        policy={"backend":"ffmpeg", "vcodec":vcodec, "acodec":acodec, "preset":preset, "crf":crf, "no_network": True},
        created_at_unix=int(time.time()),
        deterministic_notes=[
            "Plan is canonicalized and hash-addressed before execution.",
            "Exact byte output can still vary across FFmpeg versions/build flags; receipts must record backend version.",
            "ARC-Fusion treats FFmpeg as a backend until native modules replace specific stages."
        ],
    )
    obj = plan.canonical(); obj["plan_hash"] = plan.plan_hash(); return obj


def write_plan(store: Path, plan: Dict[str, Any]) -> Dict[str, Any]:
    init_store(store)
    manifest = pack_bytes(canonical_json_bytes(plan), store, label=f"{plan.get('operation','media')}.command_plan.json", mime="application/json")
    receipt = write_receipt(store, "arc_fusion.command.plan", {"operation": plan.get("operation"), "plan_hash": plan.get("plan_hash"), "plan_manifest_hash": manifest["manifest_hash"]})
    return {"plan": plan, "manifest": manifest, "receipt": receipt}


def codec_boundary_manifest() -> Dict[str, Any]:
    return {
        "schema":"arc-fusion.codec-boundary.v1",
        "position":"ARC-Fusion is FFmpeg-backed first; native codec work is introduced behind stable adapter boundaries.",
        "modules":[
            {"name":"container_demux", "status":"backend_adapter", "first_backend":"ffprobe/ffmpeg", "native_goal":"read selected lightweight containers after proof plane stabilizes"},
            {"name":"audio_pcm_wav", "status":"candidate_native_first", "native_goal":"PCM/WAV parser and writer for deterministic audio memory lanes"},
            {"name":"image_sequence", "status":"candidate_native_first", "native_goal":"PNG/JPEG sequence indexing and binary receipts"},
            {"name":"filtergraph", "status":"backend_adapter", "native_goal":"deterministic ARC filter DSL with FFmpeg export"},
            {"name":"transcode", "status":"ffmpeg_backend", "native_goal":"replace selected transforms only when test vectors and receipts prove equivalence"},
        ],
        "non_goals_now":["full H.264 encoder", "full HEVC encoder", "full muxer ecosystem", "hardware acceleration parity"],
    }
