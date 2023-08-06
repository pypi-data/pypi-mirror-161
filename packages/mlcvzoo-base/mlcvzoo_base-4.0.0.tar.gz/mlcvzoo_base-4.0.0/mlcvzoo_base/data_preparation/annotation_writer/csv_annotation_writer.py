# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for writing CSV formatted annotations."""
import logging
import os
from typing import List, Optional, Tuple

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_writer import AnnotationWriter
from mlcvzoo_base.api.data.dataset_info import BaseDatasetInfo
from mlcvzoo_base.configuration.annotation_handler_config import (
    AnnotationHandlerWriteOutputConfig,
    AnnotationHandlerWriteOutputCSVAnnotationConfig,
)
from mlcvzoo_base.configuration.structs import (
    CSVFileNameIdentifier,
    FileNamePlaceholders,
)
from mlcvzoo_base.data_preparation.structs import CSVOutputStringFormats
from mlcvzoo_base.data_preparation.utils import replace_dir_by_index, save_bbox_snippets
from mlcvzoo_base.utils.annotation_utils import (
    create_annotation_file_from_list,
    create_cross_val_list_splits,
    create_list_split,
)
from mlcvzoo_base.utils.common_utils import get_current_timestamp

logger = logging.getLogger(__name__)


class CSVAnnotationWriter(AnnotationWriter):
    """
    Writer for generating a csv file based on a given
    list of annotations
    """

    def __init__(
        self,
        write_output_config: AnnotationHandlerWriteOutputConfig,
        output_string_format: str = CSVOutputStringFormats.BASE,
    ) -> None:
        self.csv_base_file_name: Optional[str] = None
        self.write_output_config = write_output_config
        self.output_string_format = output_string_format

        # define attribute types
        self.list_splits: List[Tuple[List[str], BaseDatasetInfo]]

    def write(self, annotations: List[BaseAnnotation]) -> Optional[str]:
        # TODO: Control the filename of the csv and avoid that it is different based on date and time
        output_file_path: Optional[str] = None

        assert self.write_output_config.csv_annotation is not None

        self.list_splits = self.__generate_csv_lists_from_annotations(
            annotations=annotations, output_string_format=self.output_string_format
        )

        timestamp_string = get_current_timestamp(
            self.write_output_config.csv_annotation.timestamp_format
        )

        file_extension = CSVAnnotationWriter.__get_file_extension(
            output_string_format=self.output_string_format
        )

        self.__replace_file_name_placeholders(timestamp_string=timestamp_string)

        csv_base_file_name = CSVAnnotationWriter.get_csv_base_file_name(
            timestamp_string=timestamp_string,
            csv_annotation=self.write_output_config.csv_annotation,
        )

        if csv_base_file_name is not None:
            self.csv_base_file_name = csv_base_file_name
        else:
            raise ValueError("Could find a correct setting for 'csv_base_file_name'")

        # TODO: Select between more than cross validation and just split?
        # CROSS VALIDATION
        if self.write_output_config.use_cross_val:
            for index, list_split in enumerate(self.list_splits):
                # TODO: make output_path configurable via the configuration class
                output_file_path = os.path.join(
                    self.write_output_config.csv_annotation.csv_dir,
                    f"{csv_base_file_name}_"
                    f"{CSVFileNameIdentifier.CROSS_VAL_SPLIT}_"
                    f"{index}{file_extension}",
                )

                create_annotation_file_from_list(
                    csv_entry_list=list_split[0],
                    dataset_info=list_split[1],
                    output_file_path=output_file_path,
                )

        # TRAIN / EVAL / VALIDATION Split
        else:
            # TRAIN
            if self.write_output_config.split_size > 0.0:
                output_file_path = CSVAnnotationWriter.generate_csv_path(
                    csv_base_file_name=csv_base_file_name,
                    file_extension=file_extension,
                    file_identifier=CSVFileNameIdentifier.TRAINING,
                    csv_annotation=self.write_output_config.csv_annotation,
                )
            # VALIDATION
            else:
                output_file_path = CSVAnnotationWriter.generate_csv_path(
                    csv_base_file_name=csv_base_file_name,
                    file_extension=file_extension,
                    file_identifier=CSVFileNameIdentifier.VALIDATION,
                    csv_annotation=self.write_output_config.csv_annotation,
                )

            create_annotation_file_from_list(
                csv_entry_list=self.list_splits[0][0],
                dataset_info=self.list_splits[0][1],
                output_file_path=output_file_path,
            )

        # EVALUATION
        if len(self.list_splits) == 2:
            output_file_path = CSVAnnotationWriter.generate_csv_path(
                csv_base_file_name=csv_base_file_name,
                file_extension=file_extension,
                file_identifier=CSVFileNameIdentifier.EVALUATION,
                csv_annotation=self.write_output_config.csv_annotation,
            )

            create_annotation_file_from_list(
                csv_entry_list=self.list_splits[1][0],
                dataset_info=self.list_splits[1][1],
                output_file_path=output_file_path,
            )

        return output_file_path

    def __annotation_to_csv_entry_list(
        self, annotations: List[BaseAnnotation], output_string_format: str
    ) -> Tuple[List[str], BaseDatasetInfo]:

        csv_entry_list: List[str] = list()

        # TODO: do we need this statistic?
        dataset_info = BaseDatasetInfo(
            classes_path="",
            image_count=0.0,
        )

        for annotation in annotations:

            annotation = replace_dir_by_index(annotation=annotation)

            # Write annotation data to csv
            if len(annotation.get_bounding_boxes(include_segmentations=True)) > 0:
                if self.write_output_config.csv_annotation is None:
                    raise ValueError(
                        "In order to write data to a csv the "
                        "write_output_config.csv_annotation configuration attribute"
                        "has to be provided!"
                    )

                csv_entry = annotation.to_csv_entry(
                    include_surrounding_bboxes=(
                        self.write_output_config.csv_annotation.include_surrounding_bboxes
                    ),
                    output_string_format=output_string_format,
                    use_difficult=self.write_output_config.use_difficult,
                    use_occluded=self.write_output_config.use_occluded,
                )

                if csv_entry is None or csv_entry == "":
                    logger.warning("csv_entry is empty, skip ....")
                    continue

                logger.debug("Add csv_entry: %s", csv_entry)

                csv_entry_list.append(csv_entry)

            # Update info-dict statistics with the data of this annotation
            dataset_info.update(annotation=annotation)

            # Cut out bounding-box snippets from original image.
            # This can be useful for classification of the bounding-boxes
            if self.write_output_config.bbox_snippets is not None:
                save_bbox_snippets(
                    annotation=annotation,
                    output_dir=self.write_output_config.bbox_snippets.output_dir,
                )

        return csv_entry_list, dataset_info

    def __generate_csv_lists_from_annotations(
        self, annotations: List[BaseAnnotation], output_string_format: str
    ) -> List[Tuple[List[str], BaseDatasetInfo]]:
        """
        Creates a list of data sets which are splits from the given annotations.

        Args:
            annotations: a list of BaseAnnotation objects
            output_string_format: string, one of CSVOutputStringFormats

        Returns: a list of data and respective dataset info

        """

        list_splits: List[Tuple[List[str], BaseDatasetInfo]] = list()

        # CROSS VALIDATION
        if self.write_output_config.use_cross_val:
            cross_val_list_splits = create_cross_val_list_splits(
                input_file_list=annotations,
                number_splits=self.write_output_config.number_splits,
            )

            for cross_val_list_split in cross_val_list_splits:
                csv_entry_list, dataset_info = self.__annotation_to_csv_entry_list(
                    annotations=cross_val_list_split,
                    output_string_format=output_string_format,
                )

                list_splits.append((csv_entry_list, dataset_info))

        # TRAIN / EVAL / VALIDATION Split
        else:
            # TRAIN / EVAL
            if self.write_output_config.split_size > 0.0:
                train_list, eval_list = create_list_split(
                    input_file_list=annotations,
                    split_size=self.write_output_config.split_size,
                    random_state=self.write_output_config.random_state,
                )

                (train_csv_entry_list, train_dataset_info,) = self.__annotation_to_csv_entry_list(
                    annotations=train_list, output_string_format=output_string_format
                )

                (eval_csv_entry_list, eval_dataset_info,) = self.__annotation_to_csv_entry_list(
                    annotations=eval_list, output_string_format=output_string_format
                )

                list_splits.append((train_csv_entry_list, train_dataset_info))
                list_splits.append((eval_csv_entry_list, eval_dataset_info))

            # VALIDATION
            else:
                (train_csv_entry_list, train_dataset_info,) = self.__annotation_to_csv_entry_list(
                    annotations=annotations, output_string_format=output_string_format
                )

                list_splits.append((train_csv_entry_list, train_dataset_info))

        return list_splits

    def __replace_file_name_placeholders(self, timestamp_string: str) -> None:

        assert self.write_output_config.csv_annotation is not None

        # TODO: add test
        if (
            FileNamePlaceholders.TIMESTAMP
            in self.write_output_config.csv_annotation.csv_split_0_file_name
        ):
            self.write_output_config.csv_annotation.csv_split_0_file_name = (
                self.write_output_config.csv_annotation.csv_split_0_file_name.replace(
                    FileNamePlaceholders.TIMESTAMP, timestamp_string
                )
            )

        # TODO: add test
        if (
            FileNamePlaceholders.TIMESTAMP
            in self.write_output_config.csv_annotation.csv_split_1_file_name
        ):
            self.write_output_config.csv_annotation.csv_split_1_file_name = (
                self.write_output_config.csv_annotation.csv_split_1_file_name.replace(
                    FileNamePlaceholders.TIMESTAMP, timestamp_string
                )
            )

    @staticmethod
    def get_csv_base_file_name(
        timestamp_string: str,
        csv_annotation: Optional[AnnotationHandlerWriteOutputCSVAnnotationConfig],
    ) -> Optional[str]:
        """
        Get a csv basis file name based on a timestamp and given configuration.

        Args:
            timestamp_string: timestamp as string to identify a training process
            csv_annotation: the csv-annotation config object

        Returns:
            Optional, base filename of csv files that hold information about
            training, validation and evaluation
        """

        csv_base_file_name: Optional[str] = None

        if csv_annotation is not None:
            if FileNamePlaceholders.TIMESTAMP in csv_annotation.csv_base_file_name:
                csv_base_file_name = csv_annotation.csv_base_file_name.replace(
                    FileNamePlaceholders.TIMESTAMP, timestamp_string
                )
            else:
                csv_base_file_name = csv_annotation.csv_base_file_name

        return csv_base_file_name

    @staticmethod
    def generate_csv_path(
        csv_base_file_name: Optional[str],
        file_extension: str,
        file_identifier: str,
        csv_annotation: Optional[AnnotationHandlerWriteOutputCSVAnnotationConfig] = None,
    ) -> str:
        """
        Generates a path to a csv file where annotation information is stored.

        Args:
            csv_base_file_name: Optional name of the csv file with training data
            file_extension: string, file extension (format)
            file_identifier: string, data set identifier (one of CSVFileNameIdentifier)
            csv_annotation: Optional configuration for output formatting

        Returns: string, the annotation output file path

        """

        if csv_annotation is not None:
            if csv_base_file_name is not None:
                train_file_name = f"{csv_base_file_name}_" f"{file_identifier}" f"{file_extension}"
            elif csv_annotation.csv_split_0_file_name != "":
                train_file_name = csv_annotation.csv_split_0_file_name
            else:
                train_file_name = f"{file_identifier}{file_extension}"

            output_file_path = os.path.join(
                csv_annotation.csv_dir,
                train_file_name,
            )

        else:
            if csv_base_file_name is not None:
                output_file_path = (
                    f"{csv_base_file_name}_" f"{file_identifier}" f"{file_extension}"
                )
            else:
                output_file_path = f"{file_identifier}" f"{file_extension}"

        return output_file_path

    @staticmethod
    def __get_file_extension(output_string_format: str) -> str:

        if output_string_format == CSVOutputStringFormats.BASE:
            file_extension = ".csv"
        elif output_string_format == CSVOutputStringFormats.YOLO:
            file_extension = ".txt"
        else:
            raise ValueError(
                f"file-format '{output_string_format}' is not valid to "
                f"be used for annotation file generation."
                f"Please use either of "
                f"{CSVOutputStringFormats.get_values_as_string(class_type=CSVOutputStringFormats)}"
            )

        return file_extension
