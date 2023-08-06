# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for parsing information from yaml in python accessible attributes about the program
environment for different configuration classes.
"""
import related
from config_builder.BaseConfigClass import BaseConfigClass

STRING_REPLACEMENT_MAP_KEY = "string_replacement_map"


@related.mutable(strict=True)
class ReplacementConfig(BaseConfigClass):
    """
    Class for parsing general information about the environment placeholder mapping
    """

    CONFIG_ROOT_DIR_DIR_KEY = "CONFIG_ROOT_DIR"
    BASELINE_MODEL_DIR_KEY = "BASELINE_MODEL_DIR"
    INFERENCE_MODEL_DIR_KEY = "INFERENCE_MODEL_DIR"
    TRAINING_MODEL_DIR_KEY = "TRAINING_MODEL_DIR"
    MMDETECTION_DIR_KEY = "MMDETECTION_DIR"
    MMOCR_DIR_KEY = "MMOCR_DIR"
    MEDIA_DIR_KEY = "MEDIA_DIR"
    ANNOTATION_DIR_KEY = "ANNOTATION_DIR"
    PROJECT_ROOT_DIR_KEY = "PROJECT_ROOT_DIR"
    DARKNET_DIR_KEY = "DARKNET_DIR"
    YOLOX_DIR_KEY = "YOLOX_DIR"
    MLCVZOO_DIR_KEY = "MLCVZOO_DIR"

    DEFAULT_MAP = {
        CONFIG_ROOT_DIR_DIR_KEY: "",
        BASELINE_MODEL_DIR_KEY: "",
        INFERENCE_MODEL_DIR_KEY: "",
        TRAINING_MODEL_DIR_KEY: "",
        MMDETECTION_DIR_KEY: "",
        MMOCR_DIR_KEY: "",
        MEDIA_DIR_KEY: "",
        ANNOTATION_DIR_KEY: "",
        PROJECT_ROOT_DIR_KEY: "",
        DARKNET_DIR_KEY: "",
        YOLOX_DIR_KEY: "",
        MLCVZOO_DIR_KEY: "",
    }

    # Root Directory of the current repository
    PROJECT_ROOT_DIR: str = related.StringField(default=DEFAULT_MAP[PROJECT_ROOT_DIR_KEY])

    # Root directory of all configuration files
    CONFIG_ROOT_DIR: str = related.StringField(default=DEFAULT_MAP[CONFIG_ROOT_DIR_DIR_KEY])

    # Directory where the project mlcvzoo has be cloned to
    MLCVZOO_DIR: str = related.StringField(default=DEFAULT_MAP[MLCVZOO_DIR_KEY])

    # ==================================================
    # Placeholder for checkpoints directories

    # Main directory for all checkpoint files of original models
    # (e.g. models trained on the coco dataset)
    BASELINE_MODEL_DIR: str = related.StringField(default=DEFAULT_MAP[BASELINE_MODEL_DIR_KEY])

    # Main directory for storing inference model/checkpoint files only. When you just want to
    # use a certain device for inference, you don't want to synchronize all the training
    # checkpoints, but only the checkpoints that are relevant for the inference.
    INFERENCE_MODEL_DIR: str = related.StringField(default=DEFAULT_MAP[INFERENCE_MODEL_DIR_KEY])

    # Main directory for all shared training model/checkpoint files
    TRAINING_MODEL_DIR: str = related.StringField(default=DEFAULT_MAP[TRAINING_MODEL_DIR_KEY])

    # ==================================================
    # Placeholder for external repositories

    # Directory where the project mmdetection-fork has be cloned to
    MMDETECTION_DIR: str = related.StringField(default=DEFAULT_MAP[MMDETECTION_DIR_KEY])

    # Directory where the project mmdetection-fork has be cloned to
    MMOCR_DIR: str = related.StringField(default=DEFAULT_MAP[MMOCR_DIR_KEY])

    # Directory where the project AlexeyAB/darknet has be cloned and compiled to
    DARKNET_DIR: str = related.StringField(default=DEFAULT_MAP[DARKNET_DIR_KEY])

    # Directory where the project yolox has be cloned to
    YOLOX_DIR: str = related.StringField(default=DEFAULT_MAP[YOLOX_DIR_KEY])

    # ==================================================
    # Placeholder for data directories

    # Directory where the central media data is stored
    MEDIA_DIR: str = related.StringField(default=DEFAULT_MAP[MEDIA_DIR_KEY])

    # Directory where the central annotation data is stored
    ANNOTATION_DIR: str = related.StringField(default=DEFAULT_MAP[ANNOTATION_DIR_KEY])
