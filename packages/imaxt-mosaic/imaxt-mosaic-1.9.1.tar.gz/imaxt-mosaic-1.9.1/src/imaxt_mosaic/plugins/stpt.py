import json

import dask
import numpy as np
import xarray as xr
from imaxt_mosaic.raw import GenericSection, GenericStitcher
from imaxt_mosaic.settings import Settings
from owl_dev.logging import logger

from ..stagepos import StagePos
from ..utils import cancel_futures, get_workers_address
from . import register_stitcher

__config = {
    "y_min": 0,
    "y_max": 2080,
    "x_min": 0,
    "x_max": 2080,
    "norm_val": 1,
    "channel_to_use": 3,
    "scale": 0.55,
    "cof_dist": {
        "cof_x": [
            -0.3978768594309433,
            22.021244273079315,
            4.969194161793347,
            1.489648554969356,
        ],
        "cof_y": [
            0.24781724665108668,
            -1.908123031173702,
            -3.1947393819597947,
            1.5466333490746447,
        ],
        "tan": [974.42215511, 1037.63451947],
    },
    "bscale": 1,
    "bzero": 0,
    "normal_x": 1000,
    "normal_y": 1000,
    "sections": None,
}

_SettingsPlugin__config = __config


USE_MULTIPLE_WORKERS = True


class Section(GenericSection):
    @property
    def stagepos(self, pos_corr=10):
        dx = np.array(self["XPos"]) / Settings.scale / pos_corr
        dy = np.array(self["YPos"]) / Settings.scale / pos_corr

        t_x = dx[1:] - dx[:-1]
        corners = np.where(t_x == 0)[0]
        t_y = dy[corners + 1] - dy[corners]

        delta_x = np.median(np.abs(t_x))
        delta_y = np.median(np.abs(t_y))

        dx0 = np.round((dx - dx.min()) / delta_x).astype(int)
        dy0 = np.round((dy - dy.min()) / delta_y).astype(int)

        rows = dx0.max() - dx0
        cols = dy0

        # x_init, y_init = dx[::-1] - dx.min(), dy - dy.min()
        # initial_guess = np.array([*zip(x_init.astype("int"), y_init.astype("int"))])

        overlap = (delta_x + delta_y) / 2
        initial_guess = np.array([*zip(rows * overlap, cols * overlap)])

        return StagePos(rows, cols, initial_guess)

    @property
    def stage_size(self):
        meta = self._section.attrs["raw_meta"][0]
        nrow, ncol = meta["mrows"], meta["mcolumns"]
        dy, dx = int((nrow - 1) * 2048), int((ncol - 1) * 2048)
        return int((dy // 4096) * 4096), int((dx // 4096) * 4096)

    @property
    def metadata(self):
        raw_meta = self._section.attrs["raw_meta"][0]
        thickness = raw_meta["sectionres"]
        scale = {"x": 0.56, "y": 0.56, "z": raw_meta["zres"]}
        return {
            "raw_meta": json.dumps(raw_meta),
            "scale": json.dumps(scale),
            "thickness": thickness,
            "bscale": Settings.bscale,
            "bzero": Settings.bzero,
            "norm_val": Settings.norm_val,
            "trimsec": [Settings.x_min, Settings.y_min, Settings.x_max, Settings.y_max],
        }


@register_stitcher("stpt")
class Stitcher(GenericStitcher):
    @staticmethod
    def run(input_path, section_name, worker, output_path, overwrite=False):
        if not overwrite and output_path.exists():
            if (output_path / f"preview/{section_name}.png").exists():
                logger.info("Section %s already exist, skipping", section_name)
                return section_name

        workers = [worker] if worker else get_workers_address()
        with dask.annotate(workers=workers):
            ds = xr.open_zarr(input_path)
            section = Section(ds[section_name])
            cals = xr.open_zarr(output_path / "cals")
            section.set_pars_from_cals(cals)
            conf = section.getconf(cals, persist=True)
            grid = None
            for z in ds.z.values:
                images = section.calibrate(z, cals, persist=True)
                if grid is None:
                    grid = section.calculate_offsets(images[Settings.channel_to_use])

                section.stitch(images, z, grid, output_path / "mos", conf=conf)
                logger.debug("Stitching done")

                cancel_futures([images])
                del images

            # Write registration table
            (output_path / "registration").mkdir(exist_ok=True)
            grid["section"] = section_name
            grid.to_parquet(output_path / "registration" / f"{section_name}.parquet")

            logger.debug("Downsampling section %s", section_name)
            section.downsample(output_path / "mos")

            logger.debug("Creating preview for section %s", section_name)
            section.preview(output_path)

            del section._section, section, ds

        return section_name
