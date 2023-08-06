# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

""" Class for Segmentation (polygon areas) annotations"""
from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Type

import cv2
import numpy as np

from mlcvzoo_base.api.data.annotation_attributes import AnnotationAttributes
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.third_party.imutils.perspective import order_points

PointType = Tuple[float, float]  # a point defined as (x, y)
PolygonType = List[PointType]


class Segmentation(AnnotationAttributes, Classification):
    """
    A class for defining the data object consumed by Segmentation models.
    It is mainly described by its polygon (list of 2D points) attribute.
    The polygon captures an area of the image, that is defined by the
    inner of the linear connected points of the polygon and is associated
    with a certain class.
    In addition, a segmentation CAN have an attribute "box" that defines the rectangle
    which encloses the area of the polygon.
    """

    def __init__(
        self,
        polygon: PolygonType,
        class_identifier: ClassIdentifier,
        score: float,
        difficult: bool,
        occluded: bool,
        content: str,
        box: Optional[Box] = None,
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
        self.__polygon: PolygonType = polygon
        self.__box: Optional[Box] = box

    @property
    def polygon(self) -> PolygonType:
        return self.__polygon

    @property
    def box(self) -> Optional[Box]:
        return self.__box

    def __eq__(self, other: Segmentation):  # type: ignore
        # NOTE: Since floats may very for different systems, don't check the score for equality,
        #       but allow it to be in a reasonable range
        basic_compare: bool = (
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

        polygon_compare = True

        if len(self.polygon) == len(other.polygon):
            for polygon_point, other_polygon_point in zip(self.polygon, other.polygon):
                point_equal = (
                    polygon_point[0] == other_polygon_point[0]
                    and polygon_point[1] == other_polygon_point[1]
                )

                if point_equal:
                    polygon_compare = polygon_compare and point_equal
                else:
                    polygon_compare = False
                    break
        else:
            polygon_compare = False

        return basic_compare and polygon_compare

    def __repr__(self):  # type: ignore
        return (
            f"Segmentation("
            f"class-id={self.class_id}, "
            f"class-name={self.class_name}: "
            f"model-class-id={self.model_class_identifier.class_id}, "
            f"model-class-name={self.model_class_identifier.class_name}: "
            f"Box={self.box}, "
            f"Polygon={self.polygon}, "
            f"score={self.score}, "
            f"difficult={self.difficult}, "
            f"occluded={self.occluded}, "
            f"content='{self.content}')"
        )

    def to_bounding_box(self, image_shape: Optional[Tuple[int, int]] = None) -> BoundingBox:
        """
        Manually build the bounding box object which covers the rectangular area
        that is defined by the polygon attribute

        Returns: a Bounding Box version of Segmentation

        """

        return BoundingBox(
            class_identifier=self.class_identifier,
            model_class_identifier=self.model_class_identifier,
            score=self.score,
            box=self.get_box(image_shape=image_shape),
            difficult=self.difficult,
            occluded=self.occluded,
            content=self.content,
        )

    def to_list(self, dst_type: Type[Any] = int) -> List[List[float]]:
        """
        Produce an encapsulated list of polygon points
        [[x0, y0, x1, y1, ..., xn, yn]]

        Args:
            dst_type: destination type to transform the data to

        Returns:
            the produced list
        """

        polygon_list: List[float] = []

        for polygon_tuple in self.polygon:
            polygon_list.append(dst_type(polygon_tuple[0]))
            polygon_list.append(dst_type(polygon_tuple[1]))

        return [polygon_list]

    def to_points_string(self) -> str:
        """

        Returns: Sting, concatenation of the coordinates of polygon attribute

        """

        points_string = ""
        for i, point in enumerate(self.polygon):
            if i < len(self.polygon) - 1:
                points_string = (
                    points_string + str(float(point[0])) + "," + str(float(point[1])) + ";"
                )
            else:
                points_string = points_string + str(float(point[0])) + "," + str(float(point[1]))

        return points_string

    def get_box(self, image_shape: Optional[Tuple[int, int]] = None) -> Box:
        """

        Returns: Box object that holds information about bounding box coordinates

        """
        if self.box is not None:
            return self.box
        else:
            return Segmentation.polygon_to_box(polygon=self.polygon, image_shape=image_shape)

    @staticmethod
    def polygon_to_box(polygon: PolygonType, image_shape: Optional[Tuple[int, int]] = None) -> Box:
        """
        Produce a box object that covers the minimal rectangular area which is
        covered by the given polygon

        Args:
            polygon: PolygonType, a list of points that form the polygon
            image_shape: shape of the image for which the bounding box should
                         be created

        Returns:
            A Box that holds the coordinates of the bounding rectangle of the polygon
        """
        return Box.init_format_based(
            box_format=ObjectDetectionBBoxFormats.XYWH,
            box_list=(cv2.boundingRect(np.array(polygon).astype(int))),
            src_shape=image_shape,
        )

    def to_rect_polygon(self) -> None:
        """
        Transform a polygon

        Returns:
            A PolygonType (an ordered list of PointType) that define rectangle
            around the original polygon

        """
        np_sorted_rect_polygon = Segmentation.__polygon_to_sorted_rect_polygon(
            np_polygon=np.array(self.polygon)
        )

        # TODO: limit point coordinates to image-size -1.0 ?
        self.__polygon = [(point[0], point[1]) for point in np_sorted_rect_polygon]

    @staticmethod
    def __polygon_to_sorted_rect_polygon(np_polygon: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
        """
        Calculates the minimum area around a given numpy array of polygons.
        The input format is nx2 =>  [(x, y), (x, y), ...].
        The output will be a numpy array out of 4 polygon-points => 4x2,
        which define the rect around the original polygon
        """

        min_area_rect = cv2.minAreaRect(np_polygon.astype(int))
        box = order_points(polygon=cv2.boxPoints(min_area_rect), sort_by_euclidean=False)
        return np.int0(box).astype(np.float32)  # type: ignore[return-value]

    def copy_segmentation(self, class_identifier: ClassIdentifier) -> Segmentation:
        return Segmentation(
            polygon=self.polygon,
            class_identifier=class_identifier,
            score=self.score,
            difficult=self.difficult,
            occluded=self.occluded,
            content=self.content,
            box=self.box,
            model_class_identifier=self.model_class_identifier,
        )
