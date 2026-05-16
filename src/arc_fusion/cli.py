from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .store import init_store, pack_file, verify_manifest, restore_manifest, write_receipt, load_manifest
from .pipeline import probe_media, ingest_media, sure_recipe
from .crypto import keygen, sign_json, verify_json
from .ffmpeg_backend import has_tool

def emit(obj):
    print(json.dumps(obj, indent=2, sort_keys=True))

def main(argv=None):
    p = argparse.ArgumentParser(prog="arc-fusion", description="ARC-native binary-first FFmpeg-backed media proof runtime.")
    p.add_argument("--store", default=".arc_fusion_store", help="ARC-Fusion/ARC-Apache compatible store path")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor")
    sub.add_parser("init-store")
    sub.add_parser("smoke")

    sp = sub.add_parser("pack"); sp.add_argument("file")
    sp = sub.add_parser("verify"); sp.add_argument("manifest")
    sp = sub.add_parser("restore"); sp.add_argument("manifest"); sp.add_argument("output")
    sp = sub.add_parser("probe"); sp.add_argument("file")
    sp = sub.add_parser("ingest"); sp.add_argument("file"); sp.add_argument("--fps", default="1"); sp.add_argument("--frame-limit", type=int, default=12); sp.add_argument("--audio-seconds", type=int, default=30)
    sp = sub.add_parser("receipt"); sp.add_argument("event_type"); sp.add_argument("payload_json")
    sp = sub.add_parser("keygen"); sp.add_argument("--private", default=None); sp.add_argument("--public", default=None)
    sp = sub.add_parser("sign-receipt"); sp.add_argument("receipt"); sp.add_argument("private_key"); sp.add_argument("--out", default=None)
    sp = sub.add_parser("verify-receipt"); sp.add_argument("receipt"); sp.add_argument("public_key")
    sp = sub.add_parser("sure-recipe"); sp.add_argument("generator_id"); sp.add_argument("seed"); sp.add_argument("--params-json", default="{}"); sp.add_argument("--expected-output-hash", default=None)
    sp = sub.add_parser("mirror-language"); sp.add_argument("path")
    sp = sub.add_parser("export-llmbuilder"); sp.add_argument("timeline_manifest"); sp.add_argument("output_jsonl")
    sub.add_parser("arc-core-route-stub")

    a = p.parse_args(argv)
    store = Path(a.store)

    if a.cmd == "doctor":
        emit({"arc_fusion": "0.3.0", "ffmpeg": has_tool("ffmpeg"), "ffprobe": has_tool("ffprobe"), "store": str(store)})
    elif a.cmd == "init-store":
        emit(init_store(store))
    elif a.cmd == "pack":
        emit(pack_file(Path(a.file), store))
    elif a.cmd == "verify":
        emit(verify_manifest(Path(a.manifest), store))
    elif a.cmd == "restore":
        emit(restore_manifest(Path(a.manifest), store, Path(a.output)))
    elif a.cmd == "probe":
        emit(probe_media(Path(a.file), store))
    elif a.cmd == "ingest":
        emit(ingest_media(Path(a.file), store, fps=a.fps, frame_limit=a.frame_limit, audio_seconds=a.audio_seconds))
    elif a.cmd == "receipt":
        emit(write_receipt(store, a.event_type, json.loads(a.payload_json)))
    elif a.cmd == "keygen":
        init_store(store)
        priv = Path(a.private) if a.private else store / "keys" / "arc_fusion_ed25519_private.pem"
        pub = Path(a.public) if a.public else store / "keys" / "arc_fusion_ed25519_public.pem"
        emit(keygen(priv, pub))
    elif a.cmd == "sign-receipt":
        obj = json.loads(Path(a.receipt).read_text(encoding="utf-8"))
        signed = sign_json(obj, Path(a.private_key))
        out = Path(a.out) if a.out else Path(a.receipt)
        out.write_text(json.dumps(signed, indent=2, sort_keys=True), encoding="utf-8")
        emit({"ok": True, "signed_receipt": str(out)})
    elif a.cmd == "verify-receipt":
        obj = json.loads(Path(a.receipt).read_text(encoding="utf-8"))
        emit({"ok": verify_json(obj, Path(a.public_key))})
    elif a.cmd == "sure-recipe":
        emit(sure_recipe(store, a.generator_id, a.seed, json.loads(a.params_json), a.expected_output_hash))
    elif a.cmd == "mirror-language":
        target = Path(a.path)
        manifests = []
        if target.is_file():
            manifests.append(pack_file(target, store, label="language/" + target.name))
        else:
            for f in sorted(target.rglob("*")):
                if f.is_file():
                    manifests.append(pack_file(f, store, label="language/" + str(f.relative_to(target))))
        receipt = write_receipt(store, "arc_fusion.language.mirror", {"root": str(target), "manifest_count": len(manifests), "manifest_hashes": [m["manifest_hash"] for m in manifests]})
        emit({"manifests": manifests, "receipt": receipt})
    elif a.cmd == "export-llmbuilder":
        m = load_manifest(Path(a.timeline_manifest))
        row = {"schema": "arc-fusion.llmbuilder-export-row.v1", "timeline_manifest_hash": m.get("manifest_hash"), "source_label": m.get("label"), "annotation": None, "requires_human_or_model_labeling": True}
        Path(a.output_jsonl).write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
        emit({"ok": True, "output_jsonl": a.output_jsonl, "rows": 1})
    elif a.cmd == "arc-core-route-stub":
        emit({"route": "POST /arc-apache/payloads/register", "status": "stub", "see": "integrations/arc_core/routes_arc_fusion.py"})
    elif a.cmd == "smoke":
        init_store(store)
        payload = store / "smoke.txt"
        payload.write_text("arc-fusion smoke v0.3", encoding="utf-8")
        manifest = pack_file(payload, store)
        verify = verify_manifest(Path(manifest["manifest_path"]), store)
        receipt = write_receipt(store, "arc_fusion.smoke", {"manifest_hash": manifest["manifest_hash"]})
        emit({"ok": bool(verify["ok"] and receipt.get("receipt_hash")), "verify": verify, "receipt_hash": receipt.get("receipt_hash")})
    else:
        p.error("unknown command")


if __name__ == "__main__":
    main()
