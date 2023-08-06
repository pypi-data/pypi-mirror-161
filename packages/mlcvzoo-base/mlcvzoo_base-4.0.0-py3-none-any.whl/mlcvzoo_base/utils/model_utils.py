# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for different utility operations regarding detection models"""
import logging
import os
from typing import Optional, Tuple

from mlcvzoo_base.api.configuration import BaseDetectorConfig

logger = logging.getLogger(__name__)


def parse_model_info(yaml_config_path: Optional[str]) -> Tuple[str, str, str]:
    """
    Parses model configuration to specific information: model_specifier, model_type, model_version

    Args:
        yaml_config_path: String, defines the path where the model configuration remains

    Returns: Tuple of model information: model_specifier, model_type, model_version

    """

    if yaml_config_path is None:
        model_specifier, model_type, model_version = "", "", ""
    elif os.path.isfile(yaml_config_path):
        model_specifier = os.path.basename(yaml_config_path).replace(".yaml", "")

        model_position = model_specifier.find("_")

        model_type = model_specifier[0:model_position]
        model_version = model_specifier[model_position + 1 :]
    else:
        model_specifier, model_type, model_version = "", "", ""

        logger.debug(
            "WARNING: The given yaml_config_path does not exist! "
            "Therefore the model_info variables will be set to empty strings!"
            "yaml_config_path: '%s'" % yaml_config_path
        )

    return model_specifier, model_type, model_version


def set_model_info(yaml_config_path: Optional[str], base_config: BaseDetectorConfig) -> None:
    """
    Sets model information in the base configuration of a detector.

    Args:
        yaml_config_path: String, defines the path where the model configuration remains
        base_config: BaseDetectorConfig, configuration of a detector

    Returns:
        None
    """

    assert isinstance(base_config, BaseDetectorConfig)

    model_specifier, model_type, model_version = parse_model_info(
        yaml_config_path=yaml_config_path
    )

    if base_config.MODEL_SPECIFIER == "":
        base_config.MODEL_SPECIFIER = model_specifier

    if base_config.MODEL_TYPE == "":
        base_config.MODEL_TYPE = model_type

    if base_config.MODEL_VERSION == "":
        base_config.MODEL_VERSION = model_version
