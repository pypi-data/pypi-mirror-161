import contextlib
import itertools
import json
import math
import os
from datetime import datetime
from typing import Tuple

import cv2
import dask.array as da
import dask.config
import distributed
import imageio
import numpy as np
import pandas as pd
import xarray as xr
import zarr
from astropy.visualization import PercentileInterval
from owl_dev.logging import logger
from zarr.convenience import consolidate_metadata

import imaxt_mosaic

from .settings import Settings
from .stitcher import Stitcher
from .utils import (
    apply_geometric_transform,
    cancel_futures,
    compute,
    downsample,
    fuse,
    hsv_to_rgb,
    imageproc,
    persist_array,
)


class GenericSection:
    def __init__(self, section: xr.DataArray):
        self._section = section
        self.name = section.name
        try:
            workers = dask.config.config["annotations"]["workers"]
            self.workers = workers or None
        except KeyError:
            self.workers = None

    def __getitem__(self, attr):
        res = self._section.attrs["raw_meta"][0][attr]
        if isinstance(res, str):
            if res.isnumeric():
                res = int(res)
            else:
                with contextlib.suppress(ValueError):
                    res = float(res)
        return res

    def sel(self, **kwargs):
        return self._section.sel(**kwargs)

    @property
    def data(self):
        return self._section.data

    @property
    def tile_shape(self) -> Tuple[int, int]:
        """Tile shape"""
        dx = len(self._section.x)
        dy = len(self._section.y)
        return (dy, dx)

    @property
    def ntiles(self) -> int:
        """Number of tiles"""
        return len(self._section.tile)

    @property
    def nchannels(self) -> int:
        """Number of channels"""
        return len(self._section.channel)

    @property
    def channels(self):
        return list(self._section.channel.values)

    @property
    def nsections(self):
        """Number of optical sections"""
        return len(self._section.z)

    @property
    def metadata(self):
        return "{}"

    def normval(self, flats):
        pmax = max(p[1] for p in json.loads(flats.attrs["pval"]).values())
        scl = [1, 100, 1000, 10000, 100000]
        j = np.searchsorted(scl, pmax / (2**16 - 1), side="right")
        val = scl[j]
        logger.debug(f"Using norm_val={val}")
        return val

    def trimsec(self, flats):
        ff = flats.data.sum(axis=0).compute()
        ff = (ff - ff.min()) / (ff.max() - ff.min())
        ff = (ff * 255).astype("uint8")
        dy, dx = ff.shape
        _, thresh = cv2.threshold(ff, thresh=0, maxval=255, type=cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh.astype("uint8"), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        x, y, w, h = cv2.boundingRect(contours[0])
        y_min, y_max = max([10, y + 5]), min([dy - 10, y + h - 5])
        x_min, x_max = max([10, x + 5]), min([dx - 10, x + w - 5])
        logger.debug(f"Using trimsec={y_min}, {y_max}, {x_min}, {x_max}")
        return y_min, y_max, x_min, x_max

    def set_pars_from_cals(self, cals):
        # Compute from flats
        Settings.norm_val = self.normval(cals["flats"])
        y, yh, x, xw = self.trimsec(cals["flats"])
        Settings.y_min, Settings.y_max = y, yh
        Settings.x_min, Settings.x_max = x, xw

    def calibrate(self, z, cals, persist=False):
        """Calibrate section"""

        stack = []
        for ch in self.channels:
            if cals:
                flat = cals["flats"].sel(channel=ch).data
                dark = cals["darks"].sel(channel=ch).data
            else:
                flat = 1.0
                dark = 0.0

            data = self.sel(channel=ch, z=z).data
            images = da.stack([imageproc(im, flat=flat, dark=dark) for im in data])
            stack.append(images)
        stack = da.stack(stack)
        if persist:
            stack = persist_array(stack, self.workers)
        return stack

    def getconf(self, cals, persist=False):
        conf = []
        for ch in self.channels:
            flat = cals["flats"].sel(channel=ch).data
            this = da.where((flat < 0.3) | (flat > 5), 0, 1)
            this = apply_geometric_transform(
                this.astype("float32"), 1, 0, Settings.cof_dist
            )
            this = this[
                Settings.y_min : Settings.y_max, Settings.x_min : Settings.x_max
            ]
            this = da.where(this < 0.5, 0, 1)
            conf.append(this)
        res = da.stack(conf)
        if persist:
            res = persist_array(res, self.workers)
        return res

    def calculate_offsets(self, images):
        stitcher = Stitcher(images, self.stagepos)

        # Downsample step
        grid = stitcher.sp.grid.copy()
        for key in ["{}_pos_init_guess", "left_{}_init_guess", "top_{}_init_guess"]:
            for d in ["x", "y"]:
                grid[key.format(d)] = grid[key.format(d)] / 2

        images_downsampled = downsample(images)
        grid = stitcher.compute_first_pass(images_downsampled, grid)
        del images_downsampled

        # Upsample back the results
        for key in [
            "{}_pos_init_guess",
            "left_{}_init_guess",
            "top_{}_init_guess",
            "left_{}_first",
            "top_{}_first",
        ]:
            for d in ["x", "y"]:
                grid[key.format(d)] = grid[key.format(d)] * 2

        try:
            stitcher.filter_grid(images, grid)
        except Exception:
            grid = stitcher.sp.grid.copy()
            grid["left_ncc_first"] = 1
            grid["top_ncc_first"] = 1
            grid["left_x_first"] = grid["left_x_init_guess"]
            grid["left_y_first"] = grid["left_y_init_guess"]
            grid["top_x_first"] = grid["top_x_init_guess"]
            grid["top_y_first"] = grid["top_y_init_guess"]
            stitcher.filter_grid(images, grid)

        stitcher.compute_second_pass(images, grid)

        for direction in ["left", "top"]:
            for dim in "yx":
                key = f"{direction}_{dim}"
                grid[key] = grid[key].astype(pd.Int32Dtype())

        stitcher.compute_final_pass(grid)

        grid["y_pos2"] = grid["y_pos"] - grid["y_pos"].min()
        grid["x_pos2"] = grid["x_pos"] - grid["x_pos"].min()

        return grid

    def initialize_zarr(self, output_mos, stage_size, channels=4, nsections=1):
        """Initialize zarr"""
        sy, sx = stage_size
        zz = da.zeros(
            (channels, nsections, sy, sx),
            dtype="uint16",
            chunks=(channels, 1, 2048 * 2, 2048 * 2),
        )
        iarr = xr.DataArray(
            zz,
            dims=("channel", "z", "y", "x"),
            coords={
                "y": range(sy),
                "x": range(sx),
                "z": range(nsections),
                "channel": range(channels),
            },
        )

        iarr.attrs.update(self.metadata)

        imos = xr.Dataset()
        imos[self.name] = iarr
        imos_delayed = imos.to_zarr(output_mos, compute=False, mode="a")
        compute(imos_delayed, workers=self.workers)

    def stitch(self, images, z, grid, output_mos, conf=None):
        nch, _, ny, nx = images.shape

        result_df = grid[["row", "col", "y_pos2", "x_pos2"]].copy()

        stitched_image_size = (nch,) + self.stage_size

        _, sy, sx = stitched_image_size

        nz = len(self._section.z.values)
        if self.name not in zarr.open(output_mos, mode="r"):
            self.initialize_zarr(output_mos, self.stage_size, nch, nz)

        if conf is None:
            conf = da.ones_like(images[:, 0, :, :], dtype="uint8")

        dummy = da.zeros(
            stitched_image_size, dtype="uint16", chunks=(nch, 2048 * 4, 2048 * 4)
        )
        chunks = dummy.chunks

        for indx in itertools.product(*map(range, dummy.blocks.shape)):
            i, j = indx[-2:]
            array_location = [
                [sum(chunks[-2][:i]), sum(chunks[-2][: i + 1])],
                [sum(chunks[-1][:j]), sum(chunks[-1][: j + 1])],
            ]
            res = fuse(
                dummy.blocks[indx],
                images,
                conf,
                result_df,
                array_location,
                bzero=Settings.bzero,
                bscale=Settings.bscale,
                dtype="uint16",
            )

            stitched_image = res[:, None, ...].rechunk((nch, 1, 2048 * 4, 2048 * 4))

            nch, nz, ny, nx = stitched_image.shape
            sy = array_location[0]
            sx = array_location[1]
            arr = xr.DataArray(
                stitched_image,
                dims=("channel", "z", "y", "x"),
                coords={
                    "y": range(sy[0], sy[1]),
                    "x": range(sx[0], sx[1]),
                    "z": range(z, z + 1),
                    "channel": range(nch),
                },
            )

            arr.attrs.update(self.metadata)

            this_z = int(arr.z.values[0])
            mos = xr.Dataset()
            mos[self.name] = arr
            mos_delayed = mos.to_zarr(
                output_mos,
                mode="r+",
                compute=False,
                region={
                    "z": slice(this_z, this_z + 1),
                    "channel": slice(0, nch),
                    "x": slice(int(arr.x.min()), int(arr.x.max() + 1)),
                    "y": slice(int(arr.y.min()), int(arr.y.max() + 1)),
                },
            )
            compute(mos_delayed, workers=self.workers)

        return output_mos

    def downsample(self, output_mos):
        def transform(im):
            nch, nz, ny, nx = im.shape
            if nx < 100:
                return im[0, 0, : ny // 2, : nx // 2]
            res = []
            for ch in range(nch):
                this = cv2.pyrDown(im[ch, 0].astype("float32")) / 0.9
                res.append(this[None, ...])
            return np.stack(res).astype("uint16")

        groups = ["", "l.2", "l.4", "l.8", "l.16", "l.32"]
        for n in range(len(groups) - 1):
            ds = xr.open_zarr(output_mos, group=groups[n])

            dds = xr.Dataset()
            arr = ds[self.name].data
            nch, nz, cy, cx = arr.chunksize
            arr2 = arr.map_blocks(transform, chunks=(nch, nz, cy // 2, cx // 2))
            nch, nz, ny, nx = arr.shape
            cs = math.gcd(cy // 2, cx // 2)
            dds[self.name] = xr.DataArray(
                arr2.rechunk((nch, nz, cs, cs)),
                dims=("channel", "z", "y", "x"),
                coords={
                    "y": range(ny // 2),
                    "x": range(nx // 2),
                    "z": range(nz),
                    "channel": range(nch),
                },
            )
            dds[self.name].attrs.update(ds[self.name].attrs)
            dds_delayed = dds.to_zarr(
                output_mos, compute=False, mode="a", group=groups[n + 1]
            )
            future = compute(dds_delayed, workers=self.workers)
            cancel_futures([future, dds_delayed, dds, arr2])

    def preview(self, output_path, group=None):
        def _normalize(arr, p=99.5, q=2):
            pint = PercentileInterval(p)
            p1, p2 = pint.get_limits(arr.data.ravel())
            norm = (arr - p1) / (p2 - p1)
            norm = np.arcsinh(q * (norm - norm.min())) / q
            norm = norm.clip(0, 1) * (2**8 - 1)
            return norm.astype("uint8")

        colours = ["red", "green", "blue", "cyan", "yellow", "magenta", "grey"]
        # colours = ["cyan", "blue", "green", "red", "yellow", "magenta", "grey"]
        select_colour = {
            "red": (0, 1),
            "green": (0.3, 1),
            "blue": (0.66, 1),
            "cyan": (0.5, 1),
            "yellow": (0.15, 1),
            "magenta": (0.86, 1),
            "grey": (0.3, 0),
        }

        ds = xr.open_zarr(output_path / "mos", group=group or "l.16")
        data = ds[self.name].sel(z=0)
        data_norm = data.groupby("channel").map(_normalize)

        hs_range = [select_colour[col] for col in colours]
        channels_rgb = []
        for hs, img in zip(hs_range, data_norm.data):
            ch_hsl = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.float32)
            ch_hsl[:, :, 0] = hs[0]
            ch_hsl[:, :, 1] = hs[1]
            ch_hsl[:, :, 2] = img
            channels_rgb.append(hsv_to_rgb(ch_hsl))

        channels_rgb = np.stack(channels_rgb)
        rgb = channels_rgb.sum(axis=0).clip(0, 255).astype("uint8")

        output_preview = output_path / "preview"
        output_preview.mkdir(exist_ok=True)
        imageio.imsave(output_preview / f"{self.name}.png", rgb)


class GenericStitcher:
    @staticmethod
    def finalize(input_path, output_path):
        dd = {
            "version": "1.0",
            "jobid": os.getenv("UID") or 0,
            "software": [
                {"name": "imaxt-mosaic", "version": imaxt_mosaic.__version__},
                {"name": "opencv", "version": cv2.__version__},
                {"name": "numpy", "version": np.__version__},
                {"name": "dask", "version": dask.__version__},
                {"name": "xarray", "version": xr.__version__},
                {"name": "zarr", "version": zarr.__version__},
                {"name": "distributed", "version": distributed.__version__},
            ],
            "timestamp": datetime.now().astimezone().isoformat(),
            "origname": input_path.name,
            "multiscale": json.dumps(
                {
                    "datasets": [
                        {"path": "", "level": 1},
                        {"path": "l.2", "level": 2},
                        {"path": "l.4", "level": 4},
                        {"path": "l.8", "level": 8},
                        {"path": "l.16", "level": 16},
                        {"path": "l.32", "level": 32},
                    ],
                    "metadata": {"method": "cv2.pyrDown", "version": cv2.__version__},
                }
            ),
        }

        z = zarr.open(output_path / "mos", mode="r+")
        z.attrs.update(dd)
        consolidate_metadata(z.store)
        z.store.close()

    @staticmethod
    def cleanup(output_path):
        for root, dirs, files in os.walk(output_path):
            os.chmod(root, 0o555)
            for file in files:
                os.chmod(os.path.join(root, file), 0o444)

    @staticmethod
    def initialize(output_path):
        if not output_path.exists():
            return
        for root, dirs, files in os.walk(output_path):
            os.chmod(root, 0o755)
            for file in files:
                os.chmod(os.path.join(root, file), 0o644)
