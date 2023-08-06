# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Data class for storing information that is needed to classify an object instance"""

from __future__ import annotations


class ClassIdentifier:
    def __init__(
        self,
        class_id: int,
        class_name: str,
    ):
        # id of the 'class', respectively the id of the object type
        self.__class_id: int = class_id

        # name of the 'class', respectively the name of the object type
        self.__class_name: str = class_name

    def __eq__(self, other: ClassIdentifier) -> bool:  # type: ignore
        return self.class_id == other.class_id or self.class_name == other.class_name

    @property
    def class_id(self) -> int:
        return self.__class_id

    @property
    def class_name(self) -> str:
        return self.__class_name
