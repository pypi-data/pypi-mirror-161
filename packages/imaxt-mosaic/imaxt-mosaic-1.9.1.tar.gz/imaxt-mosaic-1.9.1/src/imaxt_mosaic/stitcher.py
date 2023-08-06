from dataclasses import dataclass

import dask
import numpy as np
import pandas as pd
from dask import delayed
from dask.distributed import get_client, wait
from sklearn.covariance import EllipticEnvelope

from .stitchlib.optimization import (
    compute_final_position,
    compute_maximum_spanning_tree,
)
from .stitchlib.refinement import find_local_max_integer_constrained
from .stitchlib.stage_model import (
    compute_image_overlap2,
    filter_by_overlap_and_correlation,
    filter_by_repeatability,
    filter_outliers,
    replace_invalid_translations,
)
from .stitchlib.translation import calculate_translation

# from pathlib import Path


# from typing import Tuple
# import utils
# from utils import Settings
# import pandas as pd


@dataclass
class ElipticEnvelopPredictor:
    contamination: float
    epsilon: float
    random_seed: int

    def __call__(self, X):
        ee = EllipticEnvelope(contamination=self.contamination)
        rng = np.random.default_rng(self.random_seed)
        X = rng.normal(size=X.shape) * self.epsilon + X
        return ee.fit_predict(X) > 0


class Stitcher:
    def __init__(self, images, stagepos, downsample=True):
        self.images = images
        self.sp = stagepos
        self.downsample = downsample
        try:
            workers = dask.config.config["annotations"]["workers"]
            self.workers = workers or None
        except KeyError:
            self.workers = None

    def compute_first_pass(self, images, grid):
        res = []
        k = 0
        for direction in ["left", "top"]:
            for i2, g in grid.iterrows():
                i1 = g[direction]
                if pd.isna(i1):
                    continue
                image1 = images[i1]
                image2 = images[i2]
                ny, nx = image1.shape

                if self.sp.position_initial_guess is not None:

                    def get_lims(dimension, size):
                        val = g[f"{direction}_{dimension}_init_guess"]
                        r = size * self.sp.overlap_diff_threshold / 100.0
                        return np.round([val - r, val + r]).astype(np.int64)

                    lims = np.array(
                        [
                            get_lims(dimension, size)
                            for dimension, size in zip("yx", [ny, nx])
                        ]
                    )
                else:
                    lims = np.array([[-ny, ny], [-nx, nx]])

                max_peak = delayed(calculate_translation)(image1, image2, lims)
                k += 1
                res.append(max_peak)

        client = get_client()
        # secede()
        max_peak = [client.compute(r, workers=self.workers) for r in res]
        wait(max_peak)
        # rejoin()
        max_peak = [m.result() for m in max_peak]

        k = 0
        for direction in ["left", "top"]:
            for i2, g in grid.iterrows():
                i1 = g[direction]
                if pd.isna(i1):
                    continue
                for j, key in enumerate(["ncc", "y", "x"]):
                    grid.loc[i2, f"{direction}_{key}_first"] = max_peak[k][j]
                k += 1

        return grid

    def filter_grid(self, images, grid, pou=3):
        sizeY, sizeX = images[0].shape
        predictor = ElipticEnvelopPredictor(
            contamination=0.4, epsilon=0.01, random_seed=0
        )
        left_displacement = compute_image_overlap2(
            grid[grid["left_ncc_first"] > 0.5], "left", sizeY, sizeX, predictor
        )
        top_displacement = compute_image_overlap2(
            grid[grid["top_ncc_first"] > 0.5], "top", sizeY, sizeX, predictor
        )
        overlap_top = np.clip(100 - top_displacement[0] * 100, pou, 100 - pou)
        overlap_left = np.clip(100 - left_displacement[1] * 100, pou, 100 - pou)

        # compute_repeatability
        grid["top_valid1"] = filter_by_overlap_and_correlation(
            grid["top_y_first"], grid["top_ncc_first"], overlap_top, sizeY, pou
        )
        grid["top_valid2"] = filter_outliers(grid["top_y_first"], grid["top_valid1"])
        grid["left_valid1"] = filter_by_overlap_and_correlation(
            grid["left_x_first"], grid["left_ncc_first"], overlap_left, sizeX, pou
        )
        grid["left_valid2"] = filter_outliers(grid["left_x_first"], grid["left_valid1"])

        rs = []
        for direction, dims, rowcol in zip(
            ["top", "left"], ["yx", "xy"], ["col", "row"]
        ):
            valid_key = f"{direction}_valid2"
            valid_grid = grid[grid[valid_key]]
            if len(valid_grid) > 0:
                w1s = valid_grid[f"{direction}_{dims[0]}_first"]
                r1 = np.ceil((w1s.max() - w1s.min()) / 2)
                _, w2s = zip(
                    *valid_grid.groupby(rowcol)[f"{direction}_{dims[1]}_first"]
                )
                r2 = np.ceil(np.max([np.max(w2) - np.min(w2) for w2 in w2s]) / 2)
                rs.append(max(r1, r2))
            rs.append(0)
        self.r = np.max(rs)

        grid = filter_by_repeatability(grid, self.r)
        grid = replace_invalid_translations(grid)
        return grid

    def compute_second_pass(self, images, grid):
        res = []
        for direction in ["left", "top"]:
            for i2, g in grid.iterrows():
                i1 = g[direction]
                if pd.isna(i1):
                    continue
                image1 = images[i1]
                image2 = images[i2]
                sizeY, sizeX = image1.shape

                init_values = [
                    int(g[f"{direction}_y_second"]),
                    int(g[f"{direction}_x_second"]),
                ]
                limits = [
                    [
                        max(-sizeY + 1, init_values[0] - self.r),
                        min(sizeY - 1, init_values[0] + self.r),
                    ],
                    [
                        max(-sizeX + 1, init_values[1] - self.r),
                        min(sizeX - 1, init_values[1] + self.r),
                    ],
                ]
                v = delayed(find_local_max_integer_constrained)(
                    image1, image2, np.array(init_values), np.array(limits)
                )

                res.append(v)

        out = dask.compute(res)[0]

        k = 0
        for direction in ["left", "top"]:
            for i2, g in grid.iterrows():
                i1 = g[direction]
                if pd.isna(i1):
                    continue
                values, ncc_value = out[k]
                grid.loc[i2, f"{direction}_y"] = values[0]
                grid.loc[i2, f"{direction}_x"] = values[1]
                grid.loc[i2, f"{direction}_ncc"] = ncc_value
                k += 1

        return grid

    def compute_final_pass(self, grid):
        tree = compute_maximum_spanning_tree(grid)
        grid = compute_final_position(grid, tree)
        return grid
