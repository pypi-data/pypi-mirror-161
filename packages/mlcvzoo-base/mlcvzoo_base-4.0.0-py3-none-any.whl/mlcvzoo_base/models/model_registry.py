# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module to put together different models"""
import importlib
import inspect
import logging
from typing import Any, Dict, List, Optional, Type

from related import to_dict

from mlcvzoo_base.api.model import ConfigurationType, DataType, Model, PredictionType
from mlcvzoo_base.configuration.model_config import ModelConfig
from mlcvzoo_base.configuration.replacement_config import (
    STRING_REPLACEMENT_MAP_KEY,
    ReplacementConfig,
)
from mlcvzoo_base.models.read_from_file.model import (
    ReadFromFileClassificationModel,
    ReadFromFileObjectDetectionModel,
    ReadFromFileSegmentationModel,
)

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Reads model configurations and provides a list of models for later use, e.g. to
    run overall evaluation or training
    """

    def __init__(self) -> None:
        self.model_registry: Dict[  # type: ignore
            str, Type[Model[PredictionType, ConfigurationType, DataType]]
        ] = {}

        self.register_model(
            model_type_name="read_from_file_classification",
            model_constructor=ReadFromFileClassificationModel,
        )
        self.register_model(
            model_type_name="read_from_file_object_detection",
            model_constructor=ReadFromFileObjectDetectionModel,
        )
        self.register_model(
            model_type_name="read_from_file_segmentation",
            model_constructor=ReadFromFileSegmentationModel,
        )
        self.register_external_model(
            model_type_name="yolox",
            model_constructor="YOLOXModel",
            package_name="mlcvzoo_yolox.model",
        )
        self.register_external_model(
            model_type_name="yolov4_darknet",
            model_constructor="DarknetDetectionModel",
            package_name="mlcvzoo_darknet.model",
        )
        self.register_external_model(
            model_type_name="mmdetection_object_detection",
            model_constructor="MMObjectDetectionModel",
            package_name="mlcvzoo_mmdetection.object_detection_model",
        )
        self.register_external_model(
            model_type_name="mmocr_text_detection",
            model_constructor="MMOCRTextDetectionModel",
            package_name="mlcvzoo_mmocr.text_detection_model",
        )
        self.register_external_model(
            model_type_name="mmocr_text_recognition",
            model_constructor="MMOCRTextRecognitionModel",
            package_name="mlcvzoo_mmocr.text_recognition_model",
        )
        self.register_external_model(
            model_type_name="tf_classification_custom_block",
            model_constructor="CustomBlockModel",
            package_name="mlcvzoo_tf_classification.model",
        )
        self.register_external_model(
            model_type_name="tf_classification_xception",
            model_constructor="XceptionModel",
            package_name="mlcvzoo_tf_classification.model",
        )

    def register_external_model(
        self, model_type_name: str, model_constructor: str, package_name: str
    ) -> None:
        """
        Register an external model
        Args:
            model_type_name: name of the model to register
            model_constructor: name of the constructor of the model to register
            package_name: the full package to import to call the constructor

        Returns:
            Nothing
        """
        try:
            # pylint: disable=c0415
            module = importlib.import_module(package_name)
        except ImportError:
            module = None

        if module:
            self.register_model(
                model_type_name=model_type_name,
                model_constructor=module.__dict__[model_constructor],
            )
        else:
            logger.info(
                "Optional model '%s' (%s.%s) not available"
                % (model_type_name, package_name, model_constructor)
            )

    def register_model(
        self, model_type_name: str, model_constructor: Any, force: bool = False
    ) -> None:

        if not force and model_type_name in self.model_registry:
            raise KeyError(
                f"{model_type_name} is already registered model registry"
                f"in {self.model_registry}"
            )

        self.model_registry[model_type_name] = model_constructor

    def init_model(
        self,
        model_config: ModelConfig,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> Model[PredictionType, ConfigurationType, DataType]:
        """
        Generic method for instantiating any model that is registered in the model-registry

        Args:
            model_config: The model configuration defining which model should be initialized
            string_replacement_map: (Optional) A dictionary that defines placeholders which can
                                    be used while parsing a configuration file. They can be
                                    understood as variables that can be used to define configs
                                    that are valid across multiple devices.

                                    If no string_replacement_map a default map based on the
                                    ReplacementConfig will be created and used. This allows
                                    to use the attributes of the ReplacementConfig to be
                                    replaced by os environment variables.

        Returns:
            The created model instance
        """

        if model_config.class_type in self.model_registry.keys():
            model: Model[PredictionType, ConfigurationType, DataType]
            model_type = self.model_registry[model_config.class_type]

            init_params: List[Any] = list(inspect.getfullargspec(model_type.__init__).args)
            # We don't need self as parameter in the configuration
            init_params.remove("self")

            if (
                STRING_REPLACEMENT_MAP_KEY not in model_config.constructor_parameters
                and STRING_REPLACEMENT_MAP_KEY in init_params
            ):
                if string_replacement_map is None:
                    string_replacement_map = to_dict(ReplacementConfig())
                model_config.constructor_parameters[
                    STRING_REPLACEMENT_MAP_KEY
                ] = string_replacement_map

            try:
                model = model_type(**model_config.constructor_parameters)
            except TypeError as e:
                logger.error(
                    "Please provide the parameters "
                    "%s, as specified for %s, "
                    "in your yaml configuration",
                    init_params,
                    model_type,
                )
                raise e
        else:
            message = (
                f"The model '{model_config.class_type}' is not registered! \n"
                f"The registered models are: {self.model_registry.keys()}"
            )

            logger.error(message)
            raise ValueError(message)

        return model
