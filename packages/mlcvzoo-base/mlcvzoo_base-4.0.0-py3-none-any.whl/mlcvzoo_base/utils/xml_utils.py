# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for different utility operations regarding xml documents and objects"""
import logging
import os
import xml.etree.ElementTree as ET_xml

from mlcvzoo_base.utils import ensure_dir

logger = logging.getLogger(__name__)


def create_xml_root(file_path: str, width: int, height: int, depth: str = "3") -> ET_xml.Element:
    """
    Creates the root-xml-structure, which is used to generate
    annotation files. These annotation contain information
    about the bounding boxes specified for a training image.

    The format of the xml-files is the same as the one used
    in PASCAL VOC: http://host.robots.ox.ac.uk/pascal/VOC/

    Args:
        file_path: String, complete path of the image, including the image name
        width: int, width of the image
        height: int, height of the image
        depth: String, channel of the images, 3 stands for color image

    Returns: the root object

    """

    root = ET_xml.Element("annotation")
    ET_xml.SubElement(root, "filename").text = os.path.basename(file_path)
    ET_xml.SubElement(root, "folder").text = os.path.basename(os.path.dirname(file_path))
    ET_xml.SubElement(root, "path").text = file_path

    source = ET_xml.SubElement(root, "source")
    ET_xml.SubElement(source, "database").text = "Unknown"

    # images size
    size = ET_xml.SubElement(root, "size")

    ET_xml.SubElement(size, "width").text = str(width)
    ET_xml.SubElement(size, "height").text = str(height)

    ET_xml.SubElement(size, "depth").text = depth

    ET_xml.SubElement(root, "segmented").text = "0"

    return root


def create_bbox_xml_entry(
    root: ET_xml.Element, name: str, xmin: int, ymin: int, xmax: int, ymax: int
) -> ET_xml.Element:
    """
    Creates an element in a xml-structure, containing the information
    about a bounding box.

    The format of the xml-files is the same as the one used
    in PASCAL VOC: http://host.robots.ox.ac.uk/pascal/VOC/

    xmin, ymin, xmax, ymax coordinates of the bounding box

    Args:
        root: XML Element, the root object, where the xml-structure should be put in
        name: String, class name of the bounding box
        xmin: int, xmin coordinate of bounding box
        ymin: int, ymin coordinate of bounding box
        xmax: int, xmax coordinate of bounding box
        ymax: int, ymax coordinate of bounding box

    Returns: XML Element, the new root object

    """

    object_entry = ET_xml.SubElement(root, "object")

    # objects
    ET_xml.SubElement(object_entry, "name").text = name
    ET_xml.SubElement(object_entry, "pose").text = "Unspecified"
    ET_xml.SubElement(object_entry, "truncated").text = "0"
    ET_xml.SubElement(object_entry, "difficult").text = "0"

    bbox_entry = ET_xml.SubElement(object_entry, "bndbox")

    # bounding boxes
    ET_xml.SubElement(bbox_entry, "xmin").text = str(int(xmin))
    ET_xml.SubElement(bbox_entry, "ymin").text = str(int(ymin))
    ET_xml.SubElement(bbox_entry, "xmax").text = str(int(xmax))
    ET_xml.SubElement(bbox_entry, "ymax").text = str(int(ymax))

    return root


def xml_tree_to_file(xml_file_path: str, xml_tree: ET_xml.ElementTree) -> None:
    """
    Writes XML object to given file

    Args:
        xml_file_path: String, file path
        xml_tree: XML ElementTree

    Returns: None

    """
    logger.info("Write xml-tree to file: %s", xml_file_path)

    ensure_dir(file_path=xml_file_path, verbose=True)

    tree_string = ET_xml.tostring(element=xml_tree.getroot()).decode("utf-8")

    with open(file=xml_file_path, mode="w", encoding="utf8") as xml_file:
        xml_file.write(tree_string)
