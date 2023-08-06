import itertools

import numpy as np

from .mutual_information import mutual_information
from .translation import extract_overlap_subregion


def overlap_ncc(image1, image2, params):
    x, y = params
    subI1 = extract_overlap_subregion(image1, x, y)
    subI2 = extract_overlap_subregion(image2, -x, -y)
    return mutual_information(subI1, subI2)


def find_local_max_integer_constrained(
    image1, image2, init_x, limits, max_iter=100, func=overlap_ncc
):
    """Find local maxima of a function with integer steps.

    Parameters
    ----------
    func : Callable[[FloatArray], Float]
        function to optimize
    init_x : FloatArray
        the initial guess of parameters
    limits : FloatArray
        the limit of parameters
    max_iter : Int, optional
        the maximum iteration for the optimization, by default 100

    Returns
    -------
    x : FloatArray
        the optimized parameters
    val : Float
        the optimized value
    """
    init_x = np.array(init_x)
    limits = np.array(limits)
    dim = init_x.shape[0]
    assert limits.shape[0] == dim
    value = func(image1, image2, init_x)
    x = init_x
    for _ in range(max_iter):
        around_x = [x + np.array(dxs) for dxs in itertools.product(*[[-1, 0, 1]] * dim)]
        around_x = [
            x
            for x in around_x
            if np.all(limits[:, 0] <= x) and np.all(x <= limits[:, 1])
        ]
        around_values = [func(image1, image2, pars) for pars in around_x]

        max_ind = np.argmax(around_values)
        max_x = around_x[max_ind]
        max_value = around_values[max_ind]
        if max_value <= value:
            return x, value
        else:
            x = max_x
            value = max_value
    return x, value
