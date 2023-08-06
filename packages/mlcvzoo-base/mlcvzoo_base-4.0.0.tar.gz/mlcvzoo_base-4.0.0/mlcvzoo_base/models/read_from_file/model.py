# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for creating a look-up model based on existing annotations"""
import hashlib
import logging
import os
import typing
from abc import ABC
from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union

import cv2
from nptyping import Int, NDArray, Shape

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.segmentation import Segmentation
from mlcvzoo_base.api.interfaces import Classifiable
from mlcvzoo_base.api.model import (
    ClassificationModel,
    Model,
    ObjectDetectionModel,
    SegmentationModel,
)
from mlcvzoo_base.configuration.utils import (
    create_configuration as create_basis_configuration,
)
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationHandler
from mlcvzoo_base.models.read_from_file.configuration import ReadFromFileConfig

logger = logging.getLogger(__name__)

ImageType = NDArray[Shape["Height, Width, Any"], Int]

ModelType = TypeVar(
    "ModelType",
    ClassificationModel[ReadFromFileConfig, Union[str, ImageType]],
    ObjectDetectionModel[ReadFromFileConfig, Union[str, ImageType]],
    SegmentationModel[ReadFromFileConfig, Union[str, ImageType]],
)


class ReadFromFileModel(
    Model,  # type: ignore
    Classifiable,
    ABC,
    Generic[ModelType],
):
    """
    Simple Model which can be used as fast Online detector.
    It takes an "AnnotationHandlerConfig" and parses all annotations
    based on this config into a datastructure. At prediction step it
    simply looks up the annotation based on the image-path information.

    NOTE: The ReadFromFileModel is only a 'Model'. In order to become a model of a
          dedicated type like ClassificationModel or ObjectDetectionModel, the
          Subclasses of a ReadFromFileModel have to inherit not only from the
          ReadFromFileModel but also from the dedicated type itself.

    NOTE: The constructor of the super class Model will not be called since
          the ReadFromFileModel is an abstract super class and therefore is
          not intended to be instantiated. But make sure to call the Model
          constructor in one of the implementing subclasses.
    """

    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[ReadFromFileConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):

        self.configuration: ReadFromFileConfig = ReadFromFileModel.create_configuration(
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )
        Model.__init__(
            self,
            unique_name=os.path.basename(from_yaml).replace(".yaml", ""),
            configuration=self.configuration,
            init_for_inference=True,
        )
        Classifiable.__init__(
            self,
            mapper=AnnotationClassMapper(
                class_mapping=self.configuration.class_mapping,
                reduction_mapping=self.configuration.reduction_class_mapping,
            ),
        )

        if self.configuration.annotation_handler_config.class_mapping is not None:
            logger.warning(
                "Explicit annotation_handler_config.class_mapping is not "
                "supported in a models context anymore!"
            )

        if self.configuration.annotation_handler_config.reduction_class_mapping is not None:
            logger.warning(
                "Explicit annotation_handler_config.reduction_class_mapping is not "
                "supported in a models context anymore!"
            )

        self.annotation_handler = AnnotationHandler(
            mapper=self.mapper,
            configuration=self.configuration.annotation_handler_config,
        )

        self.annotations_dict: Dict[str, BaseAnnotation] = self.initialize_annotations_dict(
            annotations=self.annotation_handler.parse_inference_annotations()
        )

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[ReadFromFileConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> ReadFromFileConfig:
        return typing.cast(
            ReadFromFileConfig,
            create_basis_configuration(
                configuration_class=ReadFromFileConfig,
                from_yaml=from_yaml,
                input_configuration=configuration,
                string_replacement_map=string_replacement_map,
            ),
        )

    @property
    def num_classes(self) -> int:
        return self.annotation_handler.mapper.num_classes

    def get_classes_id_dict(self) -> Dict[int, str]:
        return self.annotation_handler.mapper.annotation_class_id_to_model_class_name_map

    @staticmethod
    def create_image_hash(data_item: Union[str, ImageType]) -> str:
        if isinstance(data_item, str):
            image = cv2.imread(data_item)
        else:
            image = data_item

        return hashlib.md5(image).hexdigest()

    def initialize_annotations_dict(
        self, annotations: List[BaseAnnotation]
    ) -> Dict[str, BaseAnnotation]:
        """
        Create a hashed annotation dictionary from a given list of annotations

        Args:
            annotations: list of annotations

        Returns:
            a hashed dict with annotations
        """
        annotations_dict: Dict[str, BaseAnnotation] = {}

        for annotation in annotations:

            if annotation.image_path in annotations_dict:
                logger.warning(
                    "Duplicate annotation data for image '%s'.\n"
                    "Check your annotation-handler configuration!",
                    annotation.image_path,
                )
            if self.configuration.use_image_name_hash:
                annotations_dict[
                    os.path.basename(annotation.annotation_path).replace(".xml", "")
                ] = annotation
            else:
                annotations_dict[annotation.image_path] = annotation
                annotations_dict[self.create_image_hash(annotation.image_path)] = annotation

        return annotations_dict


class ReadFromFileClassificationModel(
    ClassificationModel[ReadFromFileConfig, Union[str, ImageType]],
    ReadFromFileModel[ClassificationModel[ReadFromFileConfig, Union[str, ImageType]]],
):
    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[ReadFromFileConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):
        ReadFromFileModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )
        ClassificationModel.__init__(
            self,
            unique_name=os.path.basename(from_yaml).replace(".yaml", ""),
            configuration=self.configuration,
            mapper=self.mapper,
            init_for_inference=True,
        )

    def predict(
        self, data_item: Union[str, ImageType]
    ) -> Tuple[Union[str, ImageType], List[Classification]]:
        if isinstance(data_item, str):
            data_hash = data_item
        else:
            data_hash = self.create_image_hash(data_item)

        if data_hash in self.annotations_dict:
            classifications = self.annotations_dict[data_hash].classifications
            return data_item, classifications

        raise ValueError("data_item='%s' not in lookup dict of the ReadFromFileModel" % data_item)


class ReadFromFileObjectDetectionModel(
    ObjectDetectionModel[ReadFromFileConfig, Union[str, ImageType]],
    ReadFromFileModel[ObjectDetectionModel[ReadFromFileConfig, Union[str, ImageType]]],
):
    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[ReadFromFileConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):
        ReadFromFileModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )
        ObjectDetectionModel.__init__(
            self,
            unique_name=os.path.basename(from_yaml).replace(".yaml", ""),
            configuration=self.configuration,
            mapper=self.mapper,
            init_for_inference=True,
        )

    def predict(
        self, data_item: Union[str, ImageType]
    ) -> Tuple[Union[str, ImageType], List[BoundingBox]]:

        include_segmentations: bool = self.configuration.include_segmentations

        if isinstance(data_item, str):
            data_hash = data_item
        else:
            data_hash = self.create_image_hash(data_item)

        if data_hash in self.annotations_dict:
            bounding_boxes = self.annotations_dict[data_hash].get_bounding_boxes(
                include_segmentations=include_segmentations
            )
            return data_item, bounding_boxes

        raise ValueError("data_item='%s' not in lookup dict of the ReadFromFileModel" % data_item)


class ReadFromFileSegmentationModel(
    SegmentationModel[ReadFromFileConfig, Union[str, ImageType]],
    ReadFromFileModel[SegmentationModel[ReadFromFileConfig, Union[str, ImageType]]],
):
    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[ReadFromFileConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):
        ReadFromFileModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )
        SegmentationModel.__init__(
            self,
            unique_name=os.path.basename(from_yaml).replace(".yaml", ""),
            configuration=self.configuration,
            mapper=self.mapper,
            init_for_inference=True,
        )

    def predict(
        self, data_item: Union[str, ImageType]
    ) -> Tuple[Union[str, ImageType], List[Segmentation]]:

        if isinstance(data_item, str):
            data_hash = data_item
        else:
            data_hash = self.create_image_hash(data_item)

        if data_hash in self.annotations_dict:
            segmentations = self.annotations_dict[data_hash].segmentations

            return data_item, segmentations

        raise ValueError("data_item='%s' not in lookup dict of the ReadFromFileModel" % data_item)
