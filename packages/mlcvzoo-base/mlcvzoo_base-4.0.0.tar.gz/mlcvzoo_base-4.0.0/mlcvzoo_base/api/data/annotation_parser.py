# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for parsing annotations"""
from abc import ABC, abstractmethod
from typing import List

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper


class AnnotationParser(ABC):
    """
    Super class for defining the methods that are needed to parse a list of
    instances that are of the type BaseAnnotation.
    Each annotation format e.g. Pascal-VOC, COCO, CVAT-for-images should have
    its own child AnnotationHandler class
    """

    csv_directory_replacement_string = "IMAGE_DIR_{}"

    def __init__(self, mapper: AnnotationClassMapper):
        self.mapper: AnnotationClassMapper = mapper

    @abstractmethod
    def parse(self) -> List[BaseAnnotation]:
        """
        Parses annotations in respective format to BaseAnnotations

        Returns: a List of BaseAnnotations
        """

        raise NotImplementedError()
