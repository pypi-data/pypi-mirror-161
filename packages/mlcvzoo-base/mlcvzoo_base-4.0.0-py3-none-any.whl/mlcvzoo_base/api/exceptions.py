# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for custom exceptions"""


class ForbiddenClassError(Exception):
    """
    Error which indicates that an invalid class-name has been tried to be mapped
    """

    def __init__(self, invalid_class: str, postfix: str = ""):
        self.message: str = f"Parsed invalid class: '{invalid_class}' {postfix}"
        Exception.__init__(self, self.message)


class ClassMappingNotFoundError(Exception):
    """
    Error which indicates that a class ID / class name could not be mapped to
    a ClassIdentifier. This is relevant when parsing annotation information from
    annotation files like CVAT xml or COCO json or PASCAL VOC xml, or when the
    prediction output of a model is decoded.
    """
