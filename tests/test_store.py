from pathlib import Path
from arc_fusion.store import pack_file, verify_manifest, restore_manifest, write_receipt
from arc_fusion.crypto import keygen, sign_json, verify_json
import json

def test_pack_verify_restore(tmp_path):
    store = tmp_path / "store"
    src = tmp_path / "hello.txt"
    src.write_text("hello arc fusion", encoding="utf-8")
    m = pack_file(src, store)
    assert verify_manifest(Path(m["manifest_path"]), store)["ok"]
    out = tmp_path / "out.txt"
    restore_manifest(Path(m["manifest_path"]), store, out)
    assert out.read_text(encoding="utf-8") == "hello arc fusion"

def test_receipt_sign_verify(tmp_path):
    store = tmp_path / "store"
    r = write_receipt(store, "test.event", {"a": 1})
    priv = tmp_path / "priv.pem"
    pub = tmp_path / "pub.pem"
    keygen(priv, pub)
    signed = sign_json(r, priv)
    assert verify_json(signed, pub)
