# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for building Pascal VOC formatted annotations."""
import logging
import os
import xml.etree.ElementTree as ET_xml
from typing import List, Tuple

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_builder import AnnotationBuilder
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError
from mlcvzoo_base.data_preparation.utils import ensure_abspath

logger = logging.getLogger(__name__)


class PascalVOCAnnotationBuilder(AnnotationBuilder):
    """
    Super class for defining the methods that are needed to build a BaseAnnotation
    object from a Pascal VOC type XML file.
    """

    def __init__(self, mapper: AnnotationClassMapper, use_difficult: bool) -> None:
        AnnotationBuilder.__init__(self)

        self.mapper = mapper
        self.use_difficult = use_difficult

    def build(
        self,
        image_path: str,
        annotation_path: str,
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
    ) -> BaseAnnotation:

        (
            annotation_path,
            image_shape,
            bounding_boxes,
            source_image_filename,
        ) = self.__init_from_pascal_voc_xml(xml_file_path=annotation_path)

        if not os.path.isfile(image_path):
            image_path = source_image_filename

        annotation: BaseAnnotation = BaseAnnotation(
            image_path=image_path,
            annotation_path=annotation_path,
            image_shape=image_shape,
            classifications=[],
            bounding_boxes=bounding_boxes,
            segmentations=[],
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

    def __init_from_pascal_voc_xml(
        self,
        xml_file_path: str,
    ) -> Tuple[str, Tuple[int, int], List[BoundingBox], str]:
        """
        Parses and generates objects that are needed to build a BaseAnnotation

        Args:
            xml_file_path: Can either be a string to a XML-File or a File-Object of a XML-File
                in VOC-Format

        Returns: the given xml_file_path,
                the shape of the annotated image,
                a list of annotated bounding_boxes and
                the file path of the image, if available in xml file

        """

        bounding_boxes: List[BoundingBox] = list()

        tree = ET_xml.parse(xml_file_path)

        root = tree.getroot()

        width = int(root.find("size")[1].text)  # type: ignore
        height = int(root.find("size")[0].text)  # type: ignore
        image_shape = (width, height)

        source_image_filename = ""
        if root.find("path") is not None:
            source_image_filename = (
                root.find("path").text if root.find("path").text is not None else ""  # type: ignore
            )

        for member in root.findall("object"):

            annotation_class_name: str = member[0].text  # type: ignore

            try:
                # map the parsed "class_name" according to the mapping defined in the mapper class
                class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                    class_name=annotation_class_name
                )

                class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                    class_name=annotation_class_name
                )
            except ClassMappingNotFoundError:
                logger.warning(
                    "Could not find a valid class-mapping for class-name '%s'. "
                    "BndBox will be skipped, file = '%s'"
                    % (
                        annotation_class_name,
                        xml_file_path,
                    )
                )
                continue

            # TODO: Handle other properties, like 'occluded', 'truncated'
            # TODO: make it configurable? => add to ClassMapping
            difficult = False
            difficult_tag = member.find("difficult")

            if difficult_tag is not None and difficult_tag.text == "1":
                difficult = True

            box_tag = member.find("bndbox")

            if box_tag is None:
                continue

            bounding_box = BoundingBox(
                box=Box(
                    xmin=int(float(str(box_tag[0].text))),
                    ymin=int(float(str(box_tag[1].text))),
                    xmax=int(float(str(box_tag[2].text))),
                    ymax=int(float(str(box_tag[3].text))),
                ),
                class_identifier=ClassIdentifier(class_id=class_id, class_name=class_name),
                model_class_identifier=ClassIdentifier(class_id=class_id, class_name=class_name),
                difficult=False,
                occluded=False,
                content="",
                score=1.0,
            )

            # TODO: handle occluded as well?
            if difficult and not self.use_difficult:
                logger.debug("Found difficult box, which will be skipped! %s", bounding_box)
                continue

            bounding_boxes.append(bounding_box)

        return xml_file_path, image_shape, bounding_boxes, source_image_filename
