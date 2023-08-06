# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for writing CVAT formatted annotations."""
import logging
import xml.etree.ElementTree as ET_xml
from typing import List, Optional

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_writer import AnnotationWriter
from mlcvzoo_base.utils.xml_utils import xml_tree_to_file

logger = logging.getLogger(__name__)


class CVATAnnotationWriter(AnnotationWriter):
    """
    Writer for generating a CVAT 1.1 conform xml file
    out of a list of annotations.
    """

    def __init__(
        self,
        cvat_xml_input_path: str,
        output_file_path: str,
        clean_boxes: bool = False,
        clean_segmentations: bool = False,
        clean_tags: bool = False,
    ):

        self.cvat_xml_input_path = cvat_xml_input_path
        self.output_file_path = output_file_path
        self.clean_boxes = clean_boxes
        self.clean_segmentations = clean_segmentations
        self.clean_tags = clean_tags

    def write(
        self,
        annotations: List[BaseAnnotation],
    ) -> Optional[str]:

        xml_tree = CVATAnnotationWriter.annotations_to_xml_tree(
            annotations=annotations,
            cvat_xml_input_path=self.cvat_xml_input_path,
            clean_boxes=self.clean_boxes,
            clean_segmentations=self.clean_segmentations,
            clean_tags=self.clean_tags,
        )

        # NOTE: generated file will overwrite existing file
        xml_tree_to_file(xml_file_path=self.output_file_path, xml_tree=xml_tree)

        return None

    @staticmethod
    def annotations_to_xml_tree(
        annotations: List[BaseAnnotation],
        cvat_xml_input_path: str,
        clean_boxes: bool = False,
        clean_segmentations: bool = False,
        clean_tags: bool = False,
    ) -> ET_xml.ElementTree:
        """
        Parses given annotations to an XML ElementTree.

        Args:
            annotations: a list of BaseAnnotation objects
            cvat_xml_input_path: string, the path to CVAT annotations in XML format
            clean_boxes: bool, whether to overwrite or add box annotations
            clean_segmentations: bool, whether to overwrite or add segmentation annotations
            clean_tags: bool, whether to overwrite or add tag annotations

        Returns: an XML ElementTree

        """
        tree = ET_xml.parse(source=cvat_xml_input_path)
        root = tree.getroot()

        annotation_dict = {}
        for annotation in annotations:
            annotation_dict[annotation.image_path] = annotation

        images = root.findall("image")
        for image in images:
            image_relative_path = image.attrib["name"]

            # create dictionary of image_path -> annotation,
            #  where the image_path ends with the relative path listed in "name" attribute
            corresponding_annotation_dict = {
                key: val
                for key, val in annotation_dict.items()
                if key.endswith(image_relative_path)
            }

            if len(list(corresponding_annotation_dict.keys())) != 1:
                logger.warning(
                    "No precise entry for image with "
                    "relative path {image_relative_path} in annotations. "
                    "Found %s entries. "
                    "Skipping that image tag in XML.",
                    len(list(corresponding_annotation_dict.keys())),
                )
                continue

            # use corresponding annotation
            image_path = list(corresponding_annotation_dict.keys())[0]
            current_annotation = annotation_dict[image_path]

            # add bbox info
            CVATAnnotationWriter._add_box_subtree(image, current_annotation, clean_boxes)

            # add seg info
            CVATAnnotationWriter._add_segmentation_subtree(
                image, current_annotation, clean_segmentations
            )

            # add tag info
            CVATAnnotationWriter._add_classification_subtree(image, current_annotation, clean_tags)

        return tree

    @staticmethod
    def _add_box_subtree(
        sub_tree: ET_xml.Element, annotation: BaseAnnotation, clean_boxes: bool = False
    ) -> None:
        if clean_boxes:
            # remove existing bounding boxes
            for elem in list(sub_tree):
                if elem.tag == "box":
                    map(elem.remove, list(elem))
                    sub_tree.remove(elem)

        for bbox in annotation.bounding_boxes:
            bbox_dict = dict()

            bbox_dict["xtl"] = str(bbox.box.xmin)
            bbox_dict["ytl"] = str(bbox.box.ymin)
            bbox_dict["xbr"] = str(bbox.box.xmax)
            bbox_dict["ybr"] = str(bbox.box.ymax)

            bbox_dict["label"] = bbox.class_name
            bbox_dict["source"] = "generated"
            bbox_dict["z_order"] = str(0)

            occluded = bbox.occluded
            occluded_value = 0
            if occluded:
                occluded_value = 1
            bbox_dict["occluded"] = str(occluded_value)

            box_tag = ET_xml.SubElement(sub_tree, "box", attrib=bbox_dict)

            difficult = bbox.difficult
            content = bbox.content

            difficult_tag = ET_xml.SubElement(box_tag, "attribute", attrib={"name": "difficult"})
            if difficult:
                difficult_tag.text = "true"
            else:
                difficult_tag.text = "false"

            occluded_tag = ET_xml.SubElement(box_tag, "attribute", attrib={"name": "occluded"})
            if occluded:
                occluded_tag.text = "true"
            else:
                occluded_tag.text = "false"

            content_tag = ET_xml.SubElement(box_tag, "attribute", attrib={"name": "content"})
            content_tag.text = content

    @staticmethod
    def _add_segmentation_subtree(
        sub_tree: ET_xml.Element,
        annotation: BaseAnnotation,
        clean_segmentations: bool = False,
    ) -> None:
        if clean_segmentations:
            # remove existing polygons
            for elem in list(sub_tree):
                if elem.tag == "polygon":
                    map(elem.remove, list(elem))
                    sub_tree.remove(elem)

        for segmentation in annotation.segmentations:
            segmentation_dict = dict()

            segmentation_dict["points"] = segmentation.to_points_string()

            segmentation_dict["label"] = segmentation.class_name
            segmentation_dict["source"] = "generated"
            segmentation_dict["z_order"] = str(0)

            occluded = segmentation.occluded
            occluded_value = 0
            if occluded:
                occluded_value = 1
            segmentation_dict["occluded"] = str(occluded_value)

            polygon_tag = ET_xml.SubElement(sub_tree, "polygon", attrib=segmentation_dict)

            difficult = segmentation.difficult
            content = segmentation.content

            difficult_tag = ET_xml.SubElement(
                polygon_tag, "attribute", attrib={"name": "difficult"}
            )
            if difficult:
                difficult_tag.text = "true"
            else:
                difficult_tag.text = "false"

            occluded_tag = ET_xml.SubElement(polygon_tag, "attribute", attrib={"name": "occluded"})
            if occluded:
                occluded_tag.text = "true"
            else:
                occluded_tag.text = "false"

            content_tag = ET_xml.SubElement(polygon_tag, "attribute", attrib={"name": "content"})
            content_tag.text = content

    @staticmethod
    def _add_classification_subtree(
        sub_tree: ET_xml.Element, annotation: BaseAnnotation, clean_tags: bool = False
    ) -> None:
        if clean_tags:
            # remove existing classification tags
            for elem in list(sub_tree):
                if elem.tag == "tag":
                    map(elem.remove, list(elem))
                    sub_tree.remove(elem)

        for classification in annotation.classifications:
            classification_dict = dict()
            classification_dict["label"] = classification.class_name
            classification_dict["source"] = "generated"
            polygon_tag = ET_xml.SubElement(sub_tree, "tag", attrib=classification_dict)
            difficult_tag = ET_xml.SubElement(
                polygon_tag, "attribute", attrib={"name": "difficult"}
            )
            difficult_tag.text = "false"
