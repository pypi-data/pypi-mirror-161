# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module that holds the class for storing and accessing annotation class mapping information."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError, ForbiddenClassError
from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.reduction_mapping_config import (
    ReductionMappingConfig,
    ReductionMappingMappingConfig,
)

logger = logging.getLogger(__name__)


class AnnotationClassMapper:
    """
    Class for handling the mapping of class ids to class names during the parsing of annotation
    files and the inference of models. It is defined by the class_mapping and reduction_mapping
    configurations that are handed over in the constructor, please see
    :class:`mlcvzoo_base.configuration.class_mapping_config.ClassMappingConfig` and
    :class:`mlcvzoo_base.configuration.reduction_mapping_config.ReductionMappingConfig`
    """

    UNKNOWN_CLASS_NAME: str = "unknown_{}"

    def __init__(
        self,
        class_mapping: ClassMappingConfig,
        reduction_mapping: Optional[ReductionMappingConfig] = None,
    ) -> None:

        self.class_mapping_config: ClassMappingConfig = class_mapping

        # Dictionary that defines how a class ID during the parsing of annotation files
        # are mapped to a model class names. Please see for examples
        #
        # EXAMPLE:
        # {
        #     0: "person",
        #     1: "truck",
        #     2: "car",
        #     3: "lion",
        # }
        self.__annotation_class_id_to_model_class_name_map: Dict[
            int, str
        ] = self.__create_annotation_class_id_to_model_class_name_map(
            class_mapping_config=class_mapping,
        )

        # Dictionary that defines how a class names during the parsing of annotation files
        # are mapped to a model class IDs.
        #
        # EXAMPLE:
        # {
        #     "person": 0,
        #     "truck": 1,
        #     "car": 2,
        #     "lion": 3,
        # }
        self.__annotation_class_name_to_model_class_id_map: Dict[
            str, int
        ] = self.__create_annotation_class_name_to_model_class_id_map(
            annotation_class_id_to_model_class_name_map=self.__annotation_class_id_to_model_class_name_map
        )

        # Dictionary for mapping annotation class names to model class names. This
        # can be used to fix typos or to aggregate classes to a single model class.
        # The
        #
        # EXAMPLE:
        # {
        #     "Person": "person",
        #     "LKW": "truck",
        #     "tuck": "truck",
        #     "PKW": "car",
        # }
        self.__annotation_class_name_to_model_class_name_map: Dict[
            str, str
        ] = self.__create_annotation_class_name_to_model_class_name_map(
            class_mapping_config=self.class_mapping_config
        )

        # Dictionary for mapping / reducing the model class IDs to an output class identifier.
        # The model class IDs 1 and 2 are reduced to class ID 1 and class name vehicle.
        # The model class ID is used to create multiple outputs.
        #
        # EXAMPLE:
        #
        # {
        #     1: [ClassIdentifier(class_id=1, class_name="vehicle")],
        #     2: [ClassIdentifier(class_id=1, class_name="vehicle")],
        #     3: [
        #         ClassIdentifier(class_id=15, class_name="animal"),
        #         ClassIdentifier(class_id=16, class_name="cat"),
        #     ],
        # }
        self.__model_class_id_to_class_identifier_map: Dict[
            int, List[ClassIdentifier]
        ] = self.__create_model_class_id_to_class_identifier_map(
            annotation_class_id_to_model_class_name_map=self.__annotation_class_id_to_model_class_name_map,
            annotation_class_name_to_model_class_id_map=self.__annotation_class_name_to_model_class_id_map,
            reduction_mapping_config=reduction_mapping,
        )

        # Dictionary for mapping / reducing the model class names to an output class identifier.
        # The model class names "banana" and "cherry" are reduced to class ID 10
        # and class name "fruit".
        #
        # EXAMPLE:
        #
        # {
        #     "banana": [ClassIdentifier(class_id=10, class_name="fruit")],
        #     "cherry": [ClassIdentifier(class_id=10, class_name="fruit")],
        #     "lion": [
        #         ClassIdentifier(class_id=15, class_name="animal"),
        #         ClassIdentifier(class_id=16, class_name="cat"),
        #     ],
        # }
        self.__model_class_name_to_class_identifier_map: Dict[
            str, List[ClassIdentifier]
        ] = self.__create_model_class_name_to_class_identifier_map(
            annotation_class_id_to_model_class_name_map=self.__annotation_class_id_to_model_class_name_map,
            model_class_id_to_class_identifier_map=self.__model_class_id_to_class_identifier_map,
        )

        logger.debug("AnnotationClassMapper initialized")

    @property
    def num_classes(self) -> int:
        """
        Returns the number of classes the AnnotationMapper 'knows'.

        Returns:
            The number of classes the AnnotationMapper 'knows'.
        """

        return self.class_mapping_config.get_number_classes()

    @property
    def annotation_class_id_to_model_class_name_map(self) -> Dict[int, str]:
        return self.__annotation_class_id_to_model_class_name_map

    def get_model_class_names(self) -> List[str]:
        """
        Returns:
            All model class names as list.
        """

        class_ids: List[int] = list(self.__annotation_class_id_to_model_class_name_map.keys())

        # We have to provide the same class names we use later to
        # reverse translate to class ids. Python guarantees the order
        # of insertion, not alphabetical or other orders, so we have
        # to sort the keys
        class_ids.sort()

        class_names: List[str] = []
        for class_id in class_ids:
            class_names.append(self.__annotation_class_id_to_model_class_name_map[class_id])

        return class_names

    @staticmethod
    def get_coco_classes_id_dict(categories: List[Dict[str, Any]]) -> Dict[int, str]:
        """

        Args:
            categories: Dictionary of COCO formatted category (or class) ids and names

        Returns:
            Dictionary of class id values to class names
        """

        __classes_id_dict: Dict[int, str] = dict()

        for category in categories:
            class_id = category["id"]
            class_name = category["name"]

            __classes_id_dict[class_id] = class_name

        return __classes_id_dict

    def map_annotation_class_name_to_model_class_name(self, class_name: str) -> str:
        """
        Map the given class name to a model class name according to
        the defined mapping in the configuration.

        Args:
            class_name: The class name to map

        Returns:
            The mapped class name

        Raises:
            ForbiddenClassError when the class_name matches a class name in the
            ignore_class_names list of the configuration.

            ClassMappingNotFoundError when the class_name can not be mapped to a model class
            name.
        """

        if not self.is_valid_class(class_name=class_name):
            raise ForbiddenClassError(invalid_class=class_name)

        # Try to find a valid mapping for the given input-key
        if class_name in self.__annotation_class_name_to_model_class_name_map:
            return self.__annotation_class_name_to_model_class_name_map[class_name]

        raise ClassMappingNotFoundError(
            f"Could not find a valid mapping for class-name='{class_name}'"
        )

    def map_annotation_class_name_to_model_class_id(self, class_name: str) -> int:
        """
        Map the given class name to a model class ID according to
        the defined mapping in the configuration.

        Args:
            class_name: The class name to map

        Returns:
            The mapped class ID

        Raises:
            ForbiddenClassError when the class_name matches a class name in the
            ignore_class_names list of the configuration.

            ClassMappingNotFoundError when the class_name can not be mapped to a model class
            name.
        """

        model_class_name = self.map_annotation_class_name_to_model_class_name(
            class_name=class_name
        )
        # Try to find a valid mapping for the given input-key
        if model_class_name in self.__annotation_class_name_to_model_class_id_map:
            return self.__annotation_class_name_to_model_class_id_map[model_class_name]

        raise ClassMappingNotFoundError(
            f"Could not find a valid mapping for class-name='{class_name}'"
        )

    def map_annotation_class_id_to_model_class_name(self, class_id: int) -> str:
        """
        Map the given class id to a model class name according to
        the defined mapping in the configuration.

        Args:
            class_id: The class id to map

        Returns:
            The mapped class name

        Raises:
            ClassMappingNotFoundError when the class_name can not be mapped to a model class
            name.
        """

        # Try to find a valid mapping for the given input-key
        if class_id in self.__annotation_class_id_to_model_class_name_map:
            return self.__annotation_class_id_to_model_class_name_map[class_id]

        raise ClassMappingNotFoundError(
            f"Could not find a valid mapping for class-id='{class_id}'"
        )

    def map_model_class_id_to_output_class_identifier(
        self, class_id: int
    ) -> List[ClassIdentifier]:
        """
        Map the given class id to a list of ClassIdentifiers according to
        the defined mapping in the configuration.

        Args:
            class_id: The class id to map

        Returns:
            The list of ClassIdentifiers

        Raises:
            ClassMappingNotFoundError when the class_name can not be mapped to a model class
            name.
        """

        # Try to find a valid mapping for the given input-key
        if class_id in self.__model_class_id_to_class_identifier_map:
            return self.__model_class_id_to_class_identifier_map[class_id]

        raise ClassMappingNotFoundError(
            f"Could not find a valid mapping for class-id='{class_id}'"
        )

    def map_model_class_name_to_output_class_identifier(
        self, class_name: str
    ) -> List[ClassIdentifier]:
        """
        Map the given class name to a list of ClassIdentifiers according to
        the defined mapping in the configuration.

        Args:
            class_name: The class name to map

        Returns:
            The list of ClassIdentifiers

        Raises:
            ClassMappingNotFoundError when the class_name can not be mapped to a model class
            name.
        """

        # Try to find a valid mapping for the given input-key
        if class_name in self.__model_class_name_to_class_identifier_map:
            return self.__model_class_name_to_class_identifier_map[class_name]

        raise ClassMappingNotFoundError(
            f"Could not find a valid mapping for class-name='{class_name}'"
        )

    def is_valid_class(self, class_name: str) -> bool:
        """
        Checks whether a class name should be ignored by the AnnotationClassMapper

        Args:
            class_name: String, a name of a class

        Returns:
            Bool, true if the name is not listed in the 'ignore_class_name' attribute
        """

        # A class is only valid, if is it not contained in the
        # ignore_class_names list.
        if class_name in self.class_mapping_config.ignore_class_names:
            return False
        else:
            return True

    @staticmethod
    def __create_annotation_class_name_to_model_class_name_map(
        class_mapping_config: ClassMappingConfig,
    ) -> Dict[str, str]:
        """
        Create a dictionary for mapping a class-name as string that is parsed from annotation data,
        to the respective model class-name as string.

        There are the following restrictions:

        The attribute class_mapping_config.mapping can only define mappings to
        class names are specified in the attribute class_mapping_config.model_classes.

        Args:
            class_mapping_config: configuration object that provides the relevant
                                  mapping information

        Returns:
            A dictionary representing the mapping
        """

        class_name_mapping: Dict[str, str] = {}

        model_class_names: List[str] = []

        for model_class in class_mapping_config.model_classes:
            model_class_names.append(model_class.class_name)
            class_name_mapping[model_class.class_name] = model_class.class_name

        for index, mapping in enumerate(class_mapping_config.mapping):
            if mapping.output_class_name in model_class_names:
                class_name_mapping[mapping.input_class_name] = mapping.output_class_name
            else:
                raise ValueError(
                    "Invalid mapping config entry: "
                    "mapping[%d].output_class_name='%s', "
                    "but has to be one of '%s'"
                    % (index, mapping.output_class_name, model_class_names)
                )

        return class_name_mapping

    @staticmethod
    def __create_annotation_class_id_to_model_class_name_map(
        class_mapping_config: ClassMappingConfig,
    ) -> Dict[int, str]:
        """
        Create a dictionary for mapping annotation class IDs to model class names.

        There are the following features and restrictions:

        In case the configuration attribute class_mapping_config.model_classes does not contain
        an entry for every class ID in the range of 0, ..., num_classes, a default mapping
        will be created the maps the respective class ID to the string "unknown_ID".

        The configuration attribute class_mapping_config.model_classes can only contain class IDs
        that are in the range of 0, ..., num_classes.

        Args:
            class_mapping_config: The configuration object that defines the mapping

        Returns:
            The created dictionary
        """

        invalid_class_ids: List[int] = []
        classes_id_dict: Dict[int, str] = {}

        for model_class in class_mapping_config.model_classes:
            if model_class.class_id > class_mapping_config.get_number_classes():
                invalid_class_ids.append(model_class.class_id)
                continue

            if model_class.class_id not in classes_id_dict:
                classes_id_dict[model_class.class_id] = model_class.class_name
            else:
                raise ValueError(
                    "Duplicate class_id='%s' is not allowed in model_classes"
                    % model_class.class_id
                )

        # Generate unknown classes string. This ensures that one
        # is not forced to define all class-names for the maximum number of classes
        for class_id in range(0, class_mapping_config.get_number_classes()):
            if class_id not in classes_id_dict:
                classes_id_dict[class_id] = AnnotationClassMapper.UNKNOWN_CLASS_NAME.format(
                    class_id
                )

        if len(invalid_class_ids) > 0:
            raise ValueError(
                "Found class_ids='%s' that exceed the number_classes=%d"
                % (invalid_class_ids, class_mapping_config.get_number_classes())
            )

        return classes_id_dict

    @staticmethod
    def __create_annotation_class_name_to_model_class_id_map(
        annotation_class_id_to_model_class_name_map: Dict[int, str]
    ) -> Dict[str, int]:
        """
        Create a dictionary for mapping annotation class names to model class IDs.

        It is the reverse of an annotation_class_id_to_model_class_name_map.

        Args:
            annotation_class_id_to_model_class_name_map: A dictionary that defines a mapping from
                                                         annotation class IDs to model class names

        Returns:
            The reversed annotation_class_id_to_model_class_name_map
        """

        return dict(
            map(reversed, annotation_class_id_to_model_class_name_map.items())  # type: ignore
        )

    @staticmethod
    def __create_model_class_id_to_class_identifier_map(
        annotation_class_id_to_model_class_name_map: Dict[int, str],
        annotation_class_name_to_model_class_id_map: Dict[str, int],
        reduction_mapping_config: Optional[ReductionMappingConfig],
    ) -> Dict[int, List[ClassIdentifier]]:

        default_model_class_id_to_class_identifier_map: Dict[int, List[ClassIdentifier]] = {}
        model_class_id_to_class_identifier_map: Dict[int, List[ClassIdentifier]] = {}

        for (
            class_id,
            model_class_name,
        ) in annotation_class_id_to_model_class_name_map.items():
            default_model_class_id_to_class_identifier_map[class_id] = [
                ClassIdentifier(class_id=class_id, class_name=model_class_name)
            ]

        output_class_id_map: Dict[int, ReductionMappingMappingConfig] = {}
        output_class_name_map: Dict[str, ReductionMappingMappingConfig] = {}

        if reduction_mapping_config is not None:
            for index, mapping_entry in enumerate(reduction_mapping_config.mapping):
                if mapping_entry.output_class_id in output_class_id_map:
                    raise ValueError(
                        "Duplicate definition for output-class-id='%s' "
                        "for mapping_entry at index='%s':\n"
                        " - already stored mapping-entry='%s'\n"
                        " - current mapping-entry='%s'"
                        % (
                            mapping_entry.output_class_id,
                            index,
                            output_class_id_map[mapping_entry.output_class_id],
                            mapping_entry,
                        ),
                    )

                if mapping_entry.output_class_name in output_class_name_map:
                    raise ValueError(
                        "Duplicate definition for output-class-name='%s' "
                        "for mapping_entry at index='%s':\n"
                        " - already stored mapping-entry='%s'\n"
                        " - current mapping-entry='%s'"
                        % (
                            mapping_entry.output_class_name,
                            index,
                            output_class_name_map[mapping_entry.output_class_name],
                            mapping_entry,
                        ),
                    )

                output_class_id_map[mapping_entry.output_class_id] = mapping_entry
                output_class_name_map[mapping_entry.output_class_name] = mapping_entry

                if mapping_entry.model_class_ids is not None:
                    model_class_id_to_class_identifier_map.update(
                        AnnotationClassMapper.__update_model_class_id_to_class_identifier_map_from_model_class_ids(
                            model_class_id_to_class_identifier_map=model_class_id_to_class_identifier_map,
                            annotation_class_id_to_model_class_name_map=annotation_class_id_to_model_class_name_map,
                            mapping_entry=mapping_entry,
                            index=index,
                        )
                    )

                if mapping_entry.model_class_names is not None:
                    model_class_id_to_class_identifier_map.update(
                        AnnotationClassMapper.__update_model_class_id_to_class_identifier_map_from_model_class_names(
                            model_class_id_to_class_identifier_map=model_class_id_to_class_identifier_map,
                            annotation_class_name_to_model_class_id_map=annotation_class_name_to_model_class_id_map,
                            mapping_entry=mapping_entry,
                            index=index,
                        )
                    )

        default_model_class_id_to_class_identifier_map.update(
            model_class_id_to_class_identifier_map
        )

        return default_model_class_id_to_class_identifier_map

    @staticmethod
    def __update_model_class_id_to_class_identifier_map_from_model_class_ids(
        model_class_id_to_class_identifier_map: Dict[int, List[ClassIdentifier]],
        annotation_class_id_to_model_class_name_map: Dict[int, str],
        mapping_entry: ReductionMappingMappingConfig,
        index: int,
    ) -> Dict[int, List[ClassIdentifier]]:

        assert mapping_entry.model_class_ids is not None

        error_class_ids: List[int] = []
        # Any model-class-id defines a mapping from class-id to a ClassIdentifier
        for model_class_id in mapping_entry.model_class_ids:
            if model_class_id not in annotation_class_id_to_model_class_name_map:
                error_class_ids.append(model_class_id)
                continue

            class_identifier = ClassIdentifier(
                class_id=mapping_entry.output_class_id,
                class_name=mapping_entry.output_class_name,
            )

            if model_class_id not in model_class_id_to_class_identifier_map:
                model_class_id_to_class_identifier_map[model_class_id] = [class_identifier]
            else:
                model_class_id_to_class_identifier_map[model_class_id].append(class_identifier)

        if len(error_class_ids) > 0:
            raise ValueError(
                "Invalid reduction-mapping config entry:\n"
                " - mapping[%d].model_class_ids='%s'\n"
                " - it can only contain values of: '%s'\n"
                " - wrong model_class_ids: '%s'"
                % (
                    index,
                    mapping_entry.model_class_ids,
                    list(annotation_class_id_to_model_class_name_map.keys()),
                    error_class_ids,
                )
            )

        return model_class_id_to_class_identifier_map

    @staticmethod
    def __update_model_class_id_to_class_identifier_map_from_model_class_names(
        model_class_id_to_class_identifier_map: Dict[int, List[ClassIdentifier]],
        annotation_class_name_to_model_class_id_map: Dict[str, int],
        mapping_entry: ReductionMappingMappingConfig,
        index: int,
    ) -> Dict[int, List[ClassIdentifier]]:

        assert mapping_entry.model_class_names is not None

        error_class_names: List[str] = []
        for model_class_name in mapping_entry.model_class_names:

            if model_class_name in annotation_class_name_to_model_class_id_map:
                model_class_id = annotation_class_name_to_model_class_id_map[model_class_name]
            else:
                error_class_names.append(model_class_name)
                continue

            class_identifier = ClassIdentifier(
                class_id=mapping_entry.output_class_id,
                class_name=mapping_entry.output_class_name,
            )

            if model_class_id not in model_class_id_to_class_identifier_map:
                model_class_id_to_class_identifier_map[model_class_id] = [class_identifier]
            else:
                model_class_id_to_class_identifier_map[model_class_id].append(class_identifier)

        if len(error_class_names) > 0:
            raise ValueError(
                "Invalid reduction-mapping config entry:\n"
                " - mapping[%d].model_class_names='%s'\n"
                " - it can only contain values of: '%s'\n"
                " - wrong model_class_names: '%s'"
                % (
                    index,
                    mapping_entry.model_class_names,
                    list(annotation_class_name_to_model_class_id_map.keys()),
                    error_class_names,
                )
            )

        return model_class_id_to_class_identifier_map

    @staticmethod
    def __create_model_class_name_to_class_identifier_map(
        annotation_class_id_to_model_class_name_map: Dict[int, str],
        model_class_id_to_class_identifier_map: Dict[int, List[ClassIdentifier]],
    ) -> Dict[str, List[ClassIdentifier]]:

        return {
            annotation_class_id_to_model_class_name_map[model_class_id]: class_identifier
            for model_class_id, class_identifier in model_class_id_to_class_identifier_map.items()
        }
