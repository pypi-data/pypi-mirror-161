# --------------------------------------------------------
# Copyright (c) 2019 Toan Dao Minh(bigkizd)
# Licensed under The MIT License [see LICENSE for details]
# --------------------------------------------------------

"""
This module is used to source out a metric computing utility, which
is taken from https://github.com/toandaominh1997/EfficientDet.Pytorch
"""

from typing import Any

import numpy as np


def compute_overlap(boxes: np.ndarray, query_boxes: np.ndarray) -> Any:  # type: ignore[type-arg]
    """
    Compute overlap between predicted boxes and query_boxes

    Code originally from

    https://github.com/toandaominh1997/EfficientDet.Pytorch/
    blob/fbe56e58c9a2749520303d2d380427e5f01305ba/eval.py#L19-L46

    Args:
        boxes: (N, 4) ndarray of float
        query_boxes: (K, 4) ndarray of float

    Returns
        (N, K) ndarray of overlap between predicted boxes and query_boxes
    """

    assert type(boxes) == np.ndarray
    assert type(query_boxes) == np.ndarray

    area = (query_boxes[:, 2] - query_boxes[:, 0]) * (query_boxes[:, 3] - query_boxes[:, 1])

    iw = np.minimum(np.expand_dims(boxes[:, 2], axis=1), query_boxes[:, 2]) - np.maximum(
        np.expand_dims(boxes[:, 0], 1), query_boxes[:, 0]
    )
    ih = np.minimum(np.expand_dims(boxes[:, 3], axis=1), query_boxes[:, 3]) - np.maximum(
        np.expand_dims(boxes[:, 1], 1), query_boxes[:, 1]
    )

    iw = np.maximum(iw, 0)
    ih = np.maximum(ih, 0)

    ua = (
        np.expand_dims((boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1]), axis=1)
        + area
        - iw * ih
    )

    ua = np.maximum(ua, np.finfo(float).eps)

    intersection = iw * ih

    # normally this is of type np.ndarray: TODO: solve mypy error
    return intersection / ua
