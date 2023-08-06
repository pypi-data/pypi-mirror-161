# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for storing data classes and complex type definitions that are used in the context of the
mlcvzoo_base.evaluation.object_detection package
"""

from dataclasses import dataclass, field
from typing import Dict, Final, List, Optional

import numpy as np

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.bounding_box import BoundingBox

# 3D List containing of the following:
#   1) One entry per data items / image
#   2) One entry per call of classes
#   3) One entry per annotation Annotations the matches the image (1) and the class (2)
# This is a list of BaseAnnotations in order to carry information about the image instead of just bounding boxes
EVALUATION_LIST_TYPE = List[List[List[BaseAnnotation]]]  # pylint: disable=invalid-name

CONFUSION_MATRIX_TYPE = List[List[int]]  # pylint: disable=invalid-name

DEFAULT_INT_VALUE: Final[int] = 0
DEFAULT_FLOAT_VALUE: Final[float] = 0.0


# NOTE: Since this are the main Object Detection metrics, it's okay to have more instance
#       attributes
@dataclass
class ODMetrics:  # pylint: disable=too-many-instance-attributes
    """
    Dataclass for storing the main metrics that are computed for object detection algorithms
    """

    # TODO: rename to lower case, disable pylint only temporary!
    TP: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name
    FP: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name
    FN: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name
    PR: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    RC: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    F1: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    AP: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    COUNT: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name

    def __repr__(self):  # type: ignore
        return (
            f"TP: {self.TP}, "
            f"FP: {self.FP}, "
            f"FN: {self.FN}, "
            f"PR: {self.PR}, "
            f"RC: {self.RC}, "
            f"F1: {self.F1}, "
            f"AP: {self.AP}, "
            f"COUNT: {self.COUNT}"
        )

    def __str__(self):  # type: ignore
        return self.__repr__()


# 1st key: iou-threshold
# 2nd key: type of the size of the bounding-box
# 3rd key: class-name
# value: The computed metrics
#
# Dict[IOU_THRESHOLD][BBoxSizeTypes.BBOX_SIZE_TYPE][CLASS_NAME] = ODMetrics
METRIC_DICT_TYPE = Dict[float, Dict[str, Dict[str, ODMetrics]]]  # pylint: disable=invalid-name


@dataclass
class MetricImageInfo:
    """
    Dataclass to store information about false positives and false negatives in the
    form of BaseAnnotation objects. This to have a exact relation between an image
    and the according false positive / false negative bounding boxes. The ground
    truth data is added to be able to visualize the expected bounding boxes.
    """

    ground_truth_annotation: Optional[BaseAnnotation] = None
    false_negative_annotation: Optional[BaseAnnotation] = None
    false_positive_annotation: Optional[BaseAnnotation] = None
    false_negative_matched_false_positive_annotation: Optional[BaseAnnotation] = None


# 1st key: class name
# 2nd key: image path
# value: The MetricImageInfo for this class name and image path
#
# Dict[CLASS_NAME][IMAGE_PATH] = MetricImageInfo
# Dict[IMAGE_PATH][CLASS_NAME] = MetricImageInfo
METRIC_IMAGE_INFO_TYPE = Dict[str, Dict[str, MetricImageInfo]]  # pylint: disable=invalid-name


@dataclass
class ODModelEvaluationMetrics:
    """
    Dataclass for storing the output of an object detection evaluation.
    The metrics_dict stores the actual computed metrics, while the metrics_image_info_dict
    stores debugging information to be able to analyze false positives and false negatives.

    The model_specifier indicates for which model the metrics have been computed.
    """

    model_specifier: str
    metrics_dict: METRIC_DICT_TYPE = field(default_factory=lambda: {})
    metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE = field(default_factory=lambda: {})


@dataclass
class ODEvaluationComputingData:
    """
    Dataclass for storing data structures that are needed to computed object detection metrics
    """

    # Dict[BBoxSizeTypes.BBOX_SIZE_TYPE][CLASS_NAME] = counter of ground truth data
    gt_counter_dict: Dict[str, Dict[str, int]] = field(default_factory=lambda: {})

    # Dict[IOU_THRESHOLD][CLASS_NAME] = Cumulative array indicating the false positives of the
    #                                   dataset
    false_positives_dict: Dict[float, Dict[str, np.ndarray]] = field(  # type: ignore[type-arg]
        default_factory=lambda: {}
    )

    # Dict[IOU_THRESHOLD][CLASS_NAME] = Cumulative array indicating the true positives of the
    #                                   dataset
    true_positives_dict: Dict[float, Dict[str, np.ndarray]] = field(  # type: ignore[type-arg]
        default_factory=lambda: {}
    )

    # Dict[IOU_THRESHOLD][CLASS_NAME] = Array indicating the score for each data item
    scores: Dict[float, Dict[str, np.ndarray]] = field(default_factory=lambda: {})  # type: ignore[type-arg]

    # Dict[IOU_THRESHOLD][CLASS_NAME] = List containing all bounding boxes for each data item
    detected_annotations: Dict[float, List[BoundingBox]] = field(default_factory=lambda: {})

    # Dict[IOU_THRESHOLD][BBoxSizeTypes.BBOX_SIZE_TYPE] = List indicating the AP metrics that have
    #                                                     been computed correctly
    valid_precisions: Dict[float, Dict[str, List[float]]] = field(default_factory=lambda: {})
