# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

""" Base class for image annotations """

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.segmentation import Segmentation
from mlcvzoo_base.data_preparation.structs import CSVOutputStringFormats

logger = logging.getLogger(__name__)


# TODO: Ensure annotations and contained coordinates are valid at any point in time
@dataclass
class BaseAnnotation:
    """
    An image annotation.
    """

    # Absolute file path to the image of the annotation (usually .jpg or .png
    image_path: str
    # Absolute file path for the annotation (usually .xml)
    annotation_path: str

    # shape of the image in the format (height, width)
    image_shape: Tuple[int, int]
    # List of classifications for this image. Can be used for training classification algorithms,
    # or to filter out images by their content.
    classifications: List[Classification] = field(default_factory=lambda: [])
    # List of bounding_boxes
    bounding_boxes: List[BoundingBox] = field(default_factory=lambda: [])
    # List of segmentations
    segmentations: List[Segmentation] = field(default_factory=lambda: [])

    image_dir: str = ""
    # TODO: rename to annotation_path_dir?
    #       When pascal-voc is used, the annotation_path_dir is a
    #       directory, when other formats are used,
    #       the annotation_path_dir is a path
    annotation_dir: str = ""
    replacement_string: str = ""

    def __repr__(self):  # type: ignore
        annotation_string = f"image_shape: {self.image_shape}\n"
        annotation_string += f"image-path: {self.image_path}\n"
        annotation_string += f"image-dir: {self.image_dir}\n"
        annotation_string += f"annotation-path: {self.annotation_path}\n"
        annotation_string += f"annotation-dir: {self.annotation_dir}\n"

        for classification in self.classifications:
            annotation_string += f"{classification}\n"

        for bounding_box in self.bounding_boxes:
            annotation_string += f"{bounding_box}\n"

        for segmentation in self.segmentations:
            annotation_string += f"{segmentation}\n"

        return annotation_string

    def __eq__(self, other):  # type: ignore

        if len(self.classifications) != len(other.classifications):
            return False
        if len(self.bounding_boxes) != len(other.bounding_boxes):
            return False
        if len(self.segmentations) != len(other.segmentations):
            return False

        for self_classification, other_classification in zip(
            self.classifications, other.classifications
        ):
            if self_classification != other_classification:
                return False

        for self_bounding_box, other_bounding_box in zip(
            self.bounding_boxes, other.bounding_boxes
        ):
            if self_bounding_box != other_bounding_box:
                return False

        for self_segmentation, other_segmentation in zip(self.segmentations, other.segmentations):
            if self_segmentation != other_segmentation:
                return False

        return True

    def get_height(self) -> int:
        """

        Returns:
            Height in pixels of the image for which the annotation is.

        """
        return int(self.image_shape[0])

    def get_width(self) -> int:
        """

        Returns:
            Width in pixels of the image for which the annotation is.

        """
        return int(self.image_shape[1])

    def get_bounding_boxes(self, include_segmentations: bool = True) -> List[BoundingBox]:
        """

        Args:
            include_segmentations (bool): Whether to return segmentations in the image

        Returns:
            list of BoundingBox objects. The bounding boxes (and segmentations) present
            in the image.

        """

        bounding_boxes: List[BoundingBox] = []

        bounding_boxes.extend([b for b in self.bounding_boxes if b.box is not None])

        if include_segmentations:
            bounding_boxes.extend(
                [s.to_bounding_box(self.image_shape) for s in self.segmentations]
            )

        return bounding_boxes

    def to_csv_entry(
        self,
        use_difficult: bool,
        use_occluded: bool,
        include_surrounding_bboxes: bool = True,
        output_string_format: str = CSVOutputStringFormats.BASE,
    ) -> Optional[str]:
        """
        Transforms the BaseAnnotation object to CSV format.

        Args:
            use_difficult (bool): Whether or not to consider the BaseAnnotation object if marked
            with 'difficult' flag
            use_occluded(bool): Whether or not to consider the BaseAnnotation object marked
            with 'occluded' flag
            include_surrounding_bboxes (bool): Whether or not to consider the BaseAnnotation
            object if it is a segmentation.
            output_string_format (str): One of CSVOutputStringFormats. Defines the format
            type of the resulting CSV string.

        Returns:
            String in CSV Format, Optional. Depending on the input parameters and format type
            the method either returns a CSV sting or None.

        """

        if output_string_format == CSVOutputStringFormats.BASE:
            csv_entry = self.__to_base_entry(
                use_difficult=use_difficult,
                use_occluded=use_occluded,
                include_segmentations=include_surrounding_bboxes,
            )
        elif output_string_format == CSVOutputStringFormats.YOLO:
            csv_entry = self.__to_yolo_entry(
                use_difficult=use_difficult,
                use_occluded=use_occluded,
                include_segmentations=include_surrounding_bboxes,
            )
        else:
            logger.warning(
                "Could not find a valid output_string_format. Given format: %s",
                output_string_format,
            )
            csv_entry = ""

        return csv_entry

    def __to_base_entry(
        self, use_difficult: bool, use_occluded: bool, include_segmentations: bool
    ) -> Optional[str]:

        csv_line = ""

        for bounding_box in self.get_bounding_boxes(include_segmentations=include_segmentations):
            if not use_occluded and bounding_box.occluded:
                logger.debug("Skip occluded bounding-box: %r", bounding_box)
                continue

            if not use_difficult and bounding_box.difficult:
                logger.debug("Skip difficult bounding-box: %r", bounding_box)
                continue

            if bounding_box.box is not None:
                is_valid_box = self.is_valid_bounding_box(box=bounding_box.box)
                if is_valid_box:
                    csv_line += "{},{},{},{},{} ".format(
                        bounding_box.box.xmin,
                        bounding_box.box.ymin,
                        bounding_box.box.xmax,
                        bounding_box.box.ymax,
                        bounding_box.class_name,
                    )
                else:
                    logger.warning(
                        "Skip bounding-box because it doesn't fulfill "
                        "the requirements check by is_valid_bounding_box: \n"
                        "   bounding-box: %s",
                        bounding_box,
                    )

        if csv_line != "":
            csv_entry: Optional[str] = "{} {} {} {}\n".format(
                self.image_path, self.image_shape[0], self.image_shape[1], csv_line
            )
        else:
            csv_entry = None

        return csv_entry

    def __to_yolo_entry(
        self, use_difficult: bool, use_occluded: bool, include_segmentations: bool
    ) -> Optional[str]:

        csv_line = ""

        for bounding_box in self.get_bounding_boxes(include_segmentations=include_segmentations):
            if not use_occluded and bounding_box.occluded:
                logger.debug("Skip occluded bounding-box: %s", bounding_box)
                continue

            if not use_difficult and bounding_box.difficult:
                logger.debug("Skip difficult bounding-box: %s", bounding_box)
                continue

            if bounding_box.box is not None:
                is_valid_box = self.is_valid_bounding_box(box=bounding_box.box)
                if is_valid_box:
                    csv_line += "{},{},{},{},{} ".format(
                        bounding_box.box.xmin,
                        bounding_box.box.ymin,
                        bounding_box.box.xmax,
                        bounding_box.box.ymax,
                        bounding_box.class_id,
                    )
                else:
                    logger.warning(
                        "Skip bounding-box because it doesn't fulfill "
                        "the requirements check by is_valid_bounding_box: \n"
                        "   bounding-box: %s",
                        bounding_box,
                    )

        if csv_line != "":
            csv_entry: Optional[str] = "{} {}\n".format(self.image_path, csv_line)
        else:
            csv_entry = None

        return csv_entry

    def is_valid_bounding_box(self, box: Box) -> bool:
        """

        Args:
            box: a Box object

        Returns:
            True if the coordinates of the Annotation are valid, else False.

        """

        bbox_has_valid_coordinates: bool = (
            (0 <= box.xmin <= self.get_width())
            and (0 <= box.xmax <= self.get_width())
            and (0 <= box.ymin <= self.get_height())
            and (0 <= box.ymax <= self.get_height())
            and (box.xmin < box.xmax)
            and (box.ymin < box.ymax)
        )

        return bbox_has_valid_coordinates

    def copy_annotation(
        self,
        classifications: Optional[List[Classification]] = None,
        bounding_boxes: Optional[List[BoundingBox]] = None,
        segmentations: Optional[List[Segmentation]] = None,
    ) -> BaseAnnotation:
        return BaseAnnotation(
            image_path=self.image_path,
            annotation_path=self.image_path,
            image_shape=self.image_shape,
            classifications=classifications
            if classifications is not None
            else self.classifications,
            bounding_boxes=bounding_boxes if bounding_boxes is not None else self.bounding_boxes,
            segmentations=segmentations if segmentations is not None else self.segmentations,
            image_dir=self.image_dir,
            annotation_dir=self.annotation_dir,
            replacement_string=self.replacement_string,
        )
