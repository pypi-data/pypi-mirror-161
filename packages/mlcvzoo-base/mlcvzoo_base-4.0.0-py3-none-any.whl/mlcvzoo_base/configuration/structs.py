# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for enumerating options of annotation and file formats, as well as data subsets and
respective phases. Furthermore mlflow configuration options can be found here.
"""
from enum import auto
from typing import Any, List

try:
    # python3.10
    from enum import StrEnum  # type: ignore
except ImportError:
    from backports.strenum import StrEnum


class BaseType:
    """Class for accessing internal attributes"""

    @staticmethod
    def get_values_as_list(class_type: Any) -> List[str]:
        list_types = []

        for attribute, value in class_type.__dict__.items():
            if (
                type(attribute) is str
                and not (attribute.startswith("__") and attribute.endswith("__"))
                and attribute != "get_values"
            ):
                list_types.append(value)
        return list_types

    @staticmethod
    def get_values_as_string(class_type: Any) -> str:
        types = ""

        for attribute, value in class_type.__dict__.items():
            if (
                type(attribute) is str
                and not (attribute.startswith("__") and attribute.endswith("__"))
                and attribute != "get_values"
            ):
                types += str(value) + ", "

        types = types[:-2]

        return types


class ObjectDetectionBBoxFormats(BaseType):
    """Class for enumerating accepted bounding box formats"""

    XYXY = "XYXY"  # => also known under xmin, ymin, xmax, ymax
    XYWH = "XYWH"


class AnnotationFormats(BaseType):
    """Class for enumerating accepted annotation formats"""

    BASE = "BASE"
    VOC_XML = "VOC_XML"
    CSV = "CSV"
    COCO = "COCO"
    CVAT_FOR_IMAGES = "CVAT_FOR_IMAGES"


class ImageFileFormats(BaseType):
    """Class for enumerating accepted image file formats"""

    JPEG = ".jpg"
    PNG = ".png"


class AnnotationFileFormats(BaseType):
    """Class for enumerating accepted annotation file formats"""

    XML = ".xml"


class ImageTypes(BaseType):
    """Class for enumerating accepted image object formats"""

    CV2 = "cv2"
    PIL = "pil"


class FileNamePlaceholders(BaseType):
    """Class for enumerating placeholders in filenames"""

    TIMESTAMP = "TIMESTAMP"
    IMAGE_NAME = "IMAGE_NAME"


class CSVFileNameIdentifier(BaseType):
    """Class for enumerating CSV annotation file identifiers regarding training phase"""

    TRAINING = "train"
    EVALUATION = "eval"
    VALIDATION = "validation"
    CROSS_VAL_SPLIT = "split"


class MMDetectionModelsTypes(BaseType):
    """Class for enumerating object detection model types used from mmdetection package"""

    HTC = "htc"


class MMOCRModelsTypes(BaseType):
    """Class for enumerating OCR model types used from mmocr package"""

    DBNET = "dbnet"


class PipelineStepTypes(BaseType):
    """Class for enumerating phases passed through a training process"""

    DATA_GENERATION = "DATA_GENERATION"
    TRAIN = "TRAIN"
    EVAL = "EVAL"
    CROSS_EVAL = "CROSS_EVAL"
    INFERENCE = "INFERENCE"


class MLFlowExperimentTypes(BaseType):
    """Class for enumerating types of mlflow experiments"""

    DATA_GENERATION = "DATA_GENERATION"
    TRAIN = "TRAIN"
    EVAL = "EVAL"
    TIMING = "TIMING"


class MLFlowExperimentConfig:
    """Class for configuring mlflow experiments"""

    EXPERIMENT_DICT = d = {
        index: i
        for index, i in enumerate(MLFlowExperimentTypes.get_values_as_list(MLFlowExperimentTypes))
    }


class MLFLowTrackingUriTypes(BaseType):
    """Class for enumerating supported mlflow tracking URI types"""

    FILE = "file"
    POSTGRES = "postgresql"


class OpenCVImageFormats(StrEnum):
    BMP = ".bmp"
    PBM = ".pbm"
    PGM = ".pgm"
    PPM = ".ppm"
    JPEG = ".jpeg"
    JPG = ".jpg"
    JPE = ".jpe"
    TIFF = ".tiff"
    TIF = ".tif"
    PNG = ".png"


class DeviceQueryTypes(StrEnum):
    NVIDIA_SMI = auto()
