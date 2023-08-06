# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for configuring machine learning models"""
from dataclasses import dataclass


@dataclass
class Configuration:
    """
    A model configuration.
    Typically sub-classes of a configuration parser implement
    this class to provide a mechanism to feed parameters into models or training.
    """

    def __init__(self) -> None:
        """
        Constructor creates a new instance.
        Ths constructor must be called by derived sub-classes.
        """
        pass


@dataclass
class BaseDetectorConfig:
    MODEL_TYPE: str = ""
    MODEL_VERSION: str = ""
    MODEL_SPECIFIER: str = ""


@dataclass
class BaseDetectorInferenceConfig:
    config_path: str
    checkpoint_path: str
    score_threshold: float = 0.5
