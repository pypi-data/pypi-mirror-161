import asyncio
import time
import traceback
from contextlib import suppress

import xarray as xr
import zarr
from distributed import as_completed, get_client, wait
from imaxt_mosaic import plugins
from owl_dev.logging import logger

from ..settings import Settings
from ..utils import get_workers_address, restart_workers, trim_memory_workers

USE_MULTIPLE_WORKERS = True


def ensure_worker(worker, status):
    workers = get_workers_address()
    if worker not in workers:
        logger.error("Worker %s is not available anymore", worker)
        worker = [w for w in workers if w not in status.values()]
        if not worker:
            worker = None
        else:
            logger.info("Using worker %s", worker)
            worker = worker[0]
    return worker


async def ensure_future_processing(future, timeout):
    await asyncio.sleep(0.1)
    if timeout is None:
        return

    await asyncio.sleep(timeout)

    client = get_client()
    proc = await client.processing()
    processing = any(future.key in v for v in proc.values())
    if not processing and not future.done():
        future.cancel()


async def ensure_future_timeout(future, timeout):
    watch = time.monotonic()
    # client = get_client()

    while not future.done():
        await asyncio.sleep(60)
        if time.monotonic() - watch > timeout:
            logger.error("Timeout reached (%s)", timeout)
            await future.cancel()
            break
        # info = client.scheduler_info()
        # now = time.time()
        # last_seen = max(now - v["last_seen"] for v in info["workers"].values())
        # if last_seen > 120:
        #     await future.cancel()
        #     break


def submit(*args, **kwargs):
    timeout = kwargs.pop("timeout", None)
    client = get_client()
    fut = client.submit(*args, **kwargs)
    if timeout > 0:
        task = asyncio.ensure_future(ensure_future_timeout(fut, timeout))
    else:
        task = None
    return fut, task


def initialize_output_path(output_path):
    logger.info("Initializing output directory %s", output_path / "mos")
    xr.Dataset().to_zarr(output_path / "mos", mode="w")


def _imaxt_stitch_multiple_workers(
    input_path, output_path, this_section, overwrite, func
):
    logger.info("Submitting section %s", this_section)
    fut, task = submit(
        func,
        input_path,
        this_section,
        None,
        output_path,
        overwrite,
        timeout=Settings.timeout,
    )
    with suppress(Exception):
        wait(fut)
    if fut.cancelled():
        logger.info("Section %s was cancelled", this_section)
        restart_workers()
        return this_section
    elif fut.exception():
        tb = fut.traceback()
        logger.error("Section %s failed : %s", this_section, fut.exception())
        logger.error(traceback.format_tb(tb))
        return
    else:
        logger.info("Stitched section %s, %s", this_section, fut.status)
    task.cancel()
    trim_memory_workers()


def _imaxt_stitch_single_worker(input_path, output_path, sections, overwrite, func):
    workers = get_workers_address()
    futures = []
    status = {}
    for worker in workers:
        if not sections:
            break
        this_section = sections.pop(0)
        if len(futures) >= len(workers):
            break
        logger.info("Submitting section %s to worker %s", this_section, worker)
        fut, _ = submit(
            func,
            input_path,
            this_section,
            worker,
            output_path,
            overwrite,
            workers=[worker],
            timeout=Settings.timeout,
        )
        futures.append(fut)
        status[fut.key] = (worker, this_section)

    seq = as_completed(futures)
    for future in seq:
        worker, this_section = status.pop(future.key)
        if future.cancelled():
            logger.error("Cancelled section %s in worker %s", this_section, worker)
            sections.insert(0, this_section)
        elif future.exception():
            tb = fut.traceback()
            logger.error(
                "Error in section %s in worker %s : %s : %s",
                this_section,
                worker,
                future.exception(),
                traceback.format_tb(tb),
            )
        else:
            logger.info("Stitched section %s on worker %s", this_section, worker)

        worker = ensure_worker(worker, status)
        if not worker:
            continue
        trim_memory_workers(worker)

        if sections:
            this_section = sections.pop(0)
            logger.info("Submitting section %s to worker %s", this_section, worker)
            fut = submit(
                func,
                input_path,
                this_section,
                worker,
                output_path,
                overwrite,
                workers=[worker],
                timeout=Settings.timeout,
            )
            seq.add(fut)
            status[fut.key] = (worker, this_section)


def imaxt_stitch(input_path, output_path, stitcher, overwrite=False):
    ds = xr.open_zarr(input_path)

    # Get stitcher plugin for dataset
    _stitch = plugins.get_plugin(stitcher)
    _stitch.initialize(output_path)

    if overwrite:
        initialize_output_path(output_path)

    try:
        xr.open_zarr(output_path / "mos", consolidated=True)
    except (zarr.errors.GroupNotFoundError, KeyError):
        initialize_output_path(output_path)

    sections = list(ds)
    if Settings.sections:
        sections = [sections[i - 1] for i in Settings.sections]

    if USE_MULTIPLE_WORKERS:
        while sections:
            this_section = sections.pop(0)
            res = _imaxt_stitch_multiple_workers(
                input_path, output_path, this_section, overwrite, _stitch.run
            )
            if res is not None:
                sections.insert(0, res)
    else:  # USE_MULTIPLE_WORKERS is False
        _imaxt_stitch_single_worker(
            input_path, output_path, sections, overwrite, _stitch.run
        )

    logger.info("Finalizing stitcher")
    _stitch.finalize(input_path, output_path)

    logger.info("Cleaning up")
    _stitch.cleanup(output_path)
