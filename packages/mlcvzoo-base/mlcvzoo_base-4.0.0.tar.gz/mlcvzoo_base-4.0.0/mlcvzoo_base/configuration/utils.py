# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for different utility operations regarding configuration operations."""
import logging
import os
import sys
import time
from argparse import ArgumentTypeError
from typing import Any, Dict, Optional, Tuple, Type, Union, cast

import yaml
from config_builder import BaseConfigClass, ConfigBuilder
from config_builder.yaml_constructors import (
    join_object,
    join_object_from_config_dir,
    join_path,
    join_string,
    join_string_with_delimiter,
)
from related import to_dict, to_model, to_yaml

from mlcvzoo_base.configuration.detector_configs import DetectorConfig
from mlcvzoo_base.configuration.replacement_config import ReplacementConfig
from mlcvzoo_base.utils.model_utils import set_model_info

logger = logging.getLogger(__name__)


def get_replacement_map_from_replacement_config(
    yaml_config_path: str,
) -> Tuple[Dict[str, str], Optional[ReplacementConfig]]:

    """
    Convenient method to fill the (global) replacement map of the config-builder.
    In the MLCVZoo all attributes of the ReplacementConfig class can be used as
    replacements in string configuration-attributes, as well as replacements in
    config-paths which are defined in e.g. !join_object. This Method parses the
    ReplacementConfig given by the yaml_config_path parameter and sets the corresponding
    values for the replacement map in the config-builder according to the parsed content.

    Args:
        yaml_config_path: The config-file where to parse the ReplacementConfig from

    Returns:
        Dictionary with a sting mapping of placeholders to actual os paths
    """
    replacement_config: Optional[ReplacementConfig] = None

    string_replacement_map: Dict[str, str] = {}

    if os.path.isfile(yaml_config_path):

        replacement_config = parse_replacement_config(yaml_config_path=yaml_config_path)

        logger.info(
            "Successfully extracted content for placeholders "
            "from the replacement config given by: \n"
            " - yaml_config_path: %s\n"
            " - replacement_config: %s\n\n"
            f"Use these placeholders to update the string replacement map\n"
            % (yaml_config_path, replacement_config)
        )

        for key, value in vars(replacement_config).items():
            if isinstance(value, str):
                string_replacement_map[key] = value
    else:
        logger.warning(
            f"The given yaml_config_path '{yaml_config_path} does not exist!\n"
            "No content for placeholders could be extracted from "
            f"the replacement config given by: {yaml_config_path}. \n"
            f"Only update placeholder identifier from the replacement config (empty values)"
            f": {list(ReplacementConfig.__dict__['__annotations__'].keys())}"
        )

        for key, value in ReplacementConfig.__dict__["__annotations__"].items():
            if isinstance(value, str):
                string_replacement_map[key] = ""

    return string_replacement_map, replacement_config


def parse_replacement_config(
    yaml_config_path: str, replacement_config_key: str = "replacement_config"
) -> ReplacementConfig:
    """
    Parse an ReplacementConfig object from the given yaml_config_path.

    Args:
        yaml_config_path: string, path to a yaml configuration file
        replacement_config_key: string, key for replacement config in YAML

    Returns:
        The ReplacementConfig object derived from the file
    """
    # register the tag handlers
    yaml.add_constructor("!join_string", join_string)
    yaml.add_constructor("!join_string_with_delimiter", join_string_with_delimiter)
    yaml.add_constructor("!join_path", join_path)
    yaml.add_constructor("!join_object", join_object)
    yaml.add_constructor("!join_object_from_config_dir", join_object_from_config_dir)

    with open(file=yaml_config_path, mode="r", encoding="utf8") as config_file:
        yaml_dict = yaml.load(stream=config_file, Loader=yaml.Loader)

    if replacement_config_key in yaml_dict:
        replacement_config_dict = yaml_dict.pop(replacement_config_key)
    else:
        replacement_config_dict = yaml_dict

    return cast(ReplacementConfig, to_model(ReplacementConfig, replacement_config_dict))


def str2bool(v: Union[bool, str]) -> bool:
    """
    Parses an object to a boolean value.

    Args:
        v: Any, an expression which indicates a boolean decision
            so either a bool variable or
            a string with one of "yes", "true", "t", "y", "1" or
            one of "no", "false", "f", "n", "0"

    Returns:
         bool, the closest boolean equivalent to the given input

    Raises:
        ArgumentTypeError if no reasonable matching is possible
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
    raise ArgumentTypeError("Boolean value expected.")


def create_configuration(
    configuration_class: Type[BaseConfigClass],
    from_yaml: Optional[str] = None,
    input_configuration: Optional[BaseConfigClass] = None,
    string_replacement_map: Optional[Dict[str, str]] = None,
) -> BaseConfigClass:
    """
    Utility method to build a configuration object.

    Args:
        configuration_class: The type of the configuration object
        from_yaml: (Optional) A yaml filepath where to build the configuration
                    object from
        input_configuration: (Optional) An already existing configuration object
        string_replacement_map: A dictionary that defines placeholders which can be used
                                while parsing the file. They can be understood as variables
                                that can be used to define configs that are valid across
                                multiple devices.

    Returns:
        The created configuration object
    """
    configuration: BaseConfigClass

    logger.info(
        f"\n==========================================\n"
        f"Create configuration:\n"
        f" - class {configuration_class} \n"
        f" - from yaml: {from_yaml}\n"
        f" - input configuration: {input_configuration}\n"
        f"=========================================="
    )

    configuration = ConfigBuilder(
        class_type=configuration_class,
        yaml_config_path=from_yaml,
        configuration=input_configuration,
        string_replacement_map=string_replacement_map,
        mutual_attribute_map={},
    ).configuration

    configuration_vars = vars(configuration)

    if "base_config" in configuration_vars and isinstance(
        configuration_vars["base_config"], DetectorConfig
    ):
        set_model_info(yaml_config_path=from_yaml, base_config=configuration_vars["base_config"])

        model_string_replacement_map = to_dict(configuration_vars["base_config"])

        configuration.recursive_string_replacement(
            string_replacement_map=model_string_replacement_map
        )

    return configuration


def handle_value_error_for_tool_configuration(
    value_error: ValueError, config_builder_instance: ConfigBuilder
) -> None:

    logger.warning(str(value_error))
    for logger_handler in logger.root.handlers:
        logger_handler.flush()
    time.sleep(0.1)

    config_builder_instance.parser.print_help(sys.stdout)


def write_config_to_yaml(config: BaseConfigClass, output_yaml_config_path: str) -> None:
    """

    Args:
        config:
        output_yaml_config_path:

    Returns:

    """

    with open(file=output_yaml_config_path, mode="w") as output_yaml_file:
        logger.info("Write current model-configuration to file: %s", output_yaml_config_path)

        to_yaml(
            obj=config,
            yaml_package=yaml,
            dumper_cls=yaml.Dumper,
            stream=output_yaml_file,
        )
