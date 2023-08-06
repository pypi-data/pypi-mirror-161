# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

""" Class for Bounding Box Annotation"""

from __future__ import annotations

import math
from typing import List, Optional

from mlcvzoo_base.api.data.annotation_attributes import AnnotationAttributes
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification


class BoundingBox(AnnotationAttributes, Classification):
    """
    A class for defining the data object consumed by ObjectDetection models.
    It is mainly described by the box attribute, which covers an rectangular
    area of an image and is associated with a certain class
    """

    def __init__(
        self,
        box: Box,
        class_identifier: ClassIdentifier,
        score: float,
        difficult: bool,
        occluded: bool,
        content: str,
        model_class_identifier: Optional[ClassIdentifier] = None,
    ):
        Classification.__init__(
            self,
            class_identifier=class_identifier,
            model_class_identifier=model_class_identifier,
            score=score,
        )
        AnnotationAttributes.__init__(
            self, difficult=difficult, occluded=occluded, content=content
        )
        self.__box = box

    @property
    def box(self) -> Box:
        return self.__box

    def __eq__(self, other: BoundingBox):  # type: ignore
        # NOTE: Since floats may very for different systems, don't check the score for equality,
        #       but allow it to be in a reasonable range
        return (
            self.box == other.box
            and self.class_identifier.class_id == other.class_identifier.class_id
            and self.class_identifier.class_name == other.class_identifier.class_name
            and self.model_class_identifier.class_id == other.model_class_identifier.class_id
            and self.model_class_identifier.class_name == other.model_class_identifier.class_name
            and self.occluded == other.occluded
            and self.difficult == other.difficult
            and self.content == other.content
            and math.isclose(a=self.score, b=other.score, abs_tol=0.005)
        )

    def __repr__(self):  # type: ignore
        return (
            f"BoundingBox: "
            f"class-id={self.class_id}, "
            f"class-name={self.class_name}: "
            f"model-class-id={self.model_class_identifier.class_id}, "
            f"model-class-name={self.model_class_identifier.class_name}: "
            f"Box={self.box}, "
            f"score={self.score}, "
            f"difficult={self.difficult}, "
            f"occluded={self.occluded}, "
            f"content='{self.content}'"
        )

    def to_list(self) -> List[int]:
        """
        Transforms the BoundingBox object to a list of its coordinates.

        Returns:
            A 1x4 list of the objects coordinates [xmin, ymin, xmax, ymax]
        """
        return [self.box.xmin, self.box.ymin, self.box.xmax, self.box.ymax]

    def copy_bounding_box(self, class_identifier: ClassIdentifier) -> BoundingBox:
        return BoundingBox(
            box=self.box,
            class_identifier=class_identifier,
            score=self.score,
            difficult=self.difficult,
            occluded=self.occluded,
            content=self.content,
            model_class_identifier=self.model_class_identifier,
        )
