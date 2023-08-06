# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for writing Darknet formatted annotations."""
import logging
import os
import random
from pathlib import Path
from shutil import copyfile, rmtree
from typing import List, Optional

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_writer import AnnotationWriter
from mlcvzoo_base.configuration.annotation_handler_config import (
    AnnotationHandlerWriteOutputDarknetAnnotationConfig,
)

logger = logging.getLogger(__name__)


class DarknetAnnotationWriter(AnnotationWriter):
    """
    Writer for generating annotation .txt files that can be used for a training
    of a darknet model, based a given list of annotations in BaseAnnotation format.
    """

    def __init__(
        self,
        darknet_train_set_config: AnnotationHandlerWriteOutputDarknetAnnotationConfig,
        split_size: float,
    ):

        self.darknet_train_set_config = darknet_train_set_config
        self.split_size = split_size

    def write(
        self,
        annotations: List[BaseAnnotation],
    ) -> Optional[str]:

        # Setup directories needed to generate a darknet training set
        output_dir = self.darknet_train_set_config.train_data_set_dir
        jpeg_dir = os.path.join(output_dir, "JPEGImages")
        label_dir = os.path.join(output_dir, "labels")

        if os.path.exists(jpeg_dir):
            rmtree(jpeg_dir)
        if os.path.exists(label_dir):
            rmtree(label_dir)

        os.makedirs(jpeg_dir)
        os.makedirs(label_dir)

        train_txt_path = self.darknet_train_set_config.get_train_file_path()
        test_txt_path = self.darknet_train_set_config.get_test_file_path()

        # open files to put annotation information for training and test data
        train_txt = open(train_txt_path, "w")
        test_txt = open(test_txt_path, "w")

        label_file_extension = ".txt"

        min_test = 1
        min_train = 1
        for annotation_id, annotation in enumerate(annotations):

            image_name, image_extension = os.path.splitext(os.path.basename(annotation.image_path))

            label_txt = open(
                os.path.join(label_dir, f"{image_name}{label_file_extension}"),
                "a",
            )
            for bounding_box in annotation.bounding_boxes:
                w = (bounding_box.box.xmax - bounding_box.box.xmin) / annotation.get_width()
                h = (bounding_box.box.ymax - bounding_box.box.ymin) / annotation.get_height()
                x = bounding_box.box.xmin / annotation.get_width() + w / 2
                y = bounding_box.box.ymin / annotation.get_height() + h / 2
                label_txt.write("{} {} {} {} {}\n".format(bounding_box.class_id, x, y, w, h))
            label_txt.close()

            img_target = os.path.join(jpeg_dir, f"{image_name}{image_extension}")
            if not os.path.exists(img_target):

                if self.darknet_train_set_config.write_as_symlink:

                    created_relpath = os.path.relpath(annotation.image_path, jpeg_dir)
                    logger.debug("Relative path is '%s'" % created_relpath)

                    symlink_path = Path(img_target)

                    symlink_path.unlink(missing_ok=True)
                    os.symlink(created_relpath, symlink_path)

                    logger.debug("Write image %s as symlink %s", created_relpath, symlink_path)
                else:
                    copyfile(annotation.image_path, img_target)

                    logger.debug("Copy image %s as symlink %s", annotation.image_path, img_target)
            if (random.random() > self.split_size or min_test > 0) and min_train == 0:
                test_txt.write(img_target + "\n")
                min_test -= 1
            else:
                train_txt.write(img_target + "\n")
                min_train -= 1

        train_txt.close()
        test_txt.close()

        return None
