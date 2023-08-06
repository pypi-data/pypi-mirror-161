import itertools

import numpy as np
import pandas as pd


class StagePos:
    """Stage Position

    This class

    Parameters
    ----------
    rows
        array of row position of each tile

    cols
        array of column position of each tile

    overlap
        overlap between tiles
    """

    def __init__(self, rows, cols, initial_guess=None):
        self.rows = rows
        self.cols = cols
        self.grid_init(position_initial_guess=initial_guess)

    def __repr__(self):
        return f"StagePos({self.rows}, {self.cols})"

    @classmethod
    def SnakePattern(cls, nrow, ncol, reverse_row=False, reverse_col=False):
        final_x_ind = np.broadcast_to(np.arange(ncol), (nrow, ncol)).T.ravel()
        y_chunk = np.arange(nrow)
        final_y_ind = np.concatenate(
            [y_chunk[::-1] if i % 2 else y_chunk for i in range(ncol)]
        )
        if reverse_row:
            rows = nrow - final_y_ind - 1
        else:
            rows = final_y_ind
        if reverse_col:
            cols = ncol - final_x_ind - 1
        else:
            cols = final_x_ind
        return cls(rows, cols)

    def get_index(self, grid, col, row):
        df = grid[(grid["col"] == col) & (grid["row"] == row)]
        assert len(df) < 2
        if len(df) == 1:
            return df.index[0]
        else:
            return None

    @property
    def stage_size(self):
        spy, spx = (
            self.grid["y_pos_init_guess"].max() + 2048,
            self.grid["x_pos_init_guess"].max() + 2048,
        )
        return int((spy // 2048) * 2048), int((spx // 2048) * 2048)

    def grid_init(self, position_initial_guess=None, overlap_diff_threshold=30):
        self.overlap_diff_threshold = overlap_diff_threshold
        self.position_initial_guess = position_initial_guess

        rows, cols = self.rows, self.cols
        position_indices = np.array([rows, cols]).T
        _rows, _cols = position_indices.T
        grid = pd.DataFrame(
            {
                "col": _cols,
                "row": _rows,
            },
            index=np.arange(len(_cols)),
        )
        grid["top"] = grid.apply(
            lambda g: self.get_index(grid, g["col"], g["row"] - 1), axis=1
        ).astype(pd.Int32Dtype())
        grid["left"] = grid.apply(
            lambda g: self.get_index(grid, g["col"] - 1, g["row"]), axis=1
        ).astype(pd.Int32Dtype())

        if position_initial_guess is not None:
            for j, dimension in enumerate(["y", "x"]):
                grid[f"{dimension}_pos_init_guess"] = position_initial_guess[:, j]
            for direction, dimension in itertools.product(["left", "top"], ["y", "x"]):
                for ind, g in grid.iterrows():
                    i1 = g[direction]
                    if pd.isna(i1):
                        continue
                    g2 = grid.loc[i1]
                    grid.loc[ind, f"{direction}_{dimension}_init_guess"] = (
                        g[f"{dimension}_pos_init_guess"]
                        - g2[f"{dimension}_pos_init_guess"]
                    )
        self.grid = grid
