# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for parsing CVAT formatted annotations"""
import logging
import xml.etree.ElementTree as ET_xml
from typing import List, Tuple

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.annotation_parser import AnnotationParser
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.segmentation import Segmentation
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError, ForbiddenClassError
from mlcvzoo_base.configuration.annotation_handler_config import (
    AnnotationHandlerSingleFileInputDataConfig,
)
from mlcvzoo_base.data_preparation.annotation_builder.cvat_annotation_builder import (
    CVATAnnotationBuilder,
)

logger = logging.getLogger(__name__)


class CVATAnnotationParser(AnnotationParser):
    """
    Super class for defining the methods that are needed to parse a list of
    instances that are of the type BaseAnnotation.
    Each annotation format e.g. Pascal-VOC, COCO, CVAT-for-images should have
    its own child AnnotationHandler class
    """

    def __init__(
        self,
        mapper: AnnotationClassMapper,
        cvat_input_data: List[AnnotationHandlerSingleFileInputDataConfig],
    ):
        AnnotationParser.__init__(self, mapper=mapper)

        self.cvat_input_data = cvat_input_data

    def parse(self) -> List[BaseAnnotation]:

        annotations: List[BaseAnnotation] = []

        for dataset_count, input_data in enumerate(self.cvat_input_data):

            tree = ET_xml.parse(input_data.input_path)
            root = tree.getroot()

            if root is not None:

                images = root.findall("image")

                for image in images:
                    cvat_tags = image.findall("tag")
                    cvat_bboxes = image.findall("box")
                    cvat_polygons = image.findall("polygon")

                    try:
                        classifications = self.__parse_cvat_classifications(cvat_tags=cvat_tags)
                        bounding_boxes = self.__parse_cvat_bounding_boxes(
                            cvat_bboxes=cvat_bboxes,
                            use_difficult=input_data.use_difficult,
                        )
                        segmentations = self.__parse_cvat_polygons(
                            cvat_polygons=cvat_polygons,
                            use_difficult=input_data.use_difficult,
                        )

                        image_path = image.attrib["name"]
                        image_width = int(image.attrib["width"])
                        image_height = int(image.attrib["height"])

                        replacement_string = (
                            AnnotationParser.csv_directory_replacement_string.format(dataset_count)
                        )

                        cvat_builder = CVATAnnotationBuilder(
                            image_shape=(image_height, image_width),
                            input_classifications=classifications,
                            input_bounding_boxes=bounding_boxes,
                            input_segmentations=segmentations,
                        )

                        annotation = cvat_builder.build(
                            image_path=image_path,
                            annotation_path=input_data.input_path,
                            image_dir=input_data.input_root_dir,
                            annotation_dir=input_data.input_root_dir,
                            replacement_string=replacement_string,
                        )
                        annotations.append(annotation)

                    except (ValueError, ForbiddenClassError) as error:
                        logger.warning("%s, annotation will be skipped" % str(error))
                        continue

        return annotations

    def __parse_cvat_classifications(
        self, cvat_tags: List[ET_xml.Element]
    ) -> List[Classification]:

        classifications: List[Classification] = []

        for tag in cvat_tags:
            xml_class_name = tag.attrib["label"]

            try:
                class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                    class_name=xml_class_name
                )
                class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                    class_name=xml_class_name
                )
            except ClassMappingNotFoundError:
                logger.warning(
                    "Could not find a valid class-mapping for class-name '%s'. "
                    "Classification will be skipped" % xml_class_name
                )
                continue

            classification = Classification(
                class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                model_class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                score=1.0,
            )

            classifications.append(classification)

        return classifications

    def __parse_cvat_bounding_boxes(
        self, cvat_bboxes: List[ET_xml.Element], use_difficult: bool
    ) -> List[BoundingBox]:

        bounding_boxes: List[BoundingBox] = []

        for cvat_bbox in cvat_bboxes:
            xml_class_name = cvat_bbox.attrib["label"]

            try:
                # map the parsed "class_name" according to the mapping defined in the mapper class
                class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                    class_name=xml_class_name
                )

                class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                    class_name=xml_class_name
                )
            except ClassMappingNotFoundError:
                logger.warning(
                    "Could not find a valid class-mapping for class-name '%s'. "
                    "BndBox will be skipped, cvat-box= '%s'"
                    % (
                        xml_class_name,
                        cvat_bbox,
                    )
                )
                continue

            occluded, difficult, content = CVATAnnotationParser.__read_attributes(
                cvat_bbox.findall("attribute")
            )

            bounding_box = BoundingBox(
                class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                model_class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                score=1.0,
                box=Box(
                    xmin=int(float(cvat_bbox.attrib["xtl"])),
                    ymin=int(float(cvat_bbox.attrib["ytl"])),
                    xmax=int(float(cvat_bbox.attrib["xbr"])),
                    ymax=int(float(cvat_bbox.attrib["ybr"])),
                ),
                occluded=occluded,
                difficult=difficult,
                content=content,
            )

            # TODO: handle occluded as well?
            if difficult and not use_difficult:
                logger.debug("Found difficult box, which will be skipped! %s", bounding_box)
                continue

            bounding_boxes.append(bounding_box)

        return bounding_boxes

    def __parse_cvat_polygons(
        self, cvat_polygons: List[ET_xml.Element], use_difficult: bool
    ) -> List[Segmentation]:

        segmentations: List[Segmentation] = []

        for cvat_polygon in cvat_polygons:
            xml_class_name = cvat_polygon.attrib["label"]

            try:
                class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                    class_name=xml_class_name
                )

                class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                    class_name=xml_class_name
                )
            except ClassMappingNotFoundError:
                logger.warning(
                    "Could not find a valid class-mapping for class-name '%s'. "
                    "Segmentation will be skipped, cvat-segmentation= '%s'",
                    xml_class_name,
                    cvat_polygon,
                )
                continue

            cvat_points = cvat_polygon.attrib["points"].split(";")

            polygon: List[Tuple[float, float]] = []

            for cvat_point in cvat_points:
                point_split = cvat_point.split(",")

                x = float(point_split[0])
                y = float(point_split[1])

                polygon.append((x, y))

            occluded, difficult, content = CVATAnnotationParser.__read_attributes(
                cvat_polygon.findall("attribute")
            )

            segmentation = Segmentation(
                class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                model_class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                score=1.0,
                polygon=polygon,
                occluded=occluded,
                difficult=difficult,
                content=content,
            )

            # TODO: handle occluded as well?
            if difficult and not use_difficult:
                logger.debug(
                    "Found difficult segmentation, which will be skipped! %s",
                    segmentation,
                )
                continue

            segmentations.append(segmentation)

        return segmentations

    @staticmethod
    def __read_attributes(attributes: List[ET_xml.Element]) -> Tuple[bool, bool, str]:

        occluded = False
        difficult = False
        content = ""

        for attribute in attributes:
            if attribute.attrib["name"] == "occluded":
                occluded = False if attribute.text == "false" else True
            if attribute.attrib["name"] == "difficult":
                difficult = False if attribute.text == "false" else True
            if attribute.attrib["name"] == "content":
                content = str(attribute.text)

        return occluded, difficult, content

    def parse_cvat_meta_info(self) -> List[ET_xml.Element]:
        """
        Parses all tags under meta tag into a list of XML Elements.

        Returns: a list of XML Elements

        """

        meta_elements: List[ET_xml.Element] = []
        for dataset_count, input_data in enumerate(self.cvat_input_data):

            tree = ET_xml.parse(input_data.input_path)
            root = tree.getroot()

            if root is not None:
                meta_tags = root.findall("meta")

                if len(meta_tags) > 1:
                    logger.warning(
                        "Found more than one <meta> tag in given XML file. "
                        "Format is not as expected."
                    )
                meta_elements.append(meta_tags[0])

        return meta_elements
