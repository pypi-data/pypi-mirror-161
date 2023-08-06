# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module that holds classes for different types of basic dataset information."""
import os
from dataclasses import dataclass, field
from typing import Dict

from dataclasses_json import dataclass_json

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.utils.implicit_path_replacements import ImplicitReplacement


@dataclass_json
@dataclass
class ClassesCountInfo:
    count: str
    count_s: str
    count_m: str
    count_l: str


@dataclass_json
@dataclass
class DatasetDirectoryInfo:
    """Class holds information about a specific directory"""

    file_count: int
    classes_count_info: Dict[str, ClassesCountInfo] = field(default_factory=dict)


@dataclass_json
@dataclass
class BaseDatasetInfo:
    """Class holds information about a specific dataset"""

    classes_path: str
    image_count: float

    directory_info: Dict[str, DatasetDirectoryInfo] = field(default_factory=dict)

    base_file: str = ""

    def update(self, annotation: BaseAnnotation) -> None:
        """
        Updates the class's directory information with the given annotation.

        Args:
            annotation: BaseAnnotation object

        """

        self.image_count += 1

        # get relative directory of the annotation
        relative_dirname = os.path.dirname(
            ImplicitReplacement.replace_directory_in_path(
                file_path=annotation.annotation_path,
                replacement_key=annotation.annotation_dir,
                replacement_value="",
            )
        )

        # Init info dict
        if relative_dirname not in self.directory_info:
            self.directory_info[relative_dirname] = DatasetDirectoryInfo(file_count=1)
        else:
            self.directory_info[relative_dirname].file_count += 1

        # Fill info dict with statistics about the annotation
        # TODO:
        # for bounding_box in annotation.get_bounding_boxes(include_segmentations=True):
        #     bbox_height = (bounding_box.box.ymax - bounding_box.box.ymin) / annotation.image_shape[0] * 480
        #     bbox_width = (bounding_box.box.xmax - bounding_box.box.xmin) / annotation.image_shape[1] * 640
        #
        #     bbox_sqrt_area = math.sqrt(bbox_height * bbox_width)
        #
        #     if bounding_box.class_name in info_dict[relative_dirname]:
        #         info_dict[relative_dirname][bounding_box.class_name]["count"] += 1
        #
        #         if bbox_sqrt_area <= 32:
        #             info_dict[relative_dirname][bounding_box.class_name]["count_s"] += 1
        #
        #         if 32 < bbox_sqrt_area <= 96:
        #             info_dict[relative_dirname][bounding_box.class_name]["count_m"] += 1
        #
        #         if bbox_sqrt_area > 96:
        #             info_dict[relative_dirname][bounding_box.class_name]["count_l"] += 1
        #     else:
        #         info_dict[relative_dirname][bounding_box.class_name] = dict()
        #
        #         info_dict[relative_dirname][bounding_box.class_name]["count"] = 1
        #
        #         info_dict[relative_dirname][bounding_box.class_name]["count_s"] = 0
        #         info_dict[relative_dirname][bounding_box.class_name]["count_m"] = 0
        #         info_dict[relative_dirname][bounding_box.class_name]["count_l"] = 0
        #
        #         if bbox_sqrt_area <= 32:
        #             info_dict[relative_dirname][bounding_box.class_name]["count_s"] += 1
        #
        #         if 32 < bbox_sqrt_area <= 96:
        #             info_dict[relative_dirname][bounding_box.class_name]["count_m"] += 1
        #
        #         if bbox_sqrt_area > 96:
        #             info_dict[relative_dirname][bounding_box.class_name]["count_l"] += 1
