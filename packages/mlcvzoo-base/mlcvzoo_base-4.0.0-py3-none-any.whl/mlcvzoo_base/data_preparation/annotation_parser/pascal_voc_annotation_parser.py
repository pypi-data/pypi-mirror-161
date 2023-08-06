# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for parsing PascalVOC formatted annotations"""
import logging
import os
from typing import List, Tuple
from xml.etree.ElementTree import ParseError

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.annotation_parser import AnnotationParser
from mlcvzoo_base.api.exceptions import ForbiddenClassError
from mlcvzoo_base.configuration.annotation_handler_config import (
    AnnotationHandlerPASCALVOCInputDataConfig,
)
from mlcvzoo_base.configuration.structs import AnnotationFileFormats, ImageFileFormats
from mlcvzoo_base.data_preparation.annotation_builder.pascal_voc_annotation_builder import (
    PascalVOCAnnotationBuilder,
)
from mlcvzoo_base.utils.file_utils import get_file_list

logger = logging.getLogger(__name__)


class PascalVOCAnnotationParser(AnnotationParser):
    """
    Super class for defining the methods that are needed to parse a list of
    instances that are of the type BaseAnnotation.
    Each annotation format e.g. Pascal-VOC, COCO, CVAT-for-images should have
    its own child AnnotationHandler class
    """

    def __init__(
        self,
        mapper: AnnotationClassMapper,
        pascal_voc_input_data: List[AnnotationHandlerPASCALVOCInputDataConfig],
    ):
        AnnotationParser.__init__(self, mapper=mapper)

        self.pascal_voc_input_data = pascal_voc_input_data

    @staticmethod
    def __ensure_annotations_match_images(
        image_path_list: List[str], annotation_path_list: List[str]
    ) -> Tuple[List[str], List[str]]:
        """

        Args:
            image_path_list:
            annotation_path_list:

        Returns:

        """
        # remove duplicate
        image_path_list = list(dict.fromkeys(image_path_list))
        annotation_path_list = list(dict.fromkeys(annotation_path_list))

        # TODO: allow more image formats
        cleaned_img = [
            os.path.basename(image_path)
            .replace(ImageFileFormats.JPEG, "")
            .replace(ImageFileFormats.PNG, "")
            for image_path in image_path_list
        ]
        cleaned_xml = [
            os.path.basename(annotation_path)
            .replace(AnnotationFileFormats.XML, "")
            .replace("_predicted", "")
            for annotation_path in annotation_path_list
        ]

        in_both_lists = set(cleaned_xml) & set(cleaned_img)

        img_indices = [idx for (idx, x) in enumerate(cleaned_img) if x in in_both_lists]
        xml_indices = [idx for (idx, x) in enumerate(cleaned_xml) if x in in_both_lists]

        cleaned_image_path_list = [
            image_path
            for (img_index, image_path) in enumerate(image_path_list)
            if img_index in img_indices
        ]
        cleaned_annotation_path_list = [
            annotation_path
            for (annotation_index, annotation_path) in enumerate(annotation_path_list)
            if annotation_index in xml_indices
        ]

        if len(image_path_list) > len(cleaned_image_path_list):
            logger.debug(
                "Did not find an annotation-paths for image-paths: \n\t- %s\n",
                "\n\t- ".join(
                    [
                        image_path_list[index]
                        for index in range(0, len(image_path_list))
                        if index not in img_indices
                    ]
                ),
            )

        if len(annotation_path_list) > len(cleaned_annotation_path_list):
            logger.debug(
                "Did not find an image-paths for annotation-paths: \n\t- %s\n",
                "\n\t- ".join(
                    [
                        annotation_path_list[index]
                        for index in range(0, len(annotation_path_list))
                        if index not in xml_indices
                    ]
                ),
            )

        return cleaned_image_path_list, cleaned_annotation_path_list

    def parse(self) -> List[BaseAnnotation]:

        image_path_list, annotation_path_list = self.__read_xml_file_paths()

        annotations: List[BaseAnnotation] = list()
        # Fill dictionary for implicit path replacement
        for dataset_count, input_data_config in enumerate(self.pascal_voc_input_data):
            if input_data_config.ignore_missing_images:
                image_path_list = len(annotation_path_list) * [""]
            else:
                (image_path_list, annotation_path_list,) = self.__ensure_annotations_match_images(
                    image_path_list=image_path_list,
                    annotation_path_list=annotation_path_list,
                )

            for image_path, annotation_path in zip(image_path_list, annotation_path_list):

                if (
                    not input_data_config.ignore_missing_images
                    and os.path.realpath(input_data_config.input_image_dir)
                    in os.path.realpath(image_path)
                    and os.path.realpath(input_data_config.input_xml_dir)
                    in os.path.realpath(annotation_path)
                ) or (
                    input_data_config.ignore_missing_images
                    and os.path.realpath(input_data_config.input_xml_dir)
                    in os.path.realpath(annotation_path)
                ):
                    replacement_string = AnnotationParser.csv_directory_replacement_string.format(
                        dataset_count
                    )

                    try:
                        pascal_voc_builder = PascalVOCAnnotationBuilder(
                            mapper=self.mapper,
                            use_difficult=input_data_config.use_difficult,
                        )

                        annotation: BaseAnnotation = pascal_voc_builder.build(
                            image_path=image_path,
                            annotation_path=annotation_path,
                            image_dir=input_data_config.input_image_dir,
                            annotation_dir=input_data_config.input_xml_dir,
                            replacement_string=replacement_string,
                        )

                        annotations.append(annotation)

                    except (ValueError, ForbiddenClassError, ParseError) as error:
                        logger.warning(
                            "%s, annotation from path %s will be skipped",
                            str(error),
                            annotation_path,
                        )
                        continue

        return annotations

    def __read_xml_file_paths(self) -> Tuple[List[str], List[str]]:

        image_paths = []
        xml_paths = []

        for input_data_config in self.pascal_voc_input_data:

            # CHECK SUBDIR CONFIG
            if len(input_data_config.input_sub_dirs) > 0:

                for sub_input_dir in input_data_config.input_sub_dirs:
                    # READ IMAGES
                    input_image_dir = os.path.join(
                        input_data_config.input_image_dir, sub_input_dir
                    )

                    image_paths.extend(
                        get_file_list(
                            input_dir=input_image_dir,
                            search_subfolders=True,
                            file_extension=f"{input_data_config.image_format}",
                        )
                    )

                    # READ ANNOTATIONS
                    input_xml_dir = os.path.join(input_data_config.input_xml_dir, sub_input_dir)

                    xml_paths.extend(
                        get_file_list(
                            input_dir=input_xml_dir,
                            search_subfolders=True,
                            # exclude_pattern="predicted",
                            file_extension=AnnotationFileFormats.XML,
                        )
                    )
            else:
                # READ IMAGES
                image_paths.extend(
                    get_file_list(
                        input_dir=input_data_config.input_image_dir,
                        search_subfolders=True,
                        file_extension=input_data_config.image_format,
                    )
                )

                # READ ANNOTATIONS
                xml_paths.extend(
                    get_file_list(
                        input_dir=input_data_config.input_xml_dir,
                        search_subfolders=True,
                        # exclude_pattern="predicted",
                        file_extension=AnnotationFileFormats.XML,
                    )
                )

        image_paths.sort()
        xml_paths.sort()

        return image_paths, xml_paths
