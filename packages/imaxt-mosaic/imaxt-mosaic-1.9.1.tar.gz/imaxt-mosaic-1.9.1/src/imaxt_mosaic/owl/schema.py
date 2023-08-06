from pathlib import Path

import voluptuous as vo

DEFAULT_RECIPES = ["calibration", "mosaic", "mosaic_preview", "bead_find"]
STITCHER_NAMES = ["stpt", "axio"]


def check_recipes(val):
    if len(val) == 1 and val[0] == "all":
        val = DEFAULT_RECIPES
    for item in val:
        if item not in DEFAULT_RECIPES:
            raise vo.Invalid(f"Not a valid recipe {item!r}")
    return val


def check_stitcher(val: str):
    val = val.lower()
    if val not in STITCHER_NAMES:
        raise vo.Invalid(f"Not a valid stitcher {val!r}")
    return val


schema = vo.Schema(
    {
        vo.Required("input_path"): vo.Coerce(Path),
        vo.Required("output_path"): vo.Coerce(Path),
        vo.Optional("overwrite", default=False): vo.Coerce(bool),
        vo.Required("recipes"): vo.All(list, check_recipes),
        vo.Required("stitcher"): vo.All(str, check_stitcher),
        vo.Optional("config", default={}): dict,
    }
)
