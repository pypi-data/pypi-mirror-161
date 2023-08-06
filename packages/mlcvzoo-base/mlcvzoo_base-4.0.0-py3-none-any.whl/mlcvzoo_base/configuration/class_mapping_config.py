# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for parsing information from yaml in python accessible attributes for different
annotation handling classes like AnnotationClassMapper and several configuration classes
where a class mapping is used.
"""

import logging
from typing import List, Optional

import related
from config_builder.BaseConfigClass import BaseConfigClass

logger = logging.getLogger(__name__)


@related.mutable(strict=True)
class ClassMappingMappingConfig(BaseConfigClass):
    """Class for parsing information about a specific mapping"""

    input_class_name: str = related.StringField()
    output_class_name: str = related.StringField()


@related.mutable(strict=True)
class ClassMappingModelClassesConfig(BaseConfigClass):
    """Class for parsing information about classes"""

    class_name: str = related.StringField()
    class_id: int = related.IntegerField()


@related.mutable(strict=True)
class ClassMappingConfig(BaseConfigClass):
    """
    The ClassMappingConfig is relevant while parsing annotations files into data structures of the
    MLCVZoo. These data structures are then used to prepare the training / ground truth data
    for any model of the MLCVZoo. The class_mapping defines the number of classes a model knows
    and how the according model class IDs relate to class names (class_mapping.model_classes)
    that are parsed from the annotation files. Furthermore, the class_mapping allows to define
    a mapping of class names via the configuration attribute class_mapping.mapping. This can be
    used to fix typos that arise during the annotation process or to aggregate classes to a
    single super class, e.g. car, truck and motorcycle are aggregated as vehicle.

    EXAMPLE:

    model_classes:
      - class_name: "person"
        class_id: 0
      - class_name: "truck"
        class_id: 1
      - class_name: "car"
        class_id: 2
    """

    model_classes: List[ClassMappingModelClassesConfig] = related.SequenceField(
        ClassMappingModelClassesConfig
    )
    mapping: List[ClassMappingMappingConfig] = related.SequenceField(
        ClassMappingMappingConfig, required=False, default=[]
    )

    # class-names that are contained in "ignore_class_names" are forbidden to be
    # contained in any annotation object. This applies for all Classifications,
    # Bounding-Boxes and Segmentations, see src/mlcvzoo/api/data/annotation.py for
    # more details.
    # If a class-name of the "ignore_class_names" is parsed, the complete annotation
    # for this image will be ignored. Example use-cases are the usage of "bad-image"
    # to indicate images, that have been put in CVAT, but should be ignored for further
    # usage.
    ignore_class_names: List[str] = related.SequenceField(cls=str, default=[])

    number_model_classes: Optional[int] = related.ChildField(cls=int, required=False, default=None)
    number_classes: Optional[int] = related.ChildField(cls=int, required=False, default=None)

    def get_number_classes(self) -> int:
        """

        Returns:
            The number of model classes of this class mapping
        """
        return (
            self.number_model_classes
            if self.number_model_classes is not None
            else self.number_classes  # type: ignore
        )

    def check_values(self) -> bool:
        if self.number_classes is not None:
            logger.warning(
                "'number_classes' of config class ClassMappingConfig "
                "is deprecated and will be removed in "
                "future versions! Please use number_model_classes instead"
            )
            return True

        if self.number_model_classes is None:
            logger.error("'number_model_classes' of config class ClassMappingConfig is not set!")
            return False

        return True
