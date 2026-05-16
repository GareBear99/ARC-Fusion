from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json, tempfile
from .store import init_store, pack_file, pack_bytes, write_receipt
from .crypto import canonical_json_bytes, sha256_json
from .ffmpeg_backend import ffprobe, extract_frames, extract_audio_preview, scene_index_from_probe

def probe_media(input_path: Path, store: Path) -> Dict[str, Any]:
    init_store(store)
    probe = ffprobe(input_path)
    manifest = pack_bytes(canonical_json_bytes(probe), store, label=input_path.name + ".ffprobe.json", mime="application/json")
    receipt = write_receipt(store, "arc_fusion.media.probe", {"input": str(input_path), "probe_manifest_hash": manifest["manifest_hash"], "probe_ok": probe.get("ok")})
    return {"probe": probe, "probe_manifest": manifest, "receipt": receipt}

def ingest_media(input_path: Path, store: Path, fps: str = "1", frame_limit: int = 12, audio_seconds: int = 30) -> Dict[str, Any]:
    init_store(store)
    input_manifest = pack_file(input_path, store, label=input_path.name)
    probe_result = ffprobe(input_path)
    probe_manifest = pack_bytes(canonical_json_bytes(probe_result), store, label=input_path.name + ".ffprobe.json", mime="application/json")
    job_dir = store / "jobs" / input_manifest["payload_hash"].split(":")[1][:16]
    frames_dir = job_dir / "frames"
    audio_path = job_dir / "audio_preview.wav"
    frame_result = extract_frames(input_path, frames_dir, fps=fps, limit=frame_limit)
    frame_manifests = []
    for fp in frame_result.get("frames", []):
        frame_manifests.append(pack_file(Path(fp), store, label=Path(fp).name))
    audio_result = extract_audio_preview(input_path, audio_path, seconds=audio_seconds)
    audio_manifest = None
    if audio_result.get("ok") and audio_result.get("output"):
        audio_manifest = pack_file(Path(audio_result["output"]), store, label="audio_preview.wav")
    scene_index = scene_index_from_probe(probe_result, frame_manifests)
    scene_manifest = pack_bytes(canonical_json_bytes(scene_index), store, label=input_path.name + ".scene_index.json", mime="application/json")
    timeline = {
        "schema": "arc-fusion.stream-timeline.v1",
        "source_input": str(input_path),
        "input_manifest_hash": input_manifest["manifest_hash"],
        "probe_manifest_hash": probe_manifest["manifest_hash"],
        "scene_index_manifest_hash": scene_manifest["manifest_hash"],
        "frame_manifest_hashes": [m["manifest_hash"] for m in frame_manifests],
        "audio_preview_manifest_hash": audio_manifest["manifest_hash"] if audio_manifest else None,
        "ffmpeg_frame_extraction": frame_result,
        "ffmpeg_audio_extraction": audio_result,
        "lineage_note": "All durable artifacts are binary-packed before authority receipt."
    }
    timeline_manifest = pack_bytes(canonical_json_bytes(timeline), store, label=input_path.name + ".stream_timeline.json", mime="application/json")
    receipt = write_receipt(store, "arc_fusion.media.ingest", {
        "input_payload_hash": input_manifest["payload_hash"],
        "input_manifest_hash": input_manifest["manifest_hash"],
        "probe_manifest_hash": probe_manifest["manifest_hash"],
        "timeline_manifest_hash": timeline_manifest["manifest_hash"],
        "scene_index_manifest_hash": scene_manifest["manifest_hash"],
        "frame_count": len(frame_manifests),
        "audio_preview": audio_manifest["manifest_hash"] if audio_manifest else None,
        "ffmpeg_available": frame_result.get("available") or audio_result.get("available"),
    })
    return {
        "input_manifest": input_manifest,
        "probe_manifest": probe_manifest,
        "frame_manifests": frame_manifests,
        "audio_manifest": audio_manifest,
        "scene_index_manifest": scene_manifest,
        "timeline_manifest": timeline_manifest,
        "receipt": receipt,
    }

def sure_recipe(store: Path, generator_id: str, seed: str, params: Dict[str, Any], expected_output_hash: str | None = None) -> Dict[str, Any]:
    recipe = {
        "schema": "arc-fusion.sure-media-recipe.v1",
        "generator_id": generator_id,
        "seed": seed,
        "params_hash": "sha256:" + sha256_json(params),
        "params": params,
        "expected_output_hash": expected_output_hash,
        "doctrine": "Store recipe plus expected hash when deterministic regeneration is cheaper than hot binary storage."
    }
    manifest = pack_bytes(canonical_json_bytes(recipe), store, label="sure_media_recipe.json", mime="application/json")
    receipt = write_receipt(store, "arc_fusion.sure.recipe", {"recipe_manifest_hash": manifest["manifest_hash"], "generator_id": generator_id})
    return {"recipe": recipe, "manifest": manifest, "receipt": receipt}
