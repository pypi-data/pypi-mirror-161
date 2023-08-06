# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

import copy
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
from tqdm import tqdm

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.evaluation.object_detection.data_classes import (
    CONFUSION_MATRIX_TYPE,
    DEFAULT_FLOAT_VALUE,
    DEFAULT_INT_VALUE,
    EVALUATION_LIST_TYPE,
    METRIC_DICT_TYPE,
    METRIC_IMAGE_INFO_TYPE,
    MetricImageInfo,
    ODEvaluationComputingData,
    ODMetrics,
    ODModelEvaluationMetrics,
)
from mlcvzoo_base.evaluation.object_detection.structs import BBoxSizeTypes
from mlcvzoo_base.evaluation.object_detection.utils import (
    compute_max_bounding_box,
    generate_metric_table,
    get_bbox_size_type,
    update_annotation_data,
)
from mlcvzoo_base.third_party.py_faster_rcnn.voc_ap import voc_ap

logger = logging.getLogger(__name__)


class MetricsComputation:
    """
    Main class for handling the evaluation of object detection models.
    """

    iou_thresholds_ap_50_95: List[float] = [
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
    ]

    def __init__(
        self,
        model_specifier: str,
        classes_id_dict: Dict[int, str],
        iou_thresholds: List[float],
        gt_annotations: List[BaseAnnotation],
        predicted_bounding_boxes_list: List[List[BoundingBox]],
    ):
        self.model_specifier = model_specifier
        self.classes_id_dict: Dict[int, str] = classes_id_dict
        self.iou_thresholds: List[float] = iou_thresholds
        self.dataset_length: int = len(gt_annotations)

        self.all_predicted_annotations: EVALUATION_LIST_TYPE = [
            [[] for _ in classes_id_dict.keys()] for _ in range(self.dataset_length)
        ]
        self.all_gt_annotations: EVALUATION_LIST_TYPE = [
            [[] for _ in classes_id_dict.keys()] for _ in range(self.dataset_length)
        ]

        # Dict[IOU_THRESHOLD][BBoxSizeTypes.BBOX_SIZE_TYPE][CLASS_NAME] = Object detection evaluation metrics
        self.model_metrics: ODModelEvaluationMetrics = ODModelEvaluationMetrics(
            model_specifier=self.model_specifier
        )
        self.computing_data: ODEvaluationComputingData = ODEvaluationComputingData()

        process_bar = tqdm(
            zip(gt_annotations, predicted_bounding_boxes_list),
            desc=f"Compute metrics",
        )

        # TODO: Convert to batch-processing
        for index, (gt_annotation, predicted_bounding_boxes) in enumerate(process_bar):

            _ = self.__update_from_prediction(
                index=index,
                gt_annotation=gt_annotation,
                predicted_bounding_boxes=predicted_bounding_boxes,
            )

    def get_metrics_dict(self) -> METRIC_DICT_TYPE:
        return self.model_metrics.metrics_dict

    def get_metrics_image_info_dict(
        self,
    ) -> METRIC_IMAGE_INFO_TYPE:
        return self.model_metrics.metrics_image_info_dict

    @staticmethod
    def get_overall_ap(metrics_dict: METRIC_DICT_TYPE, iou_threshold: float) -> float:
        """
        Calculate AP metric over every class specific AP metric for bounding boxes of all sizes.

        Args:
            metrics_dict: The dictionary that stores the relevant metric data, which is the
                          basis for the calculation
            iou_threshold: The iou threshold for which the AP metric should be computed

        Returns:
            The computed overall AP metric
        """

        class_metrics = metrics_dict[iou_threshold][BBoxSizeTypes.BBOX_ALL]

        ap_list: List[float] = list()
        for class_metric in class_metrics.values():
            ap_list.append(class_metric.AP)

        return sum(ap_list) / len(ap_list)

    @staticmethod
    def get_ap_50_95(model_metrics: ODModelEvaluationMetrics) -> float:
        return sum(
            [
                MetricsComputation.get_overall_ap(
                    metrics_dict=model_metrics.metrics_dict, iou_threshold=iou
                )
                for iou in MetricsComputation.iou_thresholds_ap_50_95
            ]
        ) / len(MetricsComputation.iou_thresholds_ap_50_95)

    @staticmethod
    def get_ap_50(model_metrics: ODModelEvaluationMetrics) -> float:
        return MetricsComputation.get_overall_ap(
            metrics_dict=model_metrics.metrics_dict, iou_threshold=0.5
        )

    def __reset_main_dictionaries(
        self,
    ) -> None:

        for class_name in self.classes_id_dict.values():
            self.model_metrics.metrics_image_info_dict[class_name] = dict()

        for bbox_size_type in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):
            self.computing_data.gt_counter_dict[bbox_size_type] = dict()

            for class_name in self.classes_id_dict.values():
                self.computing_data.gt_counter_dict[bbox_size_type][class_name] = 0

        for iou_thresh in self.iou_thresholds:
            self.model_metrics.metrics_dict[iou_thresh] = dict()
            self.computing_data.valid_precisions[iou_thresh] = dict()

            for bbox_size_type in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):
                self.model_metrics.metrics_dict[iou_thresh][bbox_size_type] = dict()
                self.computing_data.valid_precisions[iou_thresh][bbox_size_type] = list()

                for class_name in self.classes_id_dict.values():
                    self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
                        class_name
                    ] = ODMetrics()

    def __reset_computing_dictionaries(self) -> None:

        for iou_thresh in self.iou_thresholds:
            self.computing_data.false_positives_dict[iou_thresh] = dict()
            self.computing_data.true_positives_dict[iou_thresh] = dict()
            self.computing_data.detected_annotations[iou_thresh] = list()
            self.computing_data.scores[iou_thresh] = dict()

            for bbox_size in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):
                self.computing_data.false_positives_dict[iou_thresh][bbox_size] = np.zeros((0,))
                self.computing_data.true_positives_dict[iou_thresh][bbox_size] = np.zeros((0,))

                self.computing_data.scores[iou_thresh][bbox_size] = np.zeros((0,))

    def compute_metrics(
        self,
    ) -> ODModelEvaluationMetrics:
        """
        Compute MAP Metrics

        return: the metrics dictionary in the form of:
                1st key: iou-threshold
                2nd key: type of the size of the bounding-box
                3rd key: class-name
                Value: The computed metrics

                Dict[IOU_THRESHOLD][BBoxSizeTypes.BBOX_SIZE_TYPE][CLASS_NAME] = ODMetrics
        """

        self.__reset_main_dictionaries()

        # process get_bounding_boxes and annotations
        for class_id, class_name in self.classes_id_dict.items():
            self.__reset_computing_dictionaries()

            self.__fill_computing_data(
                class_id=class_id,
                class_name=class_name,
            )

            self.__compute_metrics(
                class_name=class_name,
            )

        for iou_threshold in self.iou_thresholds:
            metric_table = generate_metric_table(
                metrics_dict=self.model_metrics.metrics_dict,
                iou_threshold=iou_threshold,
            )
            logger.debug(
                "Metrics for IOU-Threshold '%s': \n%s" % (iou_threshold, metric_table.table)
            )

        return ODModelEvaluationMetrics(
            model_specifier=self.model_specifier,
            metrics_dict=self.get_metrics_dict(),
            metrics_image_info_dict=self.get_metrics_image_info_dict(),
        )

    def __update_from_prediction(
        self,
        index: int,
        gt_annotation: BaseAnnotation,
        predicted_bounding_boxes: List[BoundingBox],
    ) -> BaseAnnotation:
        """
        Update the main computing attributes given the information from the ground truth
        annotation and predicted bounding boxes at the dataset index.

        Args:
            index: The index of the dataset where to update the data
            gt_annotation: The ground truth information for the given index (data item)
            predicted_bounding_boxes: The predicted bounding boxes for this index (data item)

        Returns:
            The annotation object created on the basis of the ground truth data and the predicted
            bounding boxes
        """

        logger.debug(
            "Get metrics for annotation: \n"
            "  - image-path:       %s\n"
            "  - image-annotation: %s",
            gt_annotation.image_path,
            gt_annotation.annotation_path,
        )

        self.all_gt_annotations = update_annotation_data(
            classes_id_dict=self.classes_id_dict,
            all_annotations=self.all_gt_annotations,
            index=index,
            new_annotation=gt_annotation,
        )

        predicted_annotation = BaseAnnotation(
            image_path=gt_annotation.image_path,
            annotation_path=gt_annotation.annotation_path,
            image_shape=gt_annotation.image_shape,
            classifications=[],
            bounding_boxes=predicted_bounding_boxes,
            segmentations=[],
            image_dir=gt_annotation.image_dir,
            annotation_dir=gt_annotation.annotation_dir,
            replacement_string=gt_annotation.replacement_string,
        )

        self.all_predicted_annotations = update_annotation_data(
            classes_id_dict=self.classes_id_dict,
            all_annotations=self.all_predicted_annotations,
            index=index,
            new_annotation=predicted_annotation,
        )

        return predicted_annotation

    def __update_tp_fp_data(
        self,
        is_true_positive: bool,
        iou_thresh: float,
        bbox_size_type: str,
    ) -> None:

        if is_true_positive:
            tp_value = 1
            fp_value = 0
        else:
            tp_value = 0
            fp_value = 1

        # Update dictionary for overall mAP computation
        self.computing_data.true_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.true_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL],
            tp_value,
        )
        self.computing_data.false_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.false_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL],
            fp_value,
        )

        # Update dictionary for size specific mAP computation
        self.computing_data.true_positives_dict[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.true_positives_dict[iou_thresh][bbox_size_type],
            tp_value,
        )
        self.computing_data.false_positives_dict[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.false_positives_dict[iou_thresh][bbox_size_type],
            fp_value,
        )

    def __update_computation_dictionaries(
        self,
        bounding_box: BoundingBox,
        iou_thresh: float,
        unmatched_gt_bounding_boxes: List[BoundingBox],
    ) -> List[BoundingBox]:

        bbox_size_type: str = get_bbox_size_type(bounding_box.box)

        # if the ground truth data for this image indicates that nothing has to be detected,
        # indicate this box as False-Positive right away!
        if len(unmatched_gt_bounding_boxes) == 0:

            self.__update_tp_fp_data(
                is_true_positive=False,
                iou_thresh=iou_thresh,
                bbox_size_type=bbox_size_type,
            )
        else:
            max_overlap, assigned_gt_bounding_box = compute_max_bounding_box(
                bounding_box=bounding_box, gt_bounding_boxes=unmatched_gt_bounding_boxes
            )

            # If max-overlap fulfills given threshold
            # the detected box is treated as TP, otherwise as FP
            if (
                max_overlap
                >= iou_thresh
                # and
                # if this bounding_box has not already been assigned as valid,
                # treat it as true positive, otherwise as false positive
                # assigned_bounding_box not in self.detected_annotations[iou_thresh]
            ):
                unmatched_gt_bounding_boxes.remove(assigned_gt_bounding_box)

                # NOTE: In order to have correct metrics, the size of a true positive
                #       bounding box is the same as for the matching ground truth bounding box
                bbox_size_type = get_bbox_size_type(assigned_gt_bounding_box.box)

                # Update as True-Positive
                self.__update_tp_fp_data(
                    is_true_positive=True,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                )
            else:
                # Update as False-Positive
                self.__update_tp_fp_data(
                    is_true_positive=False,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                )

        # append the score of the current bounding-box to the overall  scores list
        self.computing_data.scores[iou_thresh][BBoxSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.scores[iou_thresh][BBoxSizeTypes.BBOX_ALL],
            bounding_box.score,
        )

        # append the score of the current bounding-box to the size specific scores list
        self.computing_data.scores[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.scores[iou_thresh][bbox_size_type], bounding_box.score
        )

        return unmatched_gt_bounding_boxes

    def __update_false_positive_metric_info(
        self,
        ground_truth_annotation: Optional[BaseAnnotation],
        predicted_annotation: BaseAnnotation,
        bounding_box: BoundingBox,
        class_name: str,
    ) -> None:
        # Build an annotation based on the ground truth data and the given
        # bounding boxes
        false_positive_annotation = BaseAnnotation(
            image_path=predicted_annotation.image_path,
            annotation_path=predicted_annotation.annotation_path,
            image_shape=predicted_annotation.image_shape,
            classifications=[],
            bounding_boxes=[bounding_box],
            segmentations=[],
            image_dir=predicted_annotation.image_dir,
            annotation_dir=predicted_annotation.annotation_dir,
            replacement_string=predicted_annotation.replacement_string,
        )

        # save FP annotation to metric_image_info_dict
        if (
            predicted_annotation.image_path
            not in self.model_metrics.metrics_image_info_dict[class_name]
        ):
            # The predicted annotation is a FP, therefore store it in a dict so that
            # it can be logged to tensorboard after the evaluation has finished
            self.model_metrics.metrics_image_info_dict[class_name][
                predicted_annotation.image_path
            ] = MetricImageInfo(
                ground_truth_annotation=ground_truth_annotation,
                false_positive_annotation=false_positive_annotation,
                false_negative_annotation=None,
            )
        else:
            # Update FP annotation object that belongs to the given image-path
            if (
                self.model_metrics.metrics_image_info_dict[class_name][
                    predicted_annotation.image_path
                ].false_positive_annotation
                is not None
            ):
                # If their already is an annotation object present, append this bounding box
                # NOTE: the mypy error 'Item "None" of "Optional[BaseAnnotation]" has no
                #       attribute "bounding_boxes' can be ignored. It is checked by the
                #       above query operation. Somehow mypy does not gets that
                self.model_metrics.metrics_image_info_dict[class_name][
                    predicted_annotation.image_path
                ].false_positive_annotation.bounding_boxes.append(  # type: ignore
                    bounding_box
                )

            # NOTE: false_positive_annotation of
            #       self.model_metrics.metrics_image_info_dict[class_name]
            #       [predicted_annotation.image_path]
            #       can't be None here. This would only be the case if a MetricImageInfo
            #       object would be inserted with
            #         MetricImageInfo(
            #           ground_truth_annotation=ground_truth_annotation,
            #           false_positive_annotation=None,
            #           false_negative_annotation=false_negative_annotation,
            #         )
            #       Since the false negative annotations will be updated after the false
            #       positive annotations are already set, we always have an
            #       false_positive_annotation present here.

    def __update_false_negative_metric_info(
        self,
        ground_truth_annotation: BaseAnnotation,
        iou_unmatched_gt_bounding_boxes: List[BoundingBox],
        class_name: str,
    ) -> None:
        """
        Update the false_negative_annotation entry of model_metrics.metrics_image_info_dict
        for the given class_name and the image path of the given ground truth annotation.

        Args:
            ground_truth_annotation:
            iou_unmatched_gt_bounding_boxes:
            class_name:

        Returns:

        """

        false_negative_annotation = BaseAnnotation(
            image_path=ground_truth_annotation.image_path,
            annotation_path=ground_truth_annotation.annotation_path,
            image_shape=ground_truth_annotation.image_shape,
            classifications=[],
            bounding_boxes=iou_unmatched_gt_bounding_boxes,
            segmentations=[],
            image_dir=ground_truth_annotation.image_dir,
            annotation_dir=ground_truth_annotation.annotation_dir,
            replacement_string=ground_truth_annotation.replacement_string,
        )

        if (
            ground_truth_annotation.image_path
            not in self.model_metrics.metrics_image_info_dict[class_name]
        ):
            self.model_metrics.metrics_image_info_dict[class_name][
                ground_truth_annotation.image_path
            ] = MetricImageInfo(
                ground_truth_annotation=ground_truth_annotation,
                false_positive_annotation=None,
                false_negative_annotation=false_negative_annotation,
            )
        else:
            self.model_metrics.metrics_image_info_dict[class_name][
                ground_truth_annotation.image_path
            ].false_negative_annotation = false_negative_annotation

    def __get_gt_annotation(
        self, dataset_index: int, class_id: int, class_name: str
    ) -> Tuple[Optional[BaseAnnotation], List[BoundingBox]]:

        # annotation object for gathering all ground truth bounding boxes for this image
        ground_truth_annotation: Optional[BaseAnnotation] = None

        unmatched_gt_bounding_boxes: List[BoundingBox] = []

        # Iterate over all ground-truth annotations that containing bounding-box
        # information for this image (dataset_index) and the given class-id
        for gt_annotation in self.all_gt_annotations[dataset_index][class_id]:

            unmatched_gt_bounding_boxes.extend(
                gt_annotation.get_bounding_boxes(include_segmentations=True)
            )

            for bounding_box in gt_annotation.get_bounding_boxes(include_segmentations=True):
                # increase bounding-box ground-truth counter for overall count
                # and the specific bounding-box size count

                self.computing_data.gt_counter_dict[BBoxSizeTypes.BBOX_ALL][class_name] += 1

                self.computing_data.gt_counter_dict[get_bbox_size_type(bounding_box.box)][
                    class_name
                ] += 1

            # Initialize/update an overall ground_truth annotation that contains all
            # data for this image and class-id
            if ground_truth_annotation is None:
                ground_truth_annotation = copy.deepcopy(gt_annotation)
            else:
                ground_truth_annotation.bounding_boxes.extend(
                    gt_annotation.get_bounding_boxes(include_segmentations=True)
                )

        return ground_truth_annotation, unmatched_gt_bounding_boxes

    def __fill_computing_data(
        self,
        class_id: int,
        class_name: str,
    ) -> None:

        process_bar = tqdm(
            range(self.dataset_length),
            desc=f"Compute metrics for class-name: {class_name}",
        )

        # Iterate over all image indices
        for dataset_index in process_bar:

            (ground_truth_annotation, unmatched_gt_bounding_boxes,) = self.__get_gt_annotation(
                dataset_index=dataset_index, class_id=class_id, class_name=class_name
            )

            # Iterate over all predicted annotations for this image and class-id
            for iou_thresh in self.iou_thresholds:

                iou_unmatched_gt_bounding_boxes = copy.deepcopy(unmatched_gt_bounding_boxes)

                for predicted_annotation in self.all_predicted_annotations[dataset_index][
                    class_id
                ]:

                    for bounding_box in predicted_annotation.get_bounding_boxes(
                        include_segmentations=True
                    ):
                        iou_unmatched_gt_bounding_boxes = self.__update_computation_dictionaries(
                            bounding_box=bounding_box,
                            iou_thresh=iou_thresh,
                            unmatched_gt_bounding_boxes=iou_unmatched_gt_bounding_boxes,
                        )

                        # The bounding_box is a FP
                        if self.computing_data.false_positives_dict[iou_thresh][
                            BBoxSizeTypes.BBOX_ALL
                        ][-1]:
                            self.__update_false_positive_metric_info(
                                ground_truth_annotation=ground_truth_annotation,
                                predicted_annotation=predicted_annotation,
                                bounding_box=bounding_box,
                                class_name=class_name,
                            )

                # There are ground truth annotations which haven't been matched,
                # this states that the box is a false negative
                if (
                    len(self.all_gt_annotations[dataset_index][class_id]) > 0
                    and len(iou_unmatched_gt_bounding_boxes) > 0
                    and ground_truth_annotation is not None
                ):
                    self.__update_false_negative_metric_info(
                        ground_truth_annotation=ground_truth_annotation,
                        iou_unmatched_gt_bounding_boxes=iou_unmatched_gt_bounding_boxes,
                        class_name=class_name,
                    )

    def __compute_and_update_metrics_step(
        self,
        class_name: str,
        iou_thresh: float,
        bbox_size_type: str,
        num_annotations: int,
        true_positives: np.ndarray,  # type: ignore[type-arg]
        false_positives: np.ndarray,  # type: ignore[type-arg]
    ) -> None:

        # compute recall and precision
        recall_values = true_positives / num_annotations
        precision_values = true_positives / np.maximum(
            true_positives + false_positives, np.finfo(np.float64).eps
        )

        # compute average precision
        # NOTE: mypy error 'Call to untyped function "close" in typed context' can be ignored
        ap = voc_ap(rec=recall_values, prec=precision_values, use_07_metric=False)  # type: ignore

        if len(true_positives) > 0:
            tp = int(true_positives[-1])

            if tp > num_annotations:
                print("TP not valid")

            rc = tp / num_annotations
        else:
            tp = DEFAULT_INT_VALUE
            rc = DEFAULT_FLOAT_VALUE

        if len(false_positives) > 0:
            fp = int(false_positives[-1])
        else:
            fp = DEFAULT_INT_VALUE

        try:
            pr = tp / (fp + tp)
        except ZeroDivisionError:
            pr = DEFAULT_FLOAT_VALUE

        try:
            p1 = 2 * (pr * rc) / (pr + rc)
        except ZeroDivisionError:
            p1 = DEFAULT_FLOAT_VALUE

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
            class_name
        ].COUNT = num_annotations

        fn = num_annotations - tp

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].TP = tp
        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].FP = fp

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].FN = fn

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].PR = pr
        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].RC = rc

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].F1 = p1

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].AP = ap

    def __compute_metrics(
        self,
        class_name: str,
    ) -> None:

        # TODO: Is this mAP computation? - separate from rest !
        for iou_thresh in self.iou_thresholds:

            for bbox_size_type in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):

                num_annotations = self.computing_data.gt_counter_dict[bbox_size_type][class_name]

                if num_annotations == 0.0:
                    continue

                # sort by score
                # TODO: CHECK NEGATIVE SIGN!!!
                indices = np.argsort(-self.computing_data.scores[iou_thresh][bbox_size_type])

                false_positives = self.computing_data.false_positives_dict[iou_thresh][
                    bbox_size_type
                ][indices]

                true_positives = self.computing_data.true_positives_dict[iou_thresh][
                    bbox_size_type
                ][indices]

                # compute false positives and true positives
                false_positives = np.cumsum(false_positives)
                true_positives = np.cumsum(true_positives)

                self.__compute_and_update_metrics_step(
                    class_name=class_name,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                    num_annotations=num_annotations,
                    true_positives=true_positives,
                    false_positives=false_positives,
                )

                if (
                    self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].FP
                    != -1
                    and self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].TP
                    != -1
                ):
                    self.computing_data.valid_precisions[iou_thresh][bbox_size_type].append(
                        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][class_name].AP
                    )

    @staticmethod
    def match_false_negatives_and_false_positives(
        metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
        iou_threshold: float,
    ) -> Tuple[METRIC_IMAGE_INFO_TYPE, CONFUSION_MATRIX_TYPE]:
        """


        Args:
            metrics_image_info_dict:
            iou_threshold:

        Returns:

        """

        confusion_matrix: CONFUSION_MATRIX_TYPE = [
            [0 for _ in metrics_image_info_dict.keys()] for _ in metrics_image_info_dict.keys()
        ]
        classes_name_dict: Dict[str, int] = {}
        for class_id, class_name in enumerate(metrics_image_info_dict.keys()):
            classes_name_dict[class_name] = class_id

        # Build a dict for reverse look up, where the keys are image paths.
        # This is needed to fill the confusion matrix per image.
        image_metrics_info_dict: Dict[str, Dict[str, MetricImageInfo]] = {}
        for class_name in metrics_image_info_dict.keys():
            for image_path, metric_image_info in metrics_image_info_dict[class_name].items():
                if image_path not in image_metrics_info_dict:
                    image_metrics_info_dict[image_path] = {}

                if class_name not in image_metrics_info_dict[image_path]:
                    image_metrics_info_dict[image_path][class_name] = metric_image_info

        result_metrics_image_info_dict = copy.deepcopy(metrics_image_info_dict)

        for image_path in image_metrics_info_dict.keys():
            class_names = list(image_metrics_info_dict[image_path].keys())

            for class_name in class_names:

                other_classes = copy.deepcopy(class_names)
                other_classes.remove(class_name)

                class_img_metrics_info = image_metrics_info_dict[image_path][class_name]
                if class_img_metrics_info.false_negative_annotation:
                    class_fn_bounding_boxes = (
                        class_img_metrics_info.false_negative_annotation.bounding_boxes
                    )

                    for fn_bounding_box in class_fn_bounding_boxes:
                        for other_class in other_classes:
                            other_class_img_metrics_info = image_metrics_info_dict[image_path][
                                other_class
                            ]

                            if other_class_img_metrics_info.false_positive_annotation:
                                other_class_fp_bounding_boxes = (
                                    other_class_img_metrics_info.false_positive_annotation.bounding_boxes
                                )

                                (
                                    max_overlap,
                                    assigned_fp_bounding_box,
                                ) = compute_max_bounding_box(
                                    bounding_box=fn_bounding_box,
                                    gt_bounding_boxes=other_class_fp_bounding_boxes,
                                )

                                if max_overlap > iou_threshold:
                                    confusion_matrix[classes_name_dict[class_name]][
                                        classes_name_dict[other_class]
                                    ] += 1
                                    annotation_path = (
                                        class_img_metrics_info.false_negative_annotation.annotation_path
                                    )
                                    image_shape = (
                                        class_img_metrics_info.false_negative_annotation.image_shape
                                    )
                                    image_dir = (
                                        class_img_metrics_info.false_negative_annotation.image_dir
                                    )
                                    annotation_dir = (
                                        class_img_metrics_info.false_negative_annotation.annotation_dir
                                    )
                                    replacement_string = (
                                        class_img_metrics_info.false_negative_annotation.replacement_string
                                    )

                                    class_img_metrics_info.false_negative_annotation.bounding_boxes.remove(
                                        fn_bounding_box
                                    )
                                    other_class_img_metrics_info.false_positive_annotation.bounding_boxes.remove(
                                        assigned_fp_bounding_box
                                    )

                                    result_metrics_image_info_dict = MetricsComputation.__change_matched_bbox_attribute(
                                        metrics_image_info_dict=result_metrics_image_info_dict,
                                        image_path=image_path,
                                        annotation_path=annotation_path,
                                        class_name=class_name,
                                        other_class=other_class,
                                        image_shape=image_shape,
                                        image_dir=image_dir,
                                        annotation_dir=annotation_dir,
                                        replacement_string=replacement_string,
                                        fn_bounding_box=fn_bounding_box,
                                        assigned_fp_bounding_box=assigned_fp_bounding_box,
                                        class_img_metrics_info=class_img_metrics_info,
                                        other_class_img_metrics_info=other_class_img_metrics_info,
                                    )

                            if other_class_img_metrics_info.false_positive_annotation:
                                if (
                                    len(
                                        other_class_img_metrics_info.false_positive_annotation.bounding_boxes
                                    )
                                    == 0
                                ):
                                    other_class_img_metrics_info.false_positive_annotation = None

                if class_img_metrics_info.false_negative_annotation:
                    if len(class_img_metrics_info.false_negative_annotation.bounding_boxes) == 0:
                        class_img_metrics_info.false_negative_annotation = None

        return result_metrics_image_info_dict, confusion_matrix

    @staticmethod
    def __change_matched_bbox_attribute(
        metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
        image_path: str,
        annotation_path: str,
        class_name: str,
        other_class: str,
        image_shape: Tuple[int, int],
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
        fn_bounding_box: BoundingBox,
        assigned_fp_bounding_box: BoundingBox,
        class_img_metrics_info: MetricImageInfo,
        other_class_img_metrics_info: MetricImageInfo,
    ) -> METRIC_IMAGE_INFO_TYPE:

        if class_img_metrics_info.false_negative_matched_false_positive_annotation is not None:
            class_img_metrics_info.false_negative_matched_false_positive_annotation.bounding_boxes.append(
                fn_bounding_box
            )
        else:
            class_img_metrics_info.false_negative_matched_false_positive_annotation = (
                BaseAnnotation(
                    image_path=image_path,
                    annotation_path=annotation_path,
                    image_shape=image_shape,
                    classifications=[],
                    bounding_boxes=[fn_bounding_box],
                    segmentations=[],
                    image_dir=image_dir,
                    annotation_dir=annotation_dir,
                    replacement_string=replacement_string,
                )
            )

        if (
            other_class_img_metrics_info.false_negative_matched_false_positive_annotation
            is not None
        ):
            other_class_img_metrics_info.false_negative_matched_false_positive_annotation.bounding_boxes.append(
                assigned_fp_bounding_box
            )

        else:
            other_class_img_metrics_info.false_negative_matched_false_positive_annotation = (
                BaseAnnotation(
                    image_path=image_path,
                    annotation_path=annotation_path,
                    image_shape=image_shape,
                    classifications=[],
                    bounding_boxes=[assigned_fp_bounding_box],
                    segmentations=[],
                    image_dir=image_dir,
                    annotation_dir=annotation_dir,
                    replacement_string=replacement_string,
                )
            )

        metrics_image_info_dict[class_name][image_path] = class_img_metrics_info
        metrics_image_info_dict[other_class][image_path] = other_class_img_metrics_info

        return metrics_image_info_dict
