# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

from typing import Dict, List, Optional

import related
from config_builder.BaseConfigClass import BaseConfigClass

from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.configuration.mlfow_config import MLFlowConfig
from mlcvzoo_base.configuration.model_config import ModelConfig
from mlcvzoo_base.configuration.visualization_config import VisualizationConfig


@related.mutable(strict=True)
class ODEvaluationInputDataConfig(BaseConfigClass):
    # path to the csv file, where the annotation data should be parsed from
    csv_file_path: str = related.StringField()


@related.mutable(strict=True)
class TensorboardLoggingConfig(BaseConfigClass):

    tensorboard_dir: str = related.StringField()
    false_positive_image_size: int = related.IntegerField(default=650)


@related.mutable(strict=True)
class ODEvaluationConfig(BaseConfigClass):

    mutual_attribute_map: Dict[str, List[str]] = {}

    iou_thresholds: List[float] = related.SequenceField(float)

    mlflow_config: Optional[MLFlowConfig] = related.ChildField(
        cls=MLFlowConfig, required=False, default=None
    )

    mutual_attribute_map.update(MLFlowConfig.mutual_attribute_map)

    tensorboard_logging: Optional[TensorboardLoggingConfig] = related.ChildField(
        cls=TensorboardLoggingConfig, required=False, default=None
    )

    visualization: VisualizationConfig = related.ChildField(
        cls=VisualizationConfig, default=VisualizationConfig()
    )

    model_configs: Optional[List[ModelConfig]] = related.SequenceField(
        cls=ModelConfig, required=False, default=None
    )

    input_data: Optional[List[ODEvaluationInputDataConfig]] = related.SequenceField(
        cls=ODEvaluationInputDataConfig, required=False, default=None
    )

    annotation_handler_config: Optional[AnnotationHandlerConfig] = related.ChildField(
        cls=AnnotationHandlerConfig, required=False, default=None
    )
