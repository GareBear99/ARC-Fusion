from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any
from .hash_utils import sha256_bytes


def make_sure_recipe(generator_id: str, seed: str, params: Dict[str, Any], expected_output_hash: str | None = None) -> Dict[str, Any]:
    params_raw = json.dumps(params, sort_keys=True, separators=(',', ':')).encode('utf-8')
    recipe = {
        'schema': 'arc-fusion.sure-media-recipe.v1',
        'generator_id': generator_id,
        'seed': str(seed),
        'params_hash': sha256_bytes(params_raw),
        'params': params,
        'expected_output_hash': expected_output_hash,
        'doctrine': 'Store deterministic generation recipes when expanded bytes can be recreated and verified.'
    }
    recipe['recipe_hash'] = sha256_bytes(json.dumps(recipe, sort_keys=True, separators=(',', ':')).encode('utf-8'))
    return recipe
