# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for parsing information from yaml in python accessible attributes for object
detection classes.
"""
from __future__ import annotations

from dataclasses import dataclass

import related
from config_builder.BaseConfigClass import BaseConfigClass

from mlcvzoo_base.api.configuration import (
    BaseDetectorConfig,
    BaseDetectorInferenceConfig,
)


@dataclass
@related.mutable(strict=True)
class DetectorConfig(BaseConfigClass, BaseDetectorConfig):
    """Class for parsing information about detector model"""

    # NOTE: When the fields are empty, they be filled based on the given config-path filename

    MODEL_TYPE: str = related.StringField(default="")
    MODEL_VERSION: str = related.StringField(default="")
    MODEL_SPECIFIER: str = related.StringField(default="")

    def __call__(self) -> DetectorConfig:
        return DetectorConfig(
            MODEL_VERSION="",
            MODEL_TYPE="",
            MODEL_SPECIFIER="",
        )


@related.mutable(strict=True)
class InferenceConfig(BaseConfigClass, BaseDetectorInferenceConfig):
    """Class for parsing information about object detection inferences"""

    config_path: str = related.StringField()
    checkpoint_path: str = related.StringField()
    score_threshold: float = related.FloatField()
