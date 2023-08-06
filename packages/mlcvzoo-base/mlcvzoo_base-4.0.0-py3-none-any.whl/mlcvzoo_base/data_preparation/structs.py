# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for enumerating options of formats"""
from mlcvzoo_base.configuration.structs import BaseType


class CSVOutputStringFormats(BaseType):
    BASE: str = "BASE"
    YOLO: str = "YOLO"
