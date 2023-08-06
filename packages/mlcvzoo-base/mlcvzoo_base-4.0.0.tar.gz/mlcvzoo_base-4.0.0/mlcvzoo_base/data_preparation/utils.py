# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for different utility operations during data preparation
"""

import logging
import os
import xml.dom.minidom as mmd
import xml.etree.ElementTree as ET_xml
from typing import List, Optional

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.utils.file_utils import ensure_dir
from mlcvzoo_base.utils.implicit_path_replacements import ImplicitReplacement
from mlcvzoo_base.utils.xml_utils import create_bbox_xml_entry, create_xml_root

logger = logging.getLogger(__name__)


def replace_index_by_dir(annotation: BaseAnnotation) -> BaseAnnotation:
    """
    Replaces replacement_string parts in image_path and annotation_path attributes of
    an annotation by respective directory information (image_dir and annotation_dir)

    Args:
        annotation: BaseAnnotation object

    Returns: BaseAnnotation, the input object with different path attributes

    """

    if annotation.replacement_string is not None:
        # TODO: use directory replacement
        annotation.image_path = ImplicitReplacement.replace_string_in_path(
            file_path=annotation.image_path,
            value=annotation.replacement_string,
            replacement_value=annotation.image_dir,
            how=ImplicitReplacement.FIRST,
        )

        # TODO: use directory replacement
        annotation.annotation_path = ImplicitReplacement.replace_string_in_path(
            file_path=annotation.annotation_path,
            value=annotation.replacement_string,
            replacement_value=annotation.annotation_dir,
            how=ImplicitReplacement.FIRST,
        )

        return ensure_abspath(annotation=annotation)


def replace_dir_by_index(annotation: BaseAnnotation) -> BaseAnnotation:
    """
    Replaces directory parts (image_dir and annotation_dir) in image_path and
    annotation_path attributes of an annotation by replacement_string information

    Args:
        annotation: BaseAnnotation object

    Returns: BaseAnnotation, the input object with different path attributes

    """

    if annotation.replacement_string is not None:
        annotation.image_path = ImplicitReplacement.replace_string_in_path(
            file_path=annotation.image_path,
            value=annotation.image_dir,
            replacement_value=annotation.replacement_string,
            how=ImplicitReplacement.FIRST,
        )

        annotation.annotation_path = ImplicitReplacement.replace_string_in_path(
            file_path=annotation.annotation_path,
            value=annotation.annotation_dir,
            replacement_value=annotation.replacement_string,
            how=ImplicitReplacement.FIRST,
        )

    return annotation


def ensure_abspath(annotation: BaseAnnotation) -> BaseAnnotation:
    """
    Sets the given annotation's path and directory attributes to absolute paths

    Args:
        annotation: BaseAnnotation object

    Returns: BaseAnnotation, the input object with different path attributes

    """

    annotation.image_path = os.path.abspath(annotation.image_path)
    annotation.image_dir = os.path.abspath(annotation.image_dir)
    annotation.annotation_path = os.path.abspath(annotation.annotation_path)
    annotation.annotation_dir = os.path.abspath(annotation.annotation_dir)

    return annotation


def annotation_to_xml(
    annotation: BaseAnnotation,
    allowed_classes: Optional[List[str]] = None,
) -> None:
    """
    Transforms the given annotation object to XML format and saves it to
    a file at annotation_path location

    Args:
        annotation: BaseAnnotation object
        allowed_classes: Optional list of strings (allowed classes)

    Returns: None

    """

    root = create_xml_root(
        file_path=annotation.image_path,
        width=annotation.image_shape[0],
        height=annotation.image_shape[1],
    )

    assert annotation.image_shape[0] > 0
    assert annotation.image_shape[1] > 0

    if len(annotation.get_bounding_boxes(include_segmentations=True)) == 0:
        logger.warning("annotation has no bounding_boxes!")

    for bounding_box in annotation.get_bounding_boxes(include_segmentations=True):

        if allowed_classes is not None and bounding_box.class_name not in allowed_classes:
            continue

        root = create_bbox_xml_entry(
            root,
            bounding_box.class_name,
            bounding_box.box.xmin,
            bounding_box.box.ymin,
            bounding_box.box.xmax,
            bounding_box.box.ymax,
        )

    logger.info("Write xml file: %s", annotation.annotation_path)

    ensure_dir(file_path=annotation.annotation_path, verbose=True)

    tree_string = "".join(ET_xml.tostring(element=root).decode("utf-8").split())
    pretty_tree_string = mmd.parseString(tree_string).toprettyxml(
        indent="  ",
    )

    with open(file=annotation.annotation_path, mode="w", encoding="utf8") as annotation_file:
        annotation_file.write(pretty_tree_string)


def save_bbox_snippets(annotation: BaseAnnotation, output_dir: str) -> None:

    raise NotImplementedError("Currently not implemented!")
    # TODO:
    # image_path = self.image_path
    #
    # snippet_base_dir = os.path.join(
    #     output_dir,
    #     "snippets"
    # )
    #
    # for index, d in enumerate(self.bounding_boxes):
    #     snippet_name = os.path.basename(image_path)[:-4] + "_" + \
    #                    d.class_name + "_" + str(index) + os.path.basename(image_path)[-4:]
    #
    #     snippet_dir = os.path.join(snippet_base_dir, d.class_name)
    #
    #     if not os.path.exists(snippet_dir):
    #         os.makedirs(snippet_dir)
    #
    #         print("Create directory: {}".format(snippet_dir))
    #
    #     snippet_path = os.path.join(snippet_dir, snippet_name)
    #
    #     if not os.path.isfile(snippet_path):
    #         img = cv2.imread(image_path)
    #
    #         crop_img = img[d.box.ymin:d.box.ymax, d.box.xmin:d.box.xmax]
    #
    #         # NOTE: comment in to show image
    #         # cv2.imshow(snippet_name, crop_img)
    #         # cv2.waitKey(0)
    #
    #         print("Write snippet: {}".format(snippet_path))
    #         cv2.imwrite(snippet_path, crop_img)


def filter_annotation(
    annotation: BaseAnnotation,
    class_ids: Optional[List[int]] = None,
    class_names: Optional[List[str]] = None,
    classification_score: float = 0.0,
    bounding_box_score: float = 0.0,
    segmentation_score: float = 0.0,
) -> BaseAnnotation:
    """
    Filter a given annotation object. Afterwards the object only contains
    the classifications, bounding-boxes and segmentations that fulfill:

    - the class id matches one of the given ids given by 'class_ids' (only when the list is
      not None nor empty)
    - the class name matches one of the given names given by 'class_names' (only when the list is
      not None nor empty)
    - the score is higher than the one associated with this datastructure

    Args:
        annotation: the annotation object to filter
        class_ids: the class ids that are valid
        class_names: the class names that are valid
        classification_score: the score a any Classification object has to fulfill
        bounding_box_score: the score a any BoundingBox object has to fulfill
        segmentation_score: the score a any Segmentation object has to fulfill

    Returns:
        The filter annotation object
    """

    filtered_annotation: BaseAnnotation = BaseAnnotation(
        image_path=annotation.image_path,
        annotation_path=annotation.annotation_path,
        image_shape=annotation.image_shape,
        image_dir=annotation.image_dir,
        replacement_string=annotation.replacement_string,
        annotation_dir=annotation.annotation_dir,
        classifications=[],
        bounding_boxes=[],
        segmentations=[],
    )

    for classification in annotation.classifications:
        if (
            class_ids is not None
            and len(class_ids) > 0
            and classification.class_id not in class_ids
        ) or (
            class_names is not None
            and len(class_names) > 0
            and classification.class_name not in class_names
        ):
            continue

        if classification.score >= classification_score:
            filtered_annotation.classifications.append(classification)

    for bounding_box in annotation.bounding_boxes:
        if (
            class_ids is not None and len(class_ids) > 0 and bounding_box.class_id not in class_ids
        ) or (
            class_names is not None
            and len(class_names) > 0
            and bounding_box.class_name not in class_names
        ):
            continue

        if bounding_box.score >= bounding_box_score:
            filtered_annotation.bounding_boxes.append(bounding_box)

    for segmentation in annotation.segmentations:
        if (
            class_ids is not None and len(class_ids) > 0 and segmentation.class_id not in class_ids
        ) or (
            class_names is not None
            and len(class_names) > 0
            and segmentation.class_name not in class_names
        ):
            continue

        if segmentation.score >= segmentation_score:
            filtered_annotation.segmentations.append(segmentation)

    return filtered_annotation


def filter_annotations(
    annotations: List[BaseAnnotation],
    class_ids: Optional[List[int]] = None,
    class_names: Optional[List[str]] = None,
    classification_score: float = 0.0,
    bounding_box_score: float = 0.0,
    segmentation_score: float = 0.0,
) -> List[BaseAnnotation]:
    """
    Filter a given list of annotations. Afterwards each annotation only contains
    the classifications, bounding-boxes and segmentations that fulfill:

    - the class id matches one of the given ids given by 'class_ids' (only when the list is
      not None nor empty)
    - the class name matches one of the given names given by 'class_names' (only when the list is
      not None nor empty)
    - the score is higher than the one associated with this datastructure

    Args:
        annotations: the list of annotations to filter
        class_ids: the class ids that are valid
        class_names: the class names that are valid
        classification_score: the score a any Classification object has to fulfill
        bounding_box_score: the score a any BoundingBox object has to fulfill
        segmentation_score: the score a any Segmentation object has to fulfill

    Returns:
        The filtered list of annotations
    """

    filtered_annotations: List[BaseAnnotation] = []

    for annotation in annotations:

        filtered_annotations.append(
            filter_annotation(
                annotation=annotation,
                class_ids=class_ids,
                class_names=class_names,
                classification_score=classification_score,
                bounding_box_score=bounding_box_score,
                segmentation_score=segmentation_score,
            )
        )

    return filtered_annotations
