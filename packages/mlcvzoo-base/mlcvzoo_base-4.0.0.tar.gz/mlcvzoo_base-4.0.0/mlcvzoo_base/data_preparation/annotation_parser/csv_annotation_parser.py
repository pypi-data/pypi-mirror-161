# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for parsing CSV formatted annotations"""
import logging
import os
from dataclasses import field
from typing import List, Optional, Tuple

from tqdm import tqdm

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.annotation_parser import AnnotationParser
from mlcvzoo_base.api.exceptions import ForbiddenClassError
from mlcvzoo_base.configuration.annotation_handler_config import (
    AnnotationHandlerPASCALVOCInputDataConfig,
    AnnotationHandlerSingleFileInputDataConfig,
)
from mlcvzoo_base.data_preparation.annotation_builder.csv_annotation_builder import (
    CSVAnnotationBuilder,
)

logger = logging.getLogger(__name__)


class CSVAnnotationParser(AnnotationParser):
    """
    Super class for defining the methods that are needed to parse a list of
    instances that are of the type BaseAnnotation.
    Each annotation format e.g. Pascal-VOC, COCO, CVAT-for-images should have
    its own child AnnotationHandler class
    """

    def __init__(
        self,
        mapper: AnnotationClassMapper,
        csv_file_path: str,
        pascal_voc_input_data: List[AnnotationHandlerPASCALVOCInputDataConfig] = field(
            default_factory=lambda: []
        ),
        coco_input_data: List[AnnotationHandlerSingleFileInputDataConfig] = field(
            default_factory=lambda: []
        ),
        cvat_input_data: List[AnnotationHandlerSingleFileInputDataConfig] = field(
            default_factory=lambda: []
        ),
    ):
        AnnotationParser.__init__(self, mapper=mapper)

        self.csv_file_path = csv_file_path
        self.pascal_voc_input_data = pascal_voc_input_data
        self.coco_input_data = coco_input_data
        self.cvat_input_data = cvat_input_data

    def parse(self) -> List[BaseAnnotation]:

        annotations: List[BaseAnnotation] = list()

        if os.path.isfile(self.csv_file_path):
            with open(file=self.csv_file_path, mode="r", encoding="'utf-8") as annotations_file:

                csv_lines = annotations_file.readlines()

                for index in tqdm(range(len(csv_lines))):
                    csv_line = csv_lines[index].strip()

                    pascal_voc_input_data_index: Optional[int] = None
                    coco_input_data_index: Optional[int] = None
                    cvat_input_data_index: Optional[int] = None

                    pascal_voc_replacement_string: Optional[str] = None
                    coco_replacement_string: Optional[str] = None
                    cvat_replacement_string: Optional[str] = None

                    if len(self.pascal_voc_input_data) > 0:
                        (
                            pascal_voc_input_data_index,
                            pascal_voc_replacement_string,
                        ) = CSVAnnotationParser.__get_input_data_index(
                            dataset_len=len(self.pascal_voc_input_data),
                            csv_line=csv_line,
                        )

                    if len(self.coco_input_data) > 0:
                        (
                            coco_input_data_index,
                            coco_replacement_string,
                        ) = CSVAnnotationParser.__get_input_data_index(
                            dataset_len=len(self.coco_input_data),
                            csv_line=csv_line,
                        )

                    if len(self.cvat_input_data) > 0:
                        (
                            cvat_input_data_index,
                            cvat_replacement_string,
                        ) = CSVAnnotationParser.__get_input_data_index(
                            dataset_len=len(self.cvat_input_data),
                            csv_line=csv_line,
                        )

                    image_dir: Optional[str] = None
                    annotation_dir: Optional[str] = None
                    replacement_string: Optional[str] = None

                    if pascal_voc_input_data_index is not None:
                        image_dir = self.pascal_voc_input_data[
                            pascal_voc_input_data_index
                        ].input_image_dir

                        annotation_dir = self.pascal_voc_input_data[
                            pascal_voc_input_data_index
                        ].input_xml_dir

                        replacement_string = pascal_voc_replacement_string

                    elif coco_input_data_index is not None:
                        image_dir = self.coco_input_data[coco_input_data_index].input_root_dir
                        annotation_dir = self.coco_input_data[coco_input_data_index].input_path

                        replacement_string = coco_replacement_string

                    elif cvat_input_data_index is not None:
                        image_dir = self.cvat_input_data[cvat_input_data_index].input_root_dir
                        annotation_dir = self.cvat_input_data[cvat_input_data_index].input_path

                        replacement_string = cvat_replacement_string

                    if (
                        image_dir is not None
                        and annotation_dir is not None
                        and replacement_string is not None
                    ):
                        csv_builder = CSVAnnotationBuilder(csv_line=csv_line, mapper=self.mapper)

                        try:
                            annotation = csv_builder.build(
                                image_path="",
                                annotation_path="",
                                image_dir=image_dir,
                                annotation_dir=annotation_dir,
                                replacement_string=replacement_string,
                            )

                            annotations.append(annotation)

                        except (ValueError, ForbiddenClassError) as error:
                            logger.warning("%s, annotation will be skipped" % str(error))
                            continue
                    else:
                        logger.warning(
                            "Could not find valid replacement for image or annotation directory!\n"
                            "csv-line: %s \n"
                            "pascal-voc-len: %s \n"
                            "coco-len: %s \n"
                            "image_dir: %s \n"
                            "annotation_dir: %s \n"
                            % (
                                csv_line,
                                len(self.pascal_voc_input_data),
                                len(self.coco_input_data),
                                image_dir,
                                annotation_dir,
                            )
                        )
        else:
            error_string = f"ERROR: file '{self.csv_file_path}' does not exist!"

            logger.error(error_string)
            raise ValueError(error_string)

        return annotations

    @staticmethod
    def __get_input_data_index(
        dataset_len: int, csv_line: str
    ) -> Tuple[Optional[int], Optional[str]]:

        input_data_index: Optional[int] = None
        replacement_string: Optional[str] = None

        for i in range(0, dataset_len):

            replacement_string = AnnotationParser.csv_directory_replacement_string.format(i)

            logger.debug(
                "Check line: \n - replacement-string: %s \n - csv_line: %s ",
                replacement_string,
                csv_line,
            )

            if replacement_string is not None:
                image_path = csv_line.split(" ")[0]

                image_path_split = image_path.split("/")

                if image_path_split[0] == replacement_string:
                    input_data_index = i
                    break

        return input_data_index, replacement_string
