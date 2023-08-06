# Copyright 2022 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for evaluating currently trained model checkpoints"""

import logging
from typing import Dict, List

from tqdm import tqdm

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.model import ConfigurationType, DataType, ObjectDetectionModel
from mlcvzoo_base.evaluation.object_detection.data_classes import (
    ODModelEvaluationMetrics,
)
from mlcvzoo_base.evaluation.object_detection.metrics_computation import (
    MetricsComputation,
)

logger = logging.getLogger(__name__)


def evaluate_with_model(
    gt_annotations: List[BaseAnnotation],
    iou_thresholds: List[float],
    model: ObjectDetectionModel[ConfigurationType, DataType],
) -> ODModelEvaluationMetrics:
    """
    Compute the metric for the given object detection model. The evaluation is performed
    on the basis of the given ground truth annotations.

    Args:
        model: The model that should be evaluated
        gt_annotations: ground truth annotations where the model should be evaluated on
        iou_thresholds: List of thresholds for which a metrics should be computed

    Returns:
        The computed object detection metrics for this model
    """

    predicted_bounding_boxes_list: List[List[BoundingBox]] = []

    process_bar = tqdm(
        gt_annotations,
        desc=f"Compute metrics",
    )

    for index, gt_annotation in enumerate(process_bar):

        # Every ObjectDetectionModel returns bounding boxes
        _, predicted_bounding_boxes = model.predict(data_item=gt_annotation.image_path)

        predicted_bounding_boxes_list.append(predicted_bounding_boxes)

    return MetricsComputation(
        model_specifier=model.get_name(),
        classes_id_dict=model.get_classes_id_dict(),
        iou_thresholds=iou_thresholds,
        gt_annotations=gt_annotations,
        predicted_bounding_boxes_list=predicted_bounding_boxes_list,
    ).compute_metrics()


def evaluate_with_precomputed_data(
    model_specifier: str,
    classes_id_dict: Dict[int, str],
    gt_annotations: List[BaseAnnotation],
    iou_thresholds: List[float],
    predicted_bounding_boxes_list: List[List[BoundingBox]],
) -> ODModelEvaluationMetrics:
    """
    Compute the object detection metrics taking precomputed (predicted) bounding boxes and
    ground truth annotations.

    IMPORTANT REMARK: The index of the lists 'ground_truth_annotations'
                      and 'predicted_bounding_boxes_list' have to match exactly. This means
                      index 0 indicates the ground truth data and predicted bounding boxes
                      for image 0.

    Args:
        model_specifier: A string to indicate with which model the precomputed bounding boxes
                         have been predicted
        classes_id_dict: A dictionary that defines the mapping of class ids to class names for
                         this evaluation
        gt_annotations: The ground truth data as basis for the evaluation
        iou_thresholds: List of thresholds for which a metrics should be computed
        predicted_bounding_boxes_list: A list containing the predicted bounding boxes for each
                                       image of ground truth data


    Returns:
        The computed object detection metrics
    """

    return MetricsComputation(
        model_specifier=model_specifier,
        classes_id_dict=classes_id_dict,
        iou_thresholds=iou_thresholds,
        gt_annotations=gt_annotations,
        predicted_bounding_boxes_list=predicted_bounding_boxes_list,
    ).compute_metrics()
