# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

""" Class for Bounding Box information"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats


class Box:
    """
    Class for storing bounding box information.

    Box on an Image:
    |-----------------------|
    |(xmin, ymin)           |
    |                       |
    |                       |
    |                       |
    |                       |
    |                       |
    |           (xmax, ymax)|
    |-----------------------|
    """

    def __init__(self, xmin: int, ymin: int, xmax: int, ymax: int):
        # top left x coordinate
        self.__xmin: int = xmin
        # top left y coordinate
        self.__ymin: int = ymin
        # lover right x coordinate
        self.__xmax: int = xmax
        # lower right y coordinate
        self.__ymax: int = ymax

    def __eq__(self, other: object) -> bool:

        if isinstance(other, Box):
            return (
                self.xmin == other.xmin
                and self.ymin == other.ymin
                and self.xmax == other.xmax
                and self.ymax == other.ymax
            )

        return False

    def __repr__(self):  # type: ignore
        return (
            f"Box("
            f"xmin={self.__xmin}, ymin={self.__ymin}, xmax={self.__xmax}, ymax={self.__ymax}"
            f")"
        )

    @property
    def xmin(self) -> int:
        return self.__xmin

    @property
    def ymin(self) -> int:
        return self.__ymin

    @property
    def xmax(self) -> int:
        return self.__xmax

    @property
    def ymax(self) -> int:
        return self.__ymax

    @staticmethod
    def init_format_based(
        box_format: str,
        box_list: Tuple[int, int, int, int],
        src_shape: Optional[Tuple[int, int]] = None,
        dst_shape: Optional[Tuple[int, int]] = None,
    ) -> Box:
        """
        Additional Constructor

        Args:
            box_format: specify the way for parsing the box argument
            box_list: object as 4D array containing bounding box information
            src_shape: shape of the original image as tuple (height, width)
            dst_shape: desired shape for creating the bounding boxes as tuple (height, width)

        Returns:
            A Box object

        """
        if box_format == ObjectDetectionBBoxFormats.XYWH:
            base_box = Box(
                xmin=int(box_list[0]),
                ymin=int(box_list[1]),
                xmax=int(box_list[0] + box_list[2]),
                ymax=int(box_list[1] + box_list[3]),
            )
        elif box_format == ObjectDetectionBBoxFormats.XYXY:
            base_box = Box(
                xmin=int(box_list[0]),
                ymin=int(box_list[1]),
                xmax=int(box_list[2]),
                ymax=int(box_list[3]),
            )
        else:
            valid_formats = ObjectDetectionBBoxFormats.get_values_as_list(
                class_type=ObjectDetectionBBoxFormats
            )
            raise ValueError(
                f"Format {box_format} is not supported. " f"Please provide any of {valid_formats}"
            )

        if src_shape is not None:
            base_box.clamp(shape=src_shape)

        if src_shape is not None and dst_shape is not None:
            base_box.scale(src_shape=src_shape, dst_shape=dst_shape)

        return base_box

    def to_list(self, dst_type: Any = int) -> List[Any]:
        """
        Args:
            dst_type: destination type to transform the data to

        Returns:
            List of transformed polygons
        """

        return [
            dst_type(self.xmin),
            dst_type(self.ymin),
            dst_type(self.xmax),
            dst_type(self.ymax),
        ]

    def clamp(self, shape: Tuple[int, int]) -> None:
        self.__xmin = int(max(0, self.__xmin))
        self.__ymin = int(max(0, self.__ymin))

        self.__ymax = int(min(shape[0] - 1, self.__ymax))
        self.__xmax = int(min(shape[1] - 1, self.__xmax))

    def scale(self, src_shape: Tuple[int, int], dst_shape: Tuple[int, int]) -> None:
        """
        Scale the Box according to the given shapes of the source and destination image

        Args:
            src_shape: shape of the original image as tuple (height, width)
            dst_shape: desired shape for creating the bounding boxes as tuple (height, width)

        Returns:
            None

        """
        if src_shape[0] < 0 or src_shape[1] < 0 or src_shape[0] > src_shape[1]:
            raise ValueError("Invalid source shape %s: ", src_shape)

        if dst_shape[0] < 0 or dst_shape[1] < 0 or dst_shape[0] > dst_shape[1]:
            raise ValueError("Invalid destination shape %s: ", dst_shape)

        height_scale_factor = dst_shape[0] / src_shape[0]
        width_scale_factor = dst_shape[1] / src_shape[1]

        self.__xmin = int(self.xmin * width_scale_factor)
        self.__xmax = int(self.xmax * width_scale_factor)

        self.__ymin = int(self.ymin * height_scale_factor)
        self.__ymax = int(self.ymax * height_scale_factor)

    def as_array(self) -> List[int]:
        """
        Transforms the Box object to a list of coordinates

        Returns: A List of coordinates in the order [xmin, ymin, xmax, ymax]
        """
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    def center(self) -> Tuple[float, float]:
        """
        Calculates the center coordinates of the Box

        Returns: A Tuple as the coordinates of the center
        """
        return (
            self.xmin + (self.xmax - self.xmin) * 0.5,
            self.ymin + (self.ymax - self.ymin) * 0.5,
        )

    def translation(self, x: int, y: int) -> None:
        """
        Shifts Box for x and y pixels in x and y direction respectively

        Args:
            x: int value for shift in x direction
            y: int value for shift in y direction

        Returns: None

        """
        self.__xmin += x
        self.__xmax += x
        self.__ymin += y
        self.__ymin += y

    def new_center(self, x: int, y: int) -> None:
        """
        Shifts the Box based on a new center coordinate. Scale of Box is kept.
        Args:
            x: int value, x coordinate of the new center
            y: int value, y coordinate of the new center

        Returns: None

        """
        width = self.xmax - self.xmin
        height = self.ymax - self.ymin

        self.__xmin = round(x - width / 2)
        self.__xmax = round(x + width / 2)
        self.__ymin = round(y - height / 2)
        self.__ymax = round(y + height / 2)
