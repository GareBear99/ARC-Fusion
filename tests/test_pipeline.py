from pathlib import Path
from arc_fusion.pipeline import sure_recipe

def test_sure_recipe(tmp_path):
    out = sure_recipe(tmp_path / "store", "voxel_gen", "seed-1337", {"fps": 30})
    assert out["recipe"]["generator_id"] == "voxel_gen"
    assert out["manifest"]["manifest_hash"].startswith("sha256:")
