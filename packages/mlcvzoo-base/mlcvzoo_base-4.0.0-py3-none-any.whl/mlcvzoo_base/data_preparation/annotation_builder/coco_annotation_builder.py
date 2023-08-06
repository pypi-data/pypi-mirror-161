# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for building COCO formatted annotations."""

import logging
from typing import Any, Dict, List, Tuple, cast

import numpy as np

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_builder import AnnotationBuilder
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.segmentation import PolygonType, Segmentation
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.data_preparation.utils import ensure_abspath
from mlcvzoo_base.third_party.imutils.perspective import order_points

logger = logging.getLogger(__name__)


class COCOAnnotationBuilder(AnnotationBuilder):
    """
    Super class for defining the methods that are needed to build a BaseAnnotation
    object from a COCO type XML file.
    """

    def __init__(
        self,
        image_shape: Tuple[int, int],  # HEIGHT, WIDTH
        image_id: str,
        coco_annotations: List[Dict[str, Any]],
        coco_categories: List[Dict[str, Any]],
        mapper: AnnotationClassMapper,
        use_difficult: bool,
    ) -> None:
        AnnotationBuilder.__init__(self)

        self.image_shape = image_shape
        self.image_id = image_id
        self.coco_annotations = coco_annotations
        self.mapper = mapper

        self.coco_classes_id_dict: Dict[int, str] = self.mapper.get_coco_classes_id_dict(
            categories=coco_categories
        )

        self.use_difficult = use_difficult

    def build(
        self,
        image_path: str,
        annotation_path: str,
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
    ) -> BaseAnnotation:

        bounding_boxes, segmentations = self.__get_coco_annotations()

        annotation: BaseAnnotation = BaseAnnotation(
            image_path=image_path,
            annotation_path=annotation_path,
            image_shape=self.image_shape,
            classifications=[],
            bounding_boxes=bounding_boxes,
            segmentations=segmentations,
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

    @staticmethod
    def __get_attributes_from_coco_annotation(
        coco_annotation: Dict[str, Any]
    ) -> Tuple[bool, bool, str]:
        """
        Sets multiple attributes which characterize the corresponding bounding box

        Args:
            coco_annotation: Dict containing information about the bounding box

        Returns:
            Tuple containing three attributes

        """

        if "attributes" in coco_annotation:
            attributes = coco_annotation["attributes"]

            difficult = attributes["difficult"] if "difficult" in attributes else False
            occluded = attributes["occluded"] if "occluded" in attributes else False
            content = attributes["content"] if "content" in attributes else ""
        else:
            difficult = False
            occluded = False
            content = ""

        return difficult, occluded, content

    @staticmethod
    def __create_polygon_from_coco_polygon(
        coco_polygon: List[List[float]],
    ) -> PolygonType:
        """
        Converts a polygon given from an annotation file in COCO formats
        to a MLCVZoo conform polygon of type PolygonType

        Args:
            coco_polygon: Polygon in COCO format

        Returns:
            Polygon of PolygonType
        """

        main_coco_polygon: List[float] = coco_polygon[0]

        polygon_tuple_list: PolygonType = []
        for index in range(0, len(main_coco_polygon), 2):
            new_point = (main_coco_polygon[index], main_coco_polygon[index + 1])
            polygon_tuple_list.append(new_point)

        if len(polygon_tuple_list) == 4:
            polygon_tuple_list = [
                cast(Tuple[float, float], tuple(point))
                for point in order_points(
                    polygon=np.array(polygon_tuple_list, dtype="float32"),
                    sort_by_euclidean=False,
                )
            ]

        return polygon_tuple_list

    def __get_coco_annotations(
        self,
    ) -> Tuple[List[BoundingBox], List[Segmentation]]:
        """
        Documentation regarding the COCO format can be found here:
        https://cocodataset.org/#format-data

        """

        _bounding_boxes: List[BoundingBox] = list()
        _segmentations: List[Segmentation] = list()

        for _coco_annotation in self.coco_annotations:
            if _coco_annotation["image_id"] != self.image_id:
                continue

            # Get the coco class name based on the given coco category_id
            coco_class_name = self.coco_classes_id_dict[int(_coco_annotation["category_id"])]

            try:
                # map the parsed "class_name" according to the mapping defined in the mapper class
                class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                    class_name=coco_class_name
                )

                class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                    class_name=coco_class_name
                )
            except ClassMappingNotFoundError:
                logger.warning(
                    "Could not find a valid class-mapping for class-name '%s'. "
                    "BndBox will be skipped, coco-annotation= '%s'"
                    % (coco_class_name, _coco_annotation)
                )
                continue

            (
                difficult,
                occluded,
                content,
            ) = self.__get_attributes_from_coco_annotation(coco_annotation=_coco_annotation)

            box = Box.init_format_based(
                box_list=_coco_annotation["bbox"],
                box_format=ObjectDetectionBBoxFormats.XYWH,
                src_shape=self.image_shape,
            )

            # NOTE: COCO bbox is format XYWH
            bounding_box = BoundingBox(
                class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                model_class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                score=0.0,
                difficult=difficult,
                occluded=occluded,
                content=content,
                box=box,
            )

            # TODO: handle occluded as well?
            if difficult and not self.use_difficult:
                logger.debug("Found difficult box, which will be skipped! %s", bounding_box)
                continue

            coco_polygon = _coco_annotation["segmentation"]
            if len(coco_polygon) > 0:

                polygon = self.__create_polygon_from_coco_polygon(coco_polygon=coco_polygon)

                segmentation = Segmentation(
                    class_identifier=ClassIdentifier(
                        class_id=class_id,
                        class_name=class_name,
                    ),
                    model_class_identifier=ClassIdentifier(
                        class_id=class_id,
                        class_name=class_name,
                    ),
                    score=0.0,
                    difficult=difficult,
                    occluded=occluded,
                    content=content,
                    polygon=polygon,
                    box=box,
                )

                # Append segmentation given with surrounding box
                _segmentations.append(segmentation)
            else:
                # No segmentation given. The bounding-box is a real bounding-box.
                _bounding_boxes.append(bounding_box)

        return _bounding_boxes, _segmentations
