# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for parsing information from yaml in python accessible attributes for the
AnnotationHandler class.
"""
import logging
import os
from typing import List, Optional

import related
from config_builder.BaseConfigClass import BaseConfigClass

from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.reduction_mapping_config import ReductionMappingConfig
from mlcvzoo_base.data_preparation.structs import CSVOutputStringFormats

logger = logging.getLogger(__name__)


@related.mutable(strict=True)
class AnnotationHandlerPASCALVOCInputDataConfig(BaseConfigClass):
    """Class for parsing information of PASCAL VOC input format"""

    input_image_dir: str = related.StringField()
    input_xml_dir: str = related.StringField()
    input_sub_dirs: List[str] = related.SequenceField(str)

    image_format: str = related.StringField()
    use_difficult: bool = related.BooleanField(default=True)
    ignore_missing_images: bool = related.BooleanField(default=False)


@related.mutable(strict=True)
class AnnotationHandlerSingleFileInputDataConfig(BaseConfigClass):
    """Class for parsing information of input data"""

    # Path to the annotation file
    input_path: str = related.StringField()
    # Root directory which fits to the relative directory in the given annotation file
    input_root_dir: str = related.StringField()

    # TODO: don't set defaults here?
    use_difficult: bool = related.BooleanField(default=True)


@related.mutable(strict=True)
class AnnotationHandlerWriteOutputCSVAnnotationConfig(BaseConfigClass):
    """Class for parsing information of output format when writing CSV annotations"""

    csv_dir: str = related.StringField()
    csv_base_file_name: str = related.StringField(default="")

    csv_split_0_file_name: str = related.StringField(default="")
    csv_split_1_file_name: str = related.StringField(default="")

    # TODO: add hint for file-name replacement? Add specific config class?
    timestamp_format: str = related.StringField(default="%Y-%m-%d")
    include_surrounding_bboxes: bool = related.BooleanField(default=True)
    output_string_format: str = related.StringField(default=CSVOutputStringFormats.BASE)

    def check_values(self) -> bool:
        if not os.path.isdir(self.csv_dir):
            # Note: this is not necessarily required or
            #       already existing when config is read (see test)
            logger.info("Class='%s', specify correct output_dir'%s'", type(self), self.csv_dir)

        return self.output_string_format in CSVOutputStringFormats.get_values_as_list(
            class_type=CSVOutputStringFormats
        )


@related.mutable(strict=True)
class AnnotationHandlerWriteOutputDarknetAnnotationConfig(BaseConfigClass):
    """Class for parsing information of output format when writing Darknet annotations"""

    train_data_set_dir: str = related.StringField()
    base_file_name: str = related.StringField(default="")
    write_as_symlink: bool = related.BooleanField(default=False)

    def get_train_file_path(self) -> str:
        return os.path.join(self.train_data_set_dir, f"{self.base_file_name}_train.txt")

    def get_test_file_path(self) -> str:
        return os.path.join(self.train_data_set_dir, f"{self.base_file_name}_test.txt")


@related.mutable(strict=True)
class AnnotationHandlerWriteOutputBoxSnippetsConfig(BaseConfigClass):
    """Class for parsing information of output directory when writing annotations"""

    output_dir: str = related.StringField()


@related.mutable(strict=True)
class AnnotationHandlerWriteOutputConfig(BaseConfigClass):
    """Class for parsing information of output format when writing annotations"""

    use_cross_val: bool = related.BooleanField()
    number_splits: int = related.IntegerField()
    split_size: int = related.FloatField()

    csv_annotation: Optional[AnnotationHandlerWriteOutputCSVAnnotationConfig] = related.ChildField(
        cls=AnnotationHandlerWriteOutputCSVAnnotationConfig,
        required=False,
        default=None,
    )

    darknet_train_set: Optional[
        AnnotationHandlerWriteOutputDarknetAnnotationConfig
    ] = related.ChildField(
        cls=AnnotationHandlerWriteOutputDarknetAnnotationConfig,
        required=False,
        default=None,
    )
    darknet_annotation: AnnotationHandlerWriteOutputDarknetAnnotationConfig = related.ChildField(
        cls=AnnotationHandlerWriteOutputDarknetAnnotationConfig,
        required=False,
        default=None,
    )
    use_difficult: bool = related.BooleanField(default=True)
    use_occluded: bool = related.BooleanField(default=True)

    bbox_snippets: Optional[AnnotationHandlerWriteOutputBoxSnippetsConfig] = related.ChildField(
        AnnotationHandlerWriteOutputBoxSnippetsConfig, required=False, default=None
    )

    random_state: Optional[int] = related.ChildField(cls=int, default=None, required=False)


@related.mutable(strict=True)
class AnnotationHandlerConfig(BaseConfigClass):
    """Class for parsing information from yaml in respective hierarchy"""

    class_mapping: Optional[ClassMappingConfig] = related.ChildField(
        cls=ClassMappingConfig, required=False, default=None
    )

    pascal_voc_input_data: List[AnnotationHandlerPASCALVOCInputDataConfig] = related.SequenceField(
        AnnotationHandlerPASCALVOCInputDataConfig, default=[]
    )

    coco_input_data: List[AnnotationHandlerSingleFileInputDataConfig] = related.SequenceField(
        AnnotationHandlerSingleFileInputDataConfig, default=[]
    )

    cvat_input_data: List[AnnotationHandlerSingleFileInputDataConfig] = related.SequenceField(
        AnnotationHandlerSingleFileInputDataConfig, default=[]
    )

    write_output: Optional[AnnotationHandlerWriteOutputConfig] = related.ChildField(
        AnnotationHandlerWriteOutputConfig, required=False, default=None
    )

    reduction_class_mapping: Optional[ReductionMappingConfig] = related.ChildField(
        cls=ReductionMappingConfig, required=False, default=None
    )
