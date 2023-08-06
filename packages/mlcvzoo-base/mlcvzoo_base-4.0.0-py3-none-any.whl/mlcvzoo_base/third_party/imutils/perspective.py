# --------------------------------------------------------
# Copyright (c) 2015-2016 Adrian Rosebrock
# Licensed under The MIT License [see LICENSE.txt for details]
# author:    Adrian Rosebrock
# website:   http://www.pyimagesearch.com
# --------------------------------------------------------
"""
Module for implementations taken from third party package 'imutils'
https://github.com/PyImageSearch/imutils
"""
import numpy as np
from scipy.spatial import distance as dist


def order_points(polygon: np.ndarray, sort_by_euclidean: bool = True) -> np.ndarray:  # type: ignore[type-arg]
    """
    Orders points of the given polygon in the order:
    [top left, top right, bottom right, bottom left]

    Base of the code taken from:
    https://github.com/PyImageSearch/imutils/blob/
    c12f15391fcc945d0d644b85194b8c044a392e0a/imutils/perspective.py#L9-L34

    Args:
        polygon: a Numpy array, containing polygon defining edge points
        sort_by_euclidean: Whether or not to sort the rightMost points by using the
                           euclidean distance between points

    Returns:
        A Numpy array, a permuted version of the input array entries
    """

    # sort the points based on their x-coordinates
    sorted_polygon = polygon[np.argsort(polygon[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-coordinate points
    leftMost = sorted_polygon[:2, :]
    rightMost = sorted_polygon[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # NOTE: the sorting on the basis of the euclidean distance does not work
    #       in all cases. That is the reason why we duplicated this method to
    #       the MLCVZoo.
    # TODO: add a pull request in https://github.com/PyImageSearch/imutils
    if sort_by_euclidean:
        # now that we have the top-left coordinate, use it as an
        # anchor to calculate the Euclidean distance between the
        # top-left and right-most points; by the Pythagorean
        # theorem, the point with the largest distance will be
        # our bottom-right point
        D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
        (br, tr) = rightMost[np.argsort(D)[::-1], :]
    else:
        # now, sort the right-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        (tr, br) = rightMost

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")
