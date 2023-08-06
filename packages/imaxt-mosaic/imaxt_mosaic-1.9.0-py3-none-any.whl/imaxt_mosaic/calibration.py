import json
from contextlib import suppress

import dask
import dask.array as da
import numpy as np
import xarray as xr
import zarr
from astropy.visualization import PercentileInterval
from dask import delayed
from owl_dev.logging import logger

from .utils import create_batches, trim_memory_workers


@delayed
def compute_percentile(img, percentile=98):
    p = PercentileInterval(percentile)
    p1, p2 = p.get_limits(img.ravel())
    return (p1, p2)


def compute_flat(arr, nsample=1000):
    flat = 0
    nimgs = 0
    maxval = 0
    nsample = min([nsample, len(arr)])
    batches = create_batches(len(arr), nsample)
    for b in batches:
        if len(b) < nsample:
            continue
        flat = flat + arr[b].sum(axis=0).compute()
        maxval = max(maxval, arr[b].max().compute())
        nimgs = nimgs + len(b)

    flat = flat / nimgs
    flat_median = np.median(flat)
    flat = flat / flat_median

    if len(arr) > nsample:
        indx = np.random.choice(len(arr), nsample, replace=False)
        arr = arr[indx]
    res = [compute_percentile(d) for d in arr]
    res = dask.compute(res)[0]
    pmax = max(r[1] for r in res)
    pmin = min(r[0] for r in res)

    ny, nx = flat.shape
    flat = xr.DataArray(
        flat[None, ...],
        dims=("channel", "y", "x"),
        coords={
            "y": range(ny),
            "x": range(nx),
            "channel": [0],
        },
    )

    flat.attrs["pval"] = (float(pmin), float(pmax))
    flat.attrs["median"] = flat_median
    flat.attrs["nimages"] = nimgs
    flat.attrs["maxval"] = float(maxval)

    return flat


def compute_dark(arr, nthresh=10):
    ni, ny, nx = arr.shape
    if ni < nthresh:
        dark = np.zeros((ny, nx))
    else:
        dark = da.median(arr, axis=0).compute()

    ny, nx = dark.shape
    dark = xr.DataArray(
        dark[None, ...],
        dims=("channel", "y", "x"),
        coords={
            "y": range(ny),
            "x": range(nx),
            "channel": [0],
        },
    )

    dark.attrs["nimages"] = ni

    return dark


def write_cals(flats, darks, output_path):
    arr_flats = xr.concat(flats, dim="channel")
    arr_flats.attrs["median"] = json.dumps(
        {int(f.channel.values): f.attrs["median"] for f in flats}
    )
    arr_flats.attrs["nimages"] = json.dumps(
        {int(f.channel.values): f.attrs["nimages"] for f in flats}
    )
    arr_flats.attrs["maxval"] = json.dumps(
        {int(f.channel.values): f.attrs["maxval"] for f in flats}
    )
    arr_flats.attrs["pval"] = json.dumps(
        {int(f.channel.values): f.attrs["pval"] for f in flats}
    )

    arr_darks = xr.concat(darks, dim="channel")
    arr_darks.attrs["nimages"] = json.dumps(
        {int(f.channel.values): f.attrs["nimages"] for f in darks}
    )

    ds = xr.Dataset()
    ds["flats"] = arr_flats
    ds["darks"] = arr_darks

    res = ds.to_zarr(output_path / "cals", mode="w", consolidated=True)
    return res


def compute_calibrations(input_path, output_path, overwrite=False, max_images=2000):
    if not overwrite and output_path.exists():
        with suppress(zarr.errors.PathNotFoundError):
            zarr.open(output_path / "cals", mode="r")
            logger.info("Calibrations already exist, skipping")
            return

    ds = xr.open_zarr(input_path)
    flats = []
    darks = []
    for ch in ds.channel:

        logger.debug("Processing channel %s", ch.values)
        arr = ds.sel(channel=ch, z=0).to_array().data
        ns, nt, ny, nx = arr.shape
        arr = arr.reshape((ns * nt, ny, nx))

        arr = arr[:max_images]
        nimgs, *_ = arr.shape
        nsample = min(nimgs, 500)
        logger.debug("Selecting images")
        means = [
            arr[batch].mean(axis=(1, 2)).compute()
            for batch in create_batches(nimgs, nsample)
            if len(batch) == nsample
        ]

        means = np.hstack(means)
        thresh = np.quantile(means, (1e-17, 0.5))
        arr = arr[: len(means)]

        good = means > thresh[1]
        logger.debug("Computing flatfield. Found %d good images", good.sum())
        flat = compute_flat(arr[good], nsample=min(1000, sum(good)))
        flats.append(flat.assign_coords({"channel": [ch]}))

        good = means < thresh[0]
        logger.debug("Computing dark. Found %d good images", good.sum())
        dark = compute_dark(arr[good])
        darks.append(dark.assign_coords({"channel": [ch]}))

    logger.debug("Writing calibration frames to %s", output_path)
    write_cals(flats, darks, output_path)
    trim_memory_workers()
