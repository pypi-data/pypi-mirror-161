# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for parsing information from yaml in python accessible attributes for different
configuration classes and also for the ModelRegistry class.
"""
from typing import Any, Dict

import related
from config_builder.BaseConfigClass import BaseConfigClass

INIT_FOR_INFERENCE_PARAMETER = "init_for_inference"


@related.mutable(strict=True)
class ModelConfig(BaseConfigClass):
    class_type: str = related.StringField()
    constructor_parameters: Dict[str, Any] = related.ChildField(
        cls=dict,
    )

    def is_inference(self) -> bool:
        return INIT_FOR_INFERENCE_PARAMETER in self.constructor_parameters

    def set_inference(self, inference: bool) -> None:
        if INIT_FOR_INFERENCE_PARAMETER in self.constructor_parameters:
            self.constructor_parameters[INIT_FOR_INFERENCE_PARAMETER] = inference
