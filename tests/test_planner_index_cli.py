from pathlib import Path
import json
from arc_fusion.planner import make_transcode_plan, codec_boundary_manifest, write_plan
from arc_fusion.index import summarize_index
from arc_fusion.cli import main
from arc_fusion.store import pack_file, write_receipt


def test_make_transcode_plan_is_hash_addressed(tmp_path):
    plan = make_transcode_plan(tmp_path / "in.mov", tmp_path / "out.mp4", crf=20)
    assert plan["schema"] == "arc-fusion.command-plan.v1"
    assert plan["operation"] == "transcode"
    assert plan["plan_hash"].startswith("sha256:")
    assert "ffmpeg" == plan["ffmpeg_args"][0]


def test_codec_boundary_manifest_has_non_goals():
    m = codec_boundary_manifest()
    assert m["schema"] == "arc-fusion.codec-boundary.v1"
    assert "full H.264 encoder" in m["non_goals_now"]


def test_index_records_manifest_and_receipt(tmp_path):
    store = tmp_path / "store"
    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    pack_file(f, store)
    write_receipt(store, "test", {"ok": True})
    summary = summarize_index(store)
    assert summary["counts"]["manifests"] >= 1
    assert summary["counts"]["receipts"] >= 1


def test_cli_smoke(tmp_path, capsys):
    main(["--store", str(tmp_path / "store"), "smoke"])
    out = capsys.readouterr().out
    obj = json.loads(out)
    assert obj["ok"] is True
