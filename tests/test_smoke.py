from pathlib import Path
import json
from arc_fusion.binary_store import BinaryStore
from arc_fusion.receipts import make_receipt
from arc_fusion.crypto_utils import keygen, sign_json, verify_signed_json
from arc_fusion.sure import make_sure_recipe
from arc_fusion.cli import main

def test_binary_store_roundtrip(tmp_path):
    p = tmp_path / 'sample.bin'
    p.write_bytes(b'abc' * 1024)
    store = BinaryStore(tmp_path / 'store', chunk_size=128)
    m = store.pack_file(p)
    assert store.verify_manifest(m)['ok'] is True
    out = store.restore_manifest(m, tmp_path / 'restored.bin')
    assert Path(out).read_bytes() == p.read_bytes()

def test_receipt_sign_verify(tmp_path):
    priv = tmp_path / 'priv.pem'; pub = tmp_path / 'pub.pem'
    keygen(priv, pub)
    r = make_receipt('test.event', {'x': 1})
    signed = sign_json(r, priv)
    assert verify_signed_json(signed, pub)['ok'] is True

def test_sure_recipe_stable():
    r = make_sure_recipe('gen', '1337', {'a': 1})
    assert r['schema'] == 'arc-fusion.sure_media_recipe.v0.2'
    assert r['params_hash']

def test_cli_smoke(tmp_path):
    assert main(['smoke', '--store', str(tmp_path / 'store')]) == 0
