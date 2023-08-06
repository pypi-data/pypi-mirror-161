import itertools

import numpy as np

from .mutual_information import mutual_information


def multi_peak_max(PCM):
    """Find the first to n th largest peaks in PCM.

    Parameters
    ---------
    PCM : np.ndarray
        the peak correlation matrix

    Returns
    -------
    rows : np.ndarray
        the row indices for the peaks
    cols : np.ndarray
        the column indices for the peaks
    vals : np.ndarray
        the values of the peaks
    """
    row, col = np.unravel_index(np.argsort(PCM.ravel()), PCM.shape)
    vals = PCM[row[::-1], col[::-1]]
    return row[::-1], col[::-1], vals


def pcm(image1, image2, extra=False):
    """Compute peak correlation matrix for two images.

    Parameters
    ---------
    image1 : np.ndarray
        the first image (the dimension must be 2)

    image2 : np.ndarray
        the second image (the dimension must be 2)

    Returns
    -------
    PCM : np.ndarray
        the peak correlation matrix
    """
    assert image1.ndim == 2
    assert image2.ndim == 2
    assert np.array_equal(image1.shape, image2.shape)
    F1 = np.fft.fft2(image1)
    F2 = np.fft.fft2(image2)
    FC = F1 * np.conjugate(F2)
    eps = np.finfo(FC.real.dtype).eps
    if extra:
        norm = np.sqrt(F1 * F1.conj() + F2 * F2.conj()) + eps
        # FC = fourier_gaussian(FC / norm, 5)
    else:
        norm = np.maximum(np.abs(FC), 100 * eps)
        # FC = FC / norm
    return np.fft.ifft2(FC / norm).real.astype(np.float32)


def extract_overlap_subregion(image, y, x):
    """Extract the overlapping subregion of the image.

    Parameters
    ---------
    image : np.ndarray
        the image (the dimension must be 2)
    y : Int
        the y (second last dim.) position
    x : Int
        the x (last dim.) position
    Returns
    -------
    subimage : np.ndarray
        the extracted subimage
    """
    sizeY = image.shape[0]
    sizeX = image.shape[1]
    assert (np.abs(y) < sizeY) and (np.abs(x) < sizeX)
    # clip x to (0, size_Y)
    xstart = int(max(0, min(y, sizeY, key=int), key=int))
    # clip x+sizeY to (0, size_Y)
    xend = int(max(0, min(y + sizeY, sizeY, key=int), key=int))
    ystart = int(max(0, min(x, sizeX, key=int), key=int))
    yend = int(max(0, min(x + sizeX, sizeX, key=int), key=int))
    return image[xstart:xend, ystart:yend]


def interpret_translation(image1, image2, yins, xins, ymin, ymax, xmin, xmax, n=2):
    """Interpret the translation to find the translation with heighest ncc.

    Parameters
    ---------
    image1 : np.ndarray
        the first image (the dimension must be 2)
    image2 : np.ndarray
        the second image (the dimension must be 2)
    yins : IntArray
        the y positions estimated by PCM
    xins : IntArray
        the x positions estimated by PCM
    ymin : Int
        the minimum value of y (second last dim.)
    ymax : Int
        the maximum value of y (second last dim.)
    xmin : Int
        the minimum value of x (last dim.)
    xmax : Int
        the maximum value of x (last dim.)
    n : Int
        the number of peaks to check, default is 2.

    Returns
    -------
    _ncc : Float
        the highest ncc
    x : Int
        the selected x position
    y : Int
        the selected y position
    """
    assert image1.ndim == 2
    assert image2.ndim == 2
    assert np.array_equal(image1.shape, image2.shape)
    sizeY = image1.shape[0]
    sizeX = image1.shape[1]
    assert np.all(yins >= 0) and np.all(yins < sizeY)
    assert np.all(xins >= 0) and np.all(xins < sizeX)

    _ncc = -np.infty
    y = 0
    x = 0

    ymagss = [yins, sizeY - yins]
    ymagss[1][ymagss[0] == 0] = 0
    xmagss = [xins, sizeX - xins]
    xmagss[1][xmagss[0] == 0] = 0

    # concatenate all the candidates
    _poss = []
    for ymags, xmags, ysign, xsign in itertools.product(
        ymagss, xmagss, [-1, +1], [-1, +1]
    ):
        yvals = ymags * ysign
        xvals = xmags * xsign
        _poss.append([yvals, xvals])
    poss = np.array(_poss)
    valid_ind = (
        (ymin <= poss[:, 0, :])
        & (poss[:, 0, :] <= ymax)
        & (xmin <= poss[:, 1, :])
        & (poss[:, 1, :] <= xmax)
    )
    assert np.any(valid_ind)
    valid_ind = np.any(valid_ind, axis=0)
    for pos in np.moveaxis(poss[:, :, valid_ind], -1, 0)[: int(n)]:
        for yval, xval in pos:
            if (ymin <= yval) and (yval <= ymax) and (xmin <= xval) and (xval <= xmax):
                subI1 = extract_overlap_subregion(image1, yval, xval)
                subI2 = extract_overlap_subregion(image2, -yval, -xval)
                ncc_val = mutual_information(subI1, subI2)
                if ncc_val > _ncc:
                    _ncc = float(ncc_val)
                    y = int(yval)
                    x = int(xval)
    return _ncc, y, x


def calculate_translation(image1, image2, lims):
    PCM = pcm(image1, image2)
    yins, xins, _ = multi_peak_max(PCM)
    max_peak = interpret_translation(image1, image2, yins, xins, *lims[0], *lims[1])
    return max_peak
