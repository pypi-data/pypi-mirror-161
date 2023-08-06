# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for writing annotations to a file"""
from abc import abstractmethod
from typing import List, Optional

from mlcvzoo_base.api.data.annotation import BaseAnnotation


class AnnotationWriter:
    """
    Super class for defining the methods that are needed to write a list of
    annotations into a file.
    Each annotation format e.g. Pascal-VOC, COCO, CVAT-for-images should have
    its own child class.
    """

    @abstractmethod
    def write(self, annotations: List[BaseAnnotation]) -> Optional[str]:
        """
        Write a given list of annotations into a file.

        Args:
            annotations: list of annotations that should be written
            output_file_path: path to file, where the annotations should be written to

        Returns: None

        """
        raise NotImplementedError()
