# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for creating machine learning models in the MLCVZoo"""

from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, Tuple, TypeVar

from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.ocr_perception import OCRPerception
from mlcvzoo_base.api.data.segmentation import PolygonType, Segmentation
from mlcvzoo_base.api.interfaces import Classifiable, Perception
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats

DataType = TypeVar("DataType")
PredictionType = TypeVar("PredictionType", bound=Perception)
ConfigurationType = TypeVar("ConfigurationType")


class Model(ABC, Generic[PredictionType, ConfigurationType, DataType]):
    """
    A model to detect objects, like things from an image or
    characters from a license plate or book.
    """

    def __init__(
        self,
        unique_name: str,
        configuration: ConfigurationType,
        init_for_inference: bool,
    ):
        """
        Constructor creates a new model instance.
        This must be called by subclass constructors to define a unique model name.
        """
        self.name: str = unique_name
        self.configuration: ConfigurationType = configuration

        if init_for_inference:
            self._init_inference_model()
        else:
            self._init_training_model()

    def _init_inference_model(self) -> None:
        # Not every model differentiates between an initialization for inference and training
        pass

    def _init_training_model(self) -> None:
        # Not every model differentiates between an initialization for inference and training
        pass

    def get_name(self) -> str:
        """
        Returns:
            The (unique) name for the model subclass. Do not override this method.
        """
        return self.name

    def get_configuration(self) -> ConfigurationType:
        """
        Returns:
            The configuration for the model subclass instance.The model is responsible
            to read and create its configuration, e.g. from a file.
        """
        return self.configuration

    @staticmethod
    @abstractmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[ConfigurationType] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> ConfigurationType:
        """
        The model is responsible to provide a configuration object. This encapsulates all
        relevant parameters for the model. The configuration will either be parsed from the
        file given by the "from_yaml" parameter or the provided configuration object is simply
        passed-trough.

        NOTE: This method is meant to be integrated and used with the config-builder module.

        Args:
            from_yaml: (Optional) Parse the configuration from this file path
            configuration: (Optional) When provided this configuration object is passed-trough.
                           It is leveraged as a convenience option.
            string_replacement_map: A dictionary that defines placeholders which can be used
                                    while parsing the file. They can be understood as variables
                                    that can be used to define configs that are valid across
                                    multiple devices.

        Returns:
            The created configuration object for this model
        """
        raise NotImplementedError("Must be implemented by sub-class: create_configuration(...).")

    @abstractmethod
    def predict(self, data_item: DataType) -> Tuple[DataType, List[PredictionType]]:
        """
        The method predicts a list of classifications from a given data item.

        Args:
            data_item: The data item as input for the model

        Returns:
            A tuple containing the input value and its predictions
        """
        raise NotImplementedError("Must be implemented by sub-class: predict(...).")

    def predict_many(
        self, data_items: List[DataType]
    ) -> List[Tuple[DataType, List[PredictionType]]]:
        """
        The method predicts a list of classifications from a given data item.

        Args:
            data_items: The data item as input for the model

        Returns:
            A tuple containing the input value and its predictions
        """
        results: List[Tuple[DataType, List[PredictionType]]] = []
        for data_item in data_items:
            results.append(self.predict(data_item=data_item))

        return results


class ClassificationModel(
    Model[Classification, ConfigurationType, DataType],
    Classifiable,
):
    """
    Class that declares the generic method predict(...) for all models that are
    performing the computer vision task "Image Classification".
    """

    def __init__(
        self,
        unique_name: str,
        configuration: ConfigurationType,
        mapper: AnnotationClassMapper,
        init_for_inference: bool,
    ):
        Classifiable.__init__(self, mapper=mapper)
        Model.__init__(
            self,
            unique_name=unique_name,
            configuration=configuration,
            init_for_inference=init_for_inference,
        )

    @abstractmethod
    def predict(self, data_item: DataType) -> Tuple[DataType, List[Classification]]:
        raise NotImplementedError("Must be implemented by sub-class: predict(...).")


class ObjectDetectionModel(
    Model[BoundingBox, ConfigurationType, DataType],
    Classifiable,
):
    """
    Class that declares the generic method predict(...) for all models that are
    performing the computer vision task "Object Detection".
    """

    def __init__(
        self,
        unique_name: str,
        configuration: ConfigurationType,
        mapper: AnnotationClassMapper,
        init_for_inference: bool,
    ):
        Classifiable.__init__(self, mapper=mapper)
        Model.__init__(
            self,
            unique_name=unique_name,
            configuration=configuration,
            init_for_inference=init_for_inference,
        )

    @abstractmethod
    def predict(self, data_item: DataType) -> Tuple[DataType, List[BoundingBox]]:
        raise NotImplementedError("Must be implemented by sub-class: predict(...).")

    @staticmethod
    def build_bounding_boxes(
        box_list: Tuple[int, int, int, int],
        class_identifiers: List[ClassIdentifier],
        model_class_identifier: ClassIdentifier,
        score: float = 1.0,
        box_format: str = ObjectDetectionBBoxFormats.XYXY,
        difficult: bool = False,
        occluded: bool = False,
        content: str = "",
        src_shape: Optional[Tuple[int, int]] = None,
        dst_shape: Optional[Tuple[int, int]] = None,
    ) -> List[BoundingBox]:
        """
        Creates a list of BoundingBox objects with the given specifications. The bounding box
        can be scaled by defining a src shape and a destination shape. One bounding box per
        ClassIdentifier in the given list will be created.

        Args:
            box_list: object as 4D array containing bounding box information, needed
                      to create a Box object
            class_identifiers: List of ClassIdentifier objects
            model_class_identifier: List of ClassIdentifier objects
            score: classification score of the class that is captured within the bounding box
            box_format: specify the way for parsing the box argument
            difficult: Whether the object is difficult
            occluded: Whether the object is occluded
            content: content of the boxed area, e.g. the text stated in it
            src_shape: source shape for applying a scaling of the box (height, width)
            dst_shape: destination shape for applying a scaling of the box (height, width)

        Returns:
            The created list of BoundingBoxes
        """

        box = Box.init_format_based(
            box_list=box_list,
            box_format=box_format,
            src_shape=src_shape,
            dst_shape=dst_shape,
        )

        bounding_boxes: List[BoundingBox] = []

        for class_identifier in class_identifiers:
            bounding_boxes.append(
                BoundingBox(
                    difficult=difficult,
                    occluded=occluded,
                    content=content,
                    class_identifier=class_identifier,
                    model_class_identifier=model_class_identifier,
                    score=score,
                    box=box,
                )
            )

        return bounding_boxes


class SegmentationModel(Model[Segmentation, ConfigurationType, DataType], Classifiable):
    """
    Class that declares the generic method predict(...) for all models that are
    performing the computer vision task "Instance Segmentation".
    """

    def __init__(
        self,
        unique_name: str,
        configuration: ConfigurationType,
        mapper: AnnotationClassMapper,
        init_for_inference: bool,
    ):
        Classifiable.__init__(self, mapper=mapper)
        Model.__init__(
            self,
            unique_name=unique_name,
            configuration=configuration,
            init_for_inference=init_for_inference,
        )

    @abstractmethod
    def predict(self, data_item: DataType) -> Tuple[DataType, List[Segmentation]]:
        raise NotImplementedError("Must be implemented by sub-class: predict(...).")

    @staticmethod
    def build_segmentations(
        polygon: PolygonType,
        class_identifiers: List[ClassIdentifier],
        model_class_identifier: Optional[ClassIdentifier] = None,
        score: float = 1.0,
        difficult: bool = False,
        occluded: bool = False,
        content: str = "",
    ) -> List[Segmentation]:
        """
        Creates a list of Segmentation objects with the given specifications.
        One Segmentation per ClassIdentifier in the given list will be created.

        Args:
            polygon: a list of points 2D points (tuples) that form the polygon
            class_identifiers: List of ClassIdentifier objects
            model_class_identifier: List of ClassIdentifier objects
            score: classification score of the area the object boxes
            difficult: Whether the object is difficult
            occluded: Whether the object is occluded
            content:  content of the captured area, e.g. the text stated in it

        Returns:
            A Segmentation Object
        """

        box: Box = Segmentation.polygon_to_box(polygon=polygon)

        segmentations: List[Segmentation] = []

        for class_identifier in class_identifiers:
            segmentations.append(
                Segmentation(
                    class_identifier=class_identifier,
                    model_class_identifier=model_class_identifier,
                    score=score,
                    polygon=polygon,
                    difficult=difficult,
                    occluded=occluded,
                    content=content,
                    box=box,
                )
            )

        return segmentations


class OCRModel(Model[OCRPerception, ConfigurationType, DataType]):
    """
    Class that declares the generic method predict(...) for all models that are
    performing the computer vision task "Text Recognition" which is a subfield of
    Optical Character Recognition (OCR).
    """

    def __init__(
        self,
        unique_name: str,
        configuration: ConfigurationType,
        init_for_inference: bool,
    ):
        Model.__init__(
            self,
            unique_name=unique_name,
            configuration=configuration,
            init_for_inference=init_for_inference,
        )

    @abstractmethod
    def predict(self, data_item: DataType) -> Tuple[DataType, List[OCRPerception]]:
        raise NotImplementedError("Must be implemented by sub-class: predict(...).")
