# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for building CSV formatted annotations."""
import logging
import os
from typing import List, Tuple

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_builder import AnnotationBuilder
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError
from mlcvzoo_base.configuration.structs import AnnotationFileFormats, ImageFileFormats
from mlcvzoo_base.data_preparation.utils import ensure_abspath, replace_index_by_dir
from mlcvzoo_base.utils.implicit_path_replacements import ImplicitReplacement

logger = logging.getLogger(__name__)


class CSVAnnotationBuilder(AnnotationBuilder):
    """
    Super class for defining the methods that are needed to build a BaseAnnotation
    object from a CSV type XML file.
    """

    def __init__(
        self,
        csv_line: str,
        mapper: AnnotationClassMapper,
    ) -> None:
        AnnotationBuilder.__init__(self)

        self.csv_line: str = csv_line
        self.mapper: AnnotationClassMapper = mapper

    def build(
        self,
        image_path: str,
        annotation_path: str,
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
    ) -> BaseAnnotation:

        if not os.path.isdir(image_dir):
            raise ValueError(
                f"image_dir '{image_dir}' does not exist. Please provide a valid directory"
            )

        (csv_annotation_path, csv_image_path, image_shape, bounding_boxes,) = self.__init_from_csv(
            image_dir=image_dir,
            annotation_dir=annotation_dir,
        )

        annotation = BaseAnnotation(
            image_path=csv_image_path,
            annotation_path=csv_annotation_path,
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

        annotation = replace_index_by_dir(
            annotation=annotation,
        )

        annotation = ensure_abspath(annotation=annotation)

        return annotation

    def __init_from_csv(
        self,
        image_dir: str,
        annotation_dir: str,
    ) -> Tuple[str, str, Tuple[int, int], List[BoundingBox]]:
        """

        Args:
            image_dir: directory where the image lives
            annotation_dir: directory of the image's annotation

        Returns: path to the annotation,
                path to the annotated image,
                shape of the annotated image and
                a list of annotated bounding_boxes

        """

        bounding_boxes, image_path, image_shape = self.__from_csv_entry()

        file_path = CSVAnnotationBuilder._get_annotation_path(
            image_path, image_dir=image_dir, annotation_dir=annotation_dir
        )

        return file_path, image_path, image_shape, bounding_boxes

    def __from_csv_entry(self) -> Tuple[List[BoundingBox], str, Tuple[int, int]]:
        """
        Parses an image's annotation from a CSV entry (row)

        Returns: a list of annotated bounding_boxes,
            the file path of the image, if available and
            the shape of the annotated image

        """

        line_split = self.csv_line.split(" ")

        image_path = line_split[0]
        image_shape = (int(line_split[1]), int(line_split[2]))

        bounding_boxes: List[BoundingBox] = list()

        for index in range(3, len(line_split)):
            annotation_split = line_split[index].split(",")

            annotation_class_name = annotation_split[4]

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
                    "BndBox will be skipped, csv-line-split = '%s'"
                    % (annotation_class_name, line_split)
                )
                continue

            bounding_boxes.append(
                BoundingBox(
                    box=Box(
                        xmin=int(annotation_split[0]),
                        ymin=int(annotation_split[1]),
                        xmax=int(annotation_split[2]),
                        ymax=int(annotation_split[3]),
                    ),
                    class_identifier=ClassIdentifier(class_id=class_id, class_name=class_name),
                    model_class_identifier=ClassIdentifier(
                        class_id=class_id, class_name=class_name
                    ),
                    difficult=False,
                    occluded=False,
                    content="",
                    score=1.0,
                )
            )

        return bounding_boxes, image_path, image_shape

    @staticmethod
    def _get_annotation_path(
        image_path: str,
        image_dir: str,
        annotation_dir: str,
        annotation_encoding: str = AnnotationFileFormats.XML,
    ) -> str:
        """
        Builds the annotation path to an image, assuming images and annotation live in
        similarly structured directories.

        Args:
            image_path: path to the image
            image_dir: directory where the image lives
            annotation_dir: directory of the image's annotation
            annotation_encoding: format of the annotation (one of AnnotationFileFormats)

        Returns: the path to the image's annotation

        """

        annotation_path: str = ImplicitReplacement.replace_directory_in_path(
            file_path=image_path,
            replacement_key=image_dir,
            replacement_value=annotation_dir,
            how=ImplicitReplacement.FIRST,
        )
        annotation_path = annotation_path.replace(ImageFileFormats.JPEG, annotation_encoding)

        annotation_path = annotation_path.replace(ImageFileFormats.PNG, annotation_encoding)

        return annotation_path
