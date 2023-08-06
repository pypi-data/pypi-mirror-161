# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for configuring the visualization of model outputs
"""

import related
from config_builder.BaseConfigClass import BaseConfigClass


@related.mutable(strict=True)
class VisualizationConfig(BaseConfigClass):
    """Class for parsing information for visualization"""

    show_image: bool = related.BooleanField(default=True)
    font_path: str = related.StringField(default="")
    output_shape: int = related.IntegerField(default=500)
