import importlib
from pathlib import Path
from typing import List

import imaxt_mosaic.plugins
from distributed import WorkerPlugin, get_client
from imaxt_mosaic.settings import Settings
from owl_dev import pipeline
from owl_dev.logging import logger

from ..utils import update_config


class SettingsPlugin(WorkerPlugin):
    def __init__(self, stitcher, config):
        self.stitcher = stitcher
        self.config = config

    def setup(self, worker):

        func = imaxt_mosaic.plugins.get_plugin(self.stitcher)
        mod = importlib.import_module(func.__module__)
        this = mod.__config.copy()
        this.update(self.config)
        Settings.set_config(this)


@pipeline
def main(
    *,
    input_path: Path,
    output_path: Path,
    recipes: List[str],
    stitcher: str,
    overwrite: bool,
    config: dict,
):
    """
    Main entry point for the pipeline.
    """
    logger.info("Starting pipeline")

    client = get_client()
    client.register_worker_plugin(SettingsPlugin(stitcher, config))
    update_config(stitcher, config)

    if "calibration" in recipes:
        logger.info("Running calibration recipe")
        from ..calibration import compute_calibrations

        compute_calibrations(input_path, output_path, overwrite)

    if "mosaic" in recipes:
        logger.info("Running mosaic recipe")
        from ..stitchlib import imaxt_stitch

        imaxt_stitch(input_path, output_path, stitcher, overwrite)

    if "mosaic_preview" in recipes:
        logger.critical("Mosaic preview recipe not implemented")

    if "bead_find" in recipes:
        logger.critical("Bead finding recipe not implemented")

    logger.info("Finished pipeline")
