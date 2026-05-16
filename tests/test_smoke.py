from pathlib import Path
from arc_fusion.binary_store import BinaryStore
from arc_fusion.sure import make_sure_recipe


def test_pack_verify_restore(tmp_path):
    p = tmp_path / 'hello.txt'
    p.write_text('hello arc fusion', encoding='utf-8')
    store = BinaryStore(tmp_path / 'store')
    obj = store.pack_file(p)
    assert store.verify_manifest(obj.manifest_path)['ok'] is True
    restored = store.restore(obj.manifest_path, tmp_path / 'out.txt')
    assert restored['ok'] is True
    assert (tmp_path / 'out.txt').read_text(encoding='utf-8') == 'hello arc fusion'


def test_sure_recipe_hash_stable():
    a = make_sure_recipe('gen', '1337', {'x': 1})
    b = make_sure_recipe('gen', '1337', {'x': 1})
    assert a['recipe_hash'] == b['recipe_hash']
