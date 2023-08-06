import dask
import dask.array as da
import numpy as np
import xarray as xr
from dask import delayed
from imaxt_mosaic.raw import GenericSection, GenericStitcher
from imaxt_mosaic.settings import Settings
from owl_dev.logging import logger
from shapely.geometry import Polygon

from ..stagepos import StagePos
from ..utils import cancel_futures, get_workers_address, persist_array
from . import register_stitcher

__config = {
    "bscale": 1,
    "bzero": 0,
    "sections": None,
    "channel_to_use": 3,
    "norm_val": 1,
}

_SettingsPlugin__config = __config

USE_MULTIPLE_WORKERS = True


def get_mosaic_bounding_box(ds):
    bby, bbx = 0, 0
    for section in ds:
        _, _, tbby, tbbx = ds[section].attrs["mosaic_boundingbox"]
        if tbby > bby:
            bby = tbby
        if tbbx > bbx:
            bbx = tbbx
    return [0, 0, bby, bbx]


def imageproc(image, flat):
    return image.astype("float32") / Settings.norm_val / flat.clip(1e-6, 1e6)


class Section(GenericSection):
    @property
    def stagepos(self):

        mosaic_positions = np.array(self._section.attrs["mosaic_positions"])
        _, _, bbh, bbw = self._section.attrs["mosaic_boundingbox"]

        dx = mosaic_positions[:, 1]
        t_x = dx[1:] - dx[:-1]

        dy = mosaic_positions[:, 0]
        t_y = dy[1:] - dy[:-1]

        delta_x = np.percentile(t_x, 96)
        delta_y = np.percentile(t_y, 96)

        ncols, nrows = int(bbw / delta_y), int(bbh / delta_x)

        row_pos = np.arange(nrows) * delta_y
        col_pos = np.arange(ncols) * delta_x

        stage = []
        for pos in mosaic_positions:
            y, x, h, w = pos
            p = Polygon.from_bounds(x, y, x + w, y + h)
            col = col_pos.searchsorted(p.centroid.x) - 1
            row = row_pos.searchsorted(p.centroid.y) - 1
            stage.append([col, row, y, x])

        stage = np.array(stage)

        return StagePos(stage[:, 1], stage[:, 0], stage[:, 2:])

    @property
    def stage_size(self):
        _, _, y, x = self._section.attrs["mosaic_boundingbox"]
        return int((y // 4096 + 0) * 4096), int((x // 4096 + 0) * 4096)

    @property
    def ntiles(self) -> int:
        """Number of tiles"""
        return len(self._section.attrs["mosaic_positions"])

    def calculate_offsets(self, images):
        grid = self.stagepos.grid.copy()

        grid["y_pos"] = grid["y_pos_init_guess"]
        grid["x_pos"] = grid["x_pos_init_guess"]
        grid["y_pos2"] = grid["y_pos"] - grid["y_pos"].min()
        grid["x_pos2"] = grid["x_pos"] - grid["x_pos"].min()
        return grid

    def calibrate(self, z, cals, persist=False):
        stack = []
        for ch in self.channels:
            images = self.sel(channel=ch, z=z).data
            _, ny, nx = images.shape
            flat = cals["flats"].sel(channel=ch).data if cals else 1
            proc = [delayed(imageproc)(im, flat) for im in images]
            proc = [da.from_delayed(im, shape=(ny, nx), dtype="float32") for im in proc]
            stack.append(da.stack(proc))
        stack = da.stack(stack).rechunk((len(self.channels), 1, ny, nx))
        # self.bscale_from_flats(cals["flats"])
        if persist:
            stack = persist_array(stack, workers=self.workers)
        return stack

    @property
    def metadata(self):
        raw_meta = self._section.attrs["Metadata"]
        return {
            "raw_meta": raw_meta,
            "scale": self._section.attrs.get("scale", ""),
            "bscale": Settings.bscale,
            "bzero": Settings.bzero,
        }


@register_stitcher("axio")
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
            # Get the bounding box from all slices
            mosaic_boundingbox = get_mosaic_bounding_box(ds)
            section._section.attrs["mosaic_boundingbox"] = mosaic_boundingbox

            z = 0
            cals = xr.open_zarr(output_path / "cals")
            images = section.calibrate(z, cals, persist=True)
            logger.debug("Read %s tile images", images.shape[1])

            logger.debug("Calculating offsets")
            grid = section.calculate_offsets(images[Settings.channel_to_use])

            logger.debug("Starting stitch")
            # conf = section.getconf(cals, persist=True)
            section.stitch(images, z, grid, output_path / "mos", conf=None)
            logger.debug("Stitching done")

            cancel_futures([images])
            del images

            # Write registration table
            logger.debug("Writing registration table")
            (output_path / "registration").mkdir(exist_ok=True)
            grid["section"] = section_name
            grid.to_parquet(output_path / "registration" / f"{section_name}.parquet")

            logger.debug("Downsampling section %s", section_name)
            section.downsample(output_path / "mos")

            logger.debug("Creating preview for section %s", section_name)
            section.preview(output_path)

            del section._section, section, ds

        return section_name
