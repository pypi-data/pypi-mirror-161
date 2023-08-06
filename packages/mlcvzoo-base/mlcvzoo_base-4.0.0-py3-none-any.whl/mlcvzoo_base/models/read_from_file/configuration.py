# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for configuring the parsing of information from yaml in python
accessible attributes for the ReadFromFileModel class
"""
from typing import Dict, List, Optional

import related
from config_builder.BaseConfigClass import BaseConfigClass

from mlcvzoo_base.api.configuration import Configuration
from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.detector_configs import DetectorConfig
from mlcvzoo_base.configuration.reduction_mapping_config import ReductionMappingConfig


@related.mutable(strict=True)
class ReadFromFileConfig(BaseConfigClass, Configuration):
    """Class for parsing information from yaml in respective hierarchy"""

    mutual_attribute_map: Dict[str, List[str]] = dict()

    class_mapping: ClassMappingConfig = related.ChildField(ClassMappingConfig)

    annotation_handler_config: AnnotationHandlerConfig = related.ChildField(
        cls=AnnotationHandlerConfig
    )

    use_image_name_hash: bool = related.BooleanField(default=False)

    include_segmentations: bool = related.BooleanField(default=False)

    reduction_class_mapping: Optional[ReductionMappingConfig] = related.ChildField(
        cls=ReductionMappingConfig, required=False, default=None
    )

    base_config: DetectorConfig = related.ChildField(cls=DetectorConfig, default=DetectorConfig())
