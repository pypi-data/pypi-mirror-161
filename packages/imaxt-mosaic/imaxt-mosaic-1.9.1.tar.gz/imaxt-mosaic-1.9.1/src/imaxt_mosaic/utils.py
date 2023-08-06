import ctypes
import importlib

import cv2
import dask.array as da
import numpy as np
from dask import delayed
from dask.distributed import get_client, wait
from shapely.geometry import Polygon
from skimage.transform import warp

import imaxt_mosaic.plugins

from .settings import Settings

# Generic functions


def create_batches(ntotal, nbatch):
    indx = list(range(ntotal))
    return [indx[i : i + nbatch] for i in range(0, len(indx), nbatch)]


def update_config(stitcher, config):
    """Set configuration"""
    func = imaxt_mosaic.plugins.get_plugin(stitcher)
    mod = importlib.import_module(func.__module__)
    this = mod.__config.copy()
    this.update(config)
    Settings.set_config(this)
    client = get_client()
    client.run(Settings.set_config, this)


# Image processing


def get_coords(coords, cof_x, cof_y, tan, normal_x, normal_y):
    c0, c1 = coords
    xc0, xc1, xc2, xc3 = cof_x
    yc0, yc1, yc2, yc3 = cof_y
    t0, t1 = tan

    x_adim = (c0 - t0) / normal_x
    y_adim = (c1 - t1) / normal_y

    xx = x_adim * x_adim
    yy = y_adim * y_adim
    distorted_x = (
        c0
        + xc0 * x_adim / abs(x_adim)
        + x_adim * (yy * xc1 + xx * xc2 + xx * y_adim * xc3)
    )
    distorted_y = (
        c1
        + yc0 * y_adim / abs(y_adim)
        + y_adim * (xx * yc1 + yy * yc2 + yy * x_adim * yc3)
    )

    return (distorted_x, distorted_y)


@delayed(pure=True)
def get_matrix(shape, cof_dist):
    coords0, coords1 = np.mgrid[: shape[0], : shape[1]].astype("float")
    for i in range(shape[0]):
        for j in range(shape[1]):
            res = get_coords(
                (i, j),
                cof_dist["cof_x"],
                cof_dist["cof_y"],
                cof_dist["tan"],
                Settings.normal_x,
                Settings.normal_y,
            )
            coords0[i, j] = res[0]
            coords1[i, j] = res[1]
    return np.array([coords0, coords1])


def calwarp(img, flat, dark, matrix):
    norm = (img - dark) / (np.clip(flat, 1e-6, 1e6) + 1e-16)
    return warp(norm, matrix)


def apply_geometric_transform(img, flat, dark, cof_dist):
    """Apply geometric transformation to array

    Parameters
    ----------
    img
        Input image
    flat
        flat field image
    cof_dist
        Distortion coefficients

    Returns
    -------
    distortion corrected array
    """
    matrix = get_matrix(img.shape, cof_dist)
    new = delayed(calwarp)(img, flat, dark, matrix)
    return da.from_delayed(new, shape=img.shape, dtype="float32")


def imageproc(img, flat=1, dark=0):
    new = apply_geometric_transform(
        img.astype("float32") / Settings.norm_val,
        flat,
        dark / Settings.norm_val,
        Settings.cof_dist,
    )
    return new[Settings.y_min : Settings.y_max, Settings.x_min : Settings.x_max]


def downsample(images):
    _, ny, nx = images.shape
    images_delayed = [delayed(cv2.pyrDown)(im.astype("float32")) for im in images]
    images_down = [
        da.from_delayed(
            im,
            (ny // 2, nx // 2),
            dtype="float32",
        )
        for im in images_delayed
    ]
    images = da.stack(images_down)
    return images


def fuse(
    x,
    images,
    conf,
    grid,
    array_location,
    bzero: float = 0,
    bscale: float = 1,
    dtype: str = "uint16",
):
    """Fuse images to a single image"""
    p2 = Polygon.from_bounds(
        array_location[1][0],
        array_location[0][0],
        array_location[1][1],
        array_location[0][1],
    )

    a = da.zeros_like(x, dtype="float32")
    cf = da.zeros_like(x, dtype="float32")
    nch, ntiles, ny, nx = images.shape
    for i, row in grid.iterrows():
        orig_x, orig_y = row["x_pos2"], row["y_pos2"]
        p1 = Polygon.from_bounds(orig_x, orig_y, orig_x + nx, orig_y + ny)

        if p2.intersects(p1):
            p = p2.intersection(p1)
            if p.area < 1:
                continue

            p_ref = [
                int(p.bounds[0] - p2.bounds[0]),
                int(p.bounds[1] - p2.bounds[1]),
                int(p.bounds[2] - p2.bounds[0]),
                int(p.bounds[3] - p2.bounds[1]),
            ]

            p_this = [
                int(p.bounds[0] - p1.bounds[0]),
                int(p.bounds[1] - p1.bounds[1]),
                int(p.bounds[2] - p1.bounds[0]),
                int(p.bounds[3] - p1.bounds[1]),
            ]
            try:
                im = images[:, i, p_this[1] : p_this[3], p_this[0] : p_this[2]]
                cc = conf[:, p_this[1] : p_this[3], p_this[0] : p_this[2]]

                a[:, p_ref[1] : p_ref[3], p_ref[0] : p_ref[2]] += im * cc
                cf[:, p_ref[1] : p_ref[3], p_ref[0] : p_ref[2]] += cc
            except Exception:
                raise
    a = a / (cf + 1e-10)
    a = (a + bzero) * bscale
    a = a.clip(0, 2**16 - 1)
    return a.astype(dtype)


def hsv_to_rgb(hsv):
    """
    Convert hsv values to rgb.
    Parameters
    ----------
    hsv : (..., 3) array-like
       All values assumed to be in range [0, 1]
    Returns
    -------
    (..., 3) ndarray
       Colors converted to RGB values in range [0, 1]
    """
    hsv = np.asarray(hsv)

    # check length of the last dimension, should be _some_ sort of rgb
    if hsv.shape[-1] != 3:
        raise ValueError(
            "Last dimension of input array must be 3; "
            "shape {shp} was found.".format(shp=hsv.shape)
        )

    in_shape = hsv.shape
    hsv = np.array(
        hsv,
        copy=False,
        dtype=np.promote_types(hsv.dtype, np.float32),  # Don't work on ints.
        ndmin=2,  # In case input was 1D.
    )

    h = hsv[..., 0]
    s = hsv[..., 1]
    v = hsv[..., 2]

    r = np.empty_like(h)
    g = np.empty_like(h)
    b = np.empty_like(h)

    i = (h * 6.0).astype(int)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))

    idx = i % 6 == 0
    r[idx] = v[idx]
    g[idx] = t[idx]
    b[idx] = p[idx]

    idx = i == 1
    r[idx] = q[idx]
    g[idx] = v[idx]
    b[idx] = p[idx]

    idx = i == 2
    r[idx] = p[idx]
    g[idx] = v[idx]
    b[idx] = t[idx]

    idx = i == 3
    r[idx] = p[idx]
    g[idx] = q[idx]
    b[idx] = v[idx]

    idx = i == 4
    r[idx] = t[idx]
    g[idx] = p[idx]
    b[idx] = v[idx]

    idx = i == 5
    r[idx] = v[idx]
    g[idx] = p[idx]
    b[idx] = q[idx]

    idx = s == 0
    r[idx] = v[idx]
    g[idx] = v[idx]
    b[idx] = v[idx]

    rgb = np.stack([r, g, b], axis=-1)

    return rgb.reshape(in_shape)


# Dask


def restart_workers(n_workers=1, timeout=None):
    client = get_client()
    client.restart()
    client.wait_for_workers(n_workers=n_workers or 1, timeout=timeout or "300s")


def trim_memory_workers(worker=None):
    client = get_client()
    if worker:
        client.run(trim_memory, workers=[worker])
    else:
        client.run(trim_memory)
    client.run_on_scheduler(trim_memory)


def trim_memory() -> int:
    libc = ctypes.CDLL("libc.so.6")
    return libc.malloc_trim(0)


def get_memory_usage():
    libc = ctypes.CDLL("libc.so.6")
    return libc.malloc_usable_size(0)


def get_workers_info():
    client = get_client()
    return client.scheduler_info()["workers"]


def get_workers_address():
    client = get_client()
    return list(client.run(lambda: 1).keys())


def persist_array(array, workers=None, do_async=False):
    client = get_client()
    # secede()
    if workers:
        arr = client.persist(array, workers=workers)
    else:
        arr = client.persist(array)
    if not do_async:
        wait(arr)
    # rejoin()
    return arr


def compute(task, workers=None, do_async=False):
    client = get_client()
    # with contextlib.suppress(Exception):
    #     secede()
    if workers:
        future = client.compute(task, workers=workers)
    else:
        future = client.compute(task)
    if not do_async:
        wait(future)
    # with contextlib.suppress(Exception):
    #     rejoin()
    # if future.exception():
    #     raise future.exception()
    return future


def cancel_futures(futures, force=True):
    if not isinstance(futures, list):
        futures = [futures]

    client = get_client()
    return client.cancel(futures, force=force)
