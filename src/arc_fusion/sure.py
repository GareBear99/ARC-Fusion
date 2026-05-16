from __future__ import annotations
import time
from .hash_utils import sha256_bytes, canonical_json_bytes

def make_sure_recipe(generator_id: str, seed: str, params: dict, expected_output_hash: str | None = None) -> dict:
    recipe = {
        'schema': 'arc-fusion.sure_media_recipe.v0.2',
        'generator_id': generator_id,
        'seed': str(seed),
        'params': params,
        'params_hash': sha256_bytes(canonical_json_bytes(params)),
        'expected_output_hash': expected_output_hash,
        'created_unix': int(time.time()),
    }
    recipe['recipe_hash'] = sha256_bytes(canonical_json_bytes(recipe))
    return recipe
