# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for different utility operations during object detection evaluation"""

import logging
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from terminaltables import AsciiTable

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.evaluation.object_detection.data_classes import (
    CONFUSION_MATRIX_TYPE,
    METRIC_DICT_TYPE,
)
from mlcvzoo_base.evaluation.object_detection.structs import BBoxSizeTypes, MetricTypes
from mlcvzoo_base.third_party.efficientdet_pytorch.computer_overlap import (
    compute_overlap,
)

logger = logging.getLogger(__name__)


def get_bbox_size_type(box: Box, image_shape: Tuple[int, int] = (1080, 1440)) -> str:
    """
    Args:
        box: Box object
        image_shape: Tuple of ints, describing the image shape

    Returns:
        a String, the category of the size of the box (small, medium or large)
    """

    bbox_height = (int(box.ymax) - int(box.ymin)) / image_shape[0] * 480
    bbox_width = (int(box.xmax) - int(box.xmin)) / image_shape[1] * 640

    bbox_sqrt_area = math.sqrt(bbox_height * bbox_width)

    small_sqrt_area_limit = 32
    large_sqrt_area_limit = 96

    if bbox_sqrt_area <= small_sqrt_area_limit:
        return str(BBoxSizeTypes.BBOX_SMALL)

    elif small_sqrt_area_limit < bbox_sqrt_area <= large_sqrt_area_limit:
        return str(BBoxSizeTypes.BBOX_MEDIUM)

    else:
        # Any other case is bbox_sqrt_area > large_sqrt_area_limit:
        return str(BBoxSizeTypes.BBOX_LARGE)


def compute_max_bounding_box(
    bounding_box: BoundingBox, gt_bounding_boxes: List[BoundingBox]
) -> Tuple[float, BoundingBox]:
    """
    Determine the ground truth bounding box that has the highest overlap with
    the given (predicted) bounding box

    Args:
        bounding_box: BoundingBox object
        gt_bounding_boxes: List of BoundingBox objects

    Returns:
        A Tuple containing the ground truth bounding box wit the highest overlap and the
        according maximum overlap score (IOU metric)
    """

    gt_bboxes = []
    for gt_bounding_box in gt_bounding_boxes:
        gt_bboxes.append(gt_bounding_box.box.to_list(dst_type=float))

    # Compute Overlap between box and all gt annotations
    # Result in an overlap 2D array of shape (1, K)
    overlaps = compute_overlap(
        np.expand_dims(bounding_box.box.to_list(dst_type=float), axis=0),
        np.asarray(gt_bboxes),
    )
    # get the index of the gt box with the highest overlap (alongside the correct axis)
    max_gt_bbox_index = int(np.argmax(overlaps, axis=1))

    # 0 as index of the first element of 2D-array of shape (1, K)
    max_overlap = float(overlaps[0, max_gt_bbox_index])

    assigned_gt_bounding_box = gt_bounding_boxes[max_gt_bbox_index]

    return max_overlap, assigned_gt_bounding_box


def update_annotation_data(
    classes_id_dict: Dict[int, str],
    all_annotations: List[List[List[BaseAnnotation]]],
    index: int,
    new_annotation: BaseAnnotation,
) -> List[List[List[BaseAnnotation]]]:
    """
    Updates annotation information in the given 'all_annotations' list at the given index.

    Args:
        classes_id_dict: Dictionary of int to String, a class id to name mapping
        all_annotations: stacked List of BaseAnnotations, containing all annotations
        index: int, index of entry (image) which annotations should be updated
        new_annotation: BaseAnnotation object, holding the new annotation information

    Returns: stacked List of BaseAnnotations, the updated list

    """
    if not 0 <= index < len(all_annotations):
        logger.debug("WARNING: Index '%s' out of range for all_annotations!", index)
        return all_annotations

    if len(new_annotation.get_bounding_boxes(include_segmentations=True)) > 0:

        # Gather (BoundingBox / Annotation) data for each class-id.
        # This is needed to be able to compute detailed metrics
        # for each class-id.
        for class_id, class_name in classes_id_dict.items():

            # TODO: do we want to add the option to filter for specific class_names?
            if not 0 <= class_id < len(all_annotations[index]):
                logger.debug(
                    "WARNING: Class-ID '%s' out of range for all_annotations[%s]!",
                    class_id,
                    index,
                )
                continue

            # Have to find all bounding-boxes for a specific class-id.
            # In order to have access to the information about the image-path,
            # we need to store an annotation object, rather than a single bounding-box.
            # Despite the fact that for the metric calculation itself the bounding-box
            # information is enough.
            # For purposes like: draw/log all false-positive bounding-boxes for specific
            # images we need to have the information about the image-path
            #   => therefore use BaseAnnotation and not BoundingBox alone
            all_annotations[index][class_id] = []
            for b in new_annotation.get_bounding_boxes(include_segmentations=True):
                if b.class_id == class_id:
                    all_annotations[index][class_id].append(
                        BaseAnnotation(
                            image_path=new_annotation.image_path,
                            annotation_path=new_annotation.annotation_path,
                            image_shape=new_annotation.image_shape,
                            classifications=[],
                            bounding_boxes=[
                                BoundingBox(
                                    class_identifier=b.class_identifier,
                                    model_class_identifier=b.model_class_identifier,
                                    score=b.score,
                                    box=b.box,
                                    difficult=False,
                                    occluded=False,
                                    content="",
                                )
                            ],
                            segmentations=[],
                            image_dir=new_annotation.image_dir,
                            annotation_dir=new_annotation.annotation_dir,
                            replacement_string=new_annotation.replacement_string,
                        )
                    )
    else:
        logger.debug(
            "WARNING: The new_annotation for image %s does not contain "
            "any bounding-boxes! new_annotation: %s",
            new_annotation.image_path,
            new_annotation,
        )

    return all_annotations


def generate_metric_table(
    metrics_dict: METRIC_DICT_TYPE, iou_threshold: float, reduced: bool = False
) -> AsciiTable:
    """
    Generate a 'AsciiTable' object filled with the metrics of a object detection evaluation.
    The columns display the attributes of dataclass
    the mlcvzoo.evaluation.object_detection.data_classes.ODMetrics.

    Args:
        metrics_dict: The dictionary containing the metrics that should be formed into a table
        iou_threshold: The iou-threshold for which the table should be generated
        reduced: Whether to use all available metrics, or only the basic ones

    Returns:
        The generated 'AsciiTable'
    """

    table_data = [
        [
            f"{'class':15s}",
            f"{'TP':6s}",
            f"{'FP':6s}",
            f"{'FN':6s}",
            f"{'CP':6s}",
            f"{'Recall':10s}",
            f"{'Precision':10s}",
            f"{'F1':10s}",
            f"{'AP':8s}",
        ]
    ]
    row_data: List[Any]
    for bbox_size_type in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):

        if bbox_size_type != BBoxSizeTypes.BBOX_ALL:
            row_data = [f"SIZE: {bbox_size_type}", "", "", "", "", "", ""]
            table_data.append(row_data)

        for class_name, od_metric in metrics_dict[iou_threshold][bbox_size_type].items():
            if od_metric.COUNT > 0:
                row_data = [
                    class_name,
                    f"{od_metric.TP}",
                    f"{od_metric.FP}",
                    f"{od_metric.FN}",
                    f"{od_metric.COUNT}",
                    f"{od_metric.RC:.4f}",
                    f"{od_metric.PR:.4f}",
                    f"{od_metric.F1:.4f}",
                    f"{od_metric.AP:.4f}",
                ]
            else:
                row_data = [
                    class_name,
                    0,
                    0,
                    0,
                    0,
                    f"{0.0:.4f}",
                    f"{0.0:.4f}",
                    f"{0.0:.4f}",
                    f"{0.0:.4f}",
                ]

            table_data.append(row_data)

        if bbox_size_type != "l":
            row_data = ["", "", "", "", "", "", ""]
            table_data.append(row_data)

    table = AsciiTable(table_data)
    table.inner_footing_row_border = False

    return table


def generate_fn_fp_confusion_matrix_table(
    confusion_matrix: CONFUSION_MATRIX_TYPE, classes_id_dict: Dict[int, str]
) -> AsciiTable:
    """
    Generate a 'AsciiTable' object that represents the confusion matrix
    of an objection detection evaluation output. The confusion matrix indicates
    which false negative bounding boxes of a certain class could be matches to
    false positive bounding boxes of another class.

    Args:
        confusion_matrix: The confusion Matrix as 2D List
        classes_id_dict: Dictionary that matches the class IDs in the confusion matrix
                         to class names

    Returns:
        The generated 'AsciiTable'
    """

    table_data = [[""]]

    for class_id in range(0, len(confusion_matrix)):
        table_data[0].append(classes_id_dict[class_id])

    row_data: List[Any]
    for row_index in range(0, len(confusion_matrix)):
        row_data = [classes_id_dict[row_index]]
        for column_index in range(0, len(confusion_matrix)):
            row_data.append(f"{confusion_matrix[row_index][column_index]}")
        table_data.append(row_data)

    table = AsciiTable(table_data)
    table.inner_footing_row_border = False

    return table


def __draw_annotation_on_tf_image(
    img: np.ndarray,  # type: ignore[type-arg]
    annotation: BaseAnnotation,
    metric_type: str,
    color: Tuple[int, int, int],
    thickness: int,
) -> None:

    height, width, _ = img.shape

    for bounding_box in annotation.get_bounding_boxes(include_segmentations=True):
        cv2.rectangle(
            img,
            (bounding_box.box.xmin, bounding_box.box.ymin),
            (bounding_box.box.xmax, bounding_box.box.ymax),
            color,
            thickness,
        )

        if metric_type == MetricTypes.GROUND_TRUTH:
            org = (bounding_box.box.xmin, bounding_box.box.ymin)
        else:
            org = (
                bounding_box.box.xmin,
                min(bounding_box.box.ymax, height) - 10,
            )

        cv2.putText(
            img=img,
            text=f"{metric_type}_{bounding_box.class_name}",
            org=org,
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=2.0,
            color=color,
            thickness=2,
        )


def generate_img_id_map(
    image_path: str, img_directory_id_dict: Dict[str, int]
) -> Tuple[int, Dict[str, int]]:
    """
    Generates an index (id) for the given image_path.

    Args:
        image_path: String, path to an image
        img_directory_id_dict: Dictionary of image paths to index in directory list

    Returns: a Tuple of image index and (updated) img_directory_id_dict
    """
    # TODO: What happens when two images get the same index?
    #  It could be possible that due to an extension of the dict two images could get the same index,
    #  because the indices after the added and sorted image are increased by 1.
    #  Therefore all other entries of the subsequent images (in sorted order) are wrong.

    image_dir = os.path.dirname(image_path)
    file_extension = os.path.splitext(image_path)[1]

    if image_path not in img_directory_id_dict:
        path_generator = Path(image_dir).glob(f"**/*{file_extension}")

        file_list = [str(p) for p in path_generator]

        file_list.sort()

        for index, file_path in enumerate(file_list):
            img_directory_id_dict[file_path] = index

    return img_directory_id_dict[image_path], img_directory_id_dict
