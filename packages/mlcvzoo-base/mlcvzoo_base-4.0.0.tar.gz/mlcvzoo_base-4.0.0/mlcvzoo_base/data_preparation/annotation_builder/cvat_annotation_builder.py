# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for building CVAT formatted annotations."""
import logging
import os
from typing import List, Tuple

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_builder import AnnotationBuilder
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.segmentation import Segmentation
from mlcvzoo_base.data_preparation.utils import ensure_abspath

logger = logging.getLogger(__name__)


class CVATAnnotationBuilder(AnnotationBuilder):
    """
    Super class for defining the methods that are needed to build a BaseAnnotation
    object from a CVAT type XML file.
    """

    def __init__(
        self,
        image_shape: Tuple[int, int],
        input_classifications: List[Classification],
        input_bounding_boxes: List[BoundingBox],
        input_segmentations: List[Segmentation],
    ) -> None:
        AnnotationBuilder.__init__(self)

        self.image_shape = image_shape
        self.input_classifications = input_classifications
        self.input_bounding_boxes = input_bounding_boxes
        self.input_segmentations = input_segmentations

    def build(
        self,
        image_path: str,
        annotation_path: str,
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
    ) -> BaseAnnotation:

        annotation = BaseAnnotation(
            image_path=os.path.join(image_dir, image_path),
            annotation_path=os.path.join(annotation_dir, annotation_path),
            image_shape=self.image_shape,
            classifications=self.input_classifications,
            bounding_boxes=self.input_bounding_boxes,
            segmentations=self.input_segmentations,
            image_dir=image_dir,
            annotation_dir=annotation_dir,
            replacement_string=replacement_string,
        )

        try:
            AnnotationBuilder._check_annotation(annotation=annotation)
        except ValueError as value_error:
            logger.exception(
                f"{value_error}, in a future version, the whole annotation will be skipped!"
            )
        annotation = ensure_abspath(annotation=annotation)

        return annotation
