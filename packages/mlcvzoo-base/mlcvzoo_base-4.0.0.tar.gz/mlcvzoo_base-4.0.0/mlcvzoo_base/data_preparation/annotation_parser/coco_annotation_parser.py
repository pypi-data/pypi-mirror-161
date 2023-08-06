# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for parsing COCO formatted annotations"""
import json
import logging
import os
from typing import List

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.annotation_parser import AnnotationParser
from mlcvzoo_base.api.exceptions import ForbiddenClassError
from mlcvzoo_base.configuration.annotation_handler_config import (
    AnnotationHandlerSingleFileInputDataConfig,
)
from mlcvzoo_base.data_preparation.annotation_builder.coco_annotation_builder import (
    COCOAnnotationBuilder,
)

logger = logging.getLogger(__name__)


class COCOAnnotationParser(AnnotationParser):
    """
    Super class for defining the methods that are needed to parse a list of
    instances that are of the type BaseAnnotation.
    Each annotation format e.g. Pascal-VOC, COCO, CVAT-for-images should have
    its own child AnnotationHandler class
    """

    def __init__(
        self,
        mapper: AnnotationClassMapper,
        coco_input_data: List[AnnotationHandlerSingleFileInputDataConfig],
    ) -> None:
        AnnotationParser.__init__(self, mapper=mapper)

        self.coco_input_data = coco_input_data

    def parse(self) -> List[BaseAnnotation]:

        annotations: List[BaseAnnotation] = list()

        for dataset_count, input_data in enumerate(self.coco_input_data):
            with open(file=input_data.input_path, mode="r", encoding="'utf-8") as annotation_file:
                annotation_dict = json.load(fp=annotation_file)

            coco_images = annotation_dict["images"]

            for coco_image in coco_images:
                image_path = os.path.join(input_data.input_root_dir, coco_image["file_name"])
                image_width = coco_image["width"]
                image_height = coco_image["height"]

                replacement_string = AnnotationParser.csv_directory_replacement_string.format(
                    dataset_count
                )

                coco_builder = COCOAnnotationBuilder(
                    image_shape=(image_height, image_width),
                    image_id=coco_image["id"],
                    coco_annotations=annotation_dict["annotations"],
                    coco_categories=annotation_dict["categories"],
                    mapper=self.mapper,
                    use_difficult=input_data.use_difficult,
                )

                try:
                    annotation = coco_builder.build(
                        image_path=image_path,
                        annotation_path=input_data.input_path,
                        image_dir=input_data.input_root_dir,
                        annotation_dir=os.path.dirname(input_data.input_path),
                        replacement_string=replacement_string,
                    )

                    annotations.append(annotation)

                except (ValueError, ForbiddenClassError) as error:
                    logger.warning("%s, annotation will be skipped" % str(error))
                    continue

        return annotations
