# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for different utility operations regarding drawing on images"""

import colorsys
import copy
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.segmentation import PolygonType, Segmentation


def generate_detector_colors(num_classes: int):  # type: ignore
    """
    Generates a color palette for object detector

    Args:
        num_classes: int, the number of classes to distinguish

    Returns:
        List[Tuples(int, int, int)] specifying bounding box color
        with len(List) == number of classes

    """

    # Generate colors for drawing bounding boxes.
    hsv_tuples = [(x / num_classes, 1.0, 1.0) for x in range(num_classes)]

    hsv_colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))

    rgb_colors = list(
        map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), hsv_colors)
    )

    np.random.seed(10101)  # Fixed seed for consistent colors across runs.
    np.random.shuffle(rgb_colors)  # Shuffle colors to decorrelate adjacent classes.
    np.random.seed(None)  # Reset seed to default.

    return rgb_colors


def draw_on_image(
    frame: np.ndarray,  # type: ignore[type-arg]
    rgb_colors: List[Tuple[int, int, int]],
    cv2_font: int = cv2.FONT_HERSHEY_COMPLEX,
    bounding_boxes: Optional[List[BoundingBox]] = None,
    segmentations: Optional[List[Segmentation]] = None,
    flip_image: bool = False,
    draw_caption: Optional[bool] = True,
    thickness: Optional[int] = None,
    font_scale: float = 0.9,
) -> np.ndarray:  # type: ignore[type-arg]
    """
    Draws annotations on the given image
    Args:
        frame: Numpy array, the image
        rgb_colors: List of colors, for matching a class-name to an index of the rgb-color list
        cv2_font: int, font of cv2 textual annotations
        bounding_boxes: Optional List of BoundingBox objects
        segmentations: Optional List of Segmentation objects
        flip_image: Bool, whether to flip the image or not
        draw_caption: Optional bool, whether to draw a caption text or not
        thickness: Optional int, defines the thickness of the annotation lines
        font_scale: float, defines the size of a font

    Returns: Numpy array, the given image decorated with annotations

    """

    frame = copy.deepcopy(frame)

    if bounding_boxes is not None:
        for bounding_box in bounding_boxes:
            frame = draw_bbox_cv2(
                frame=frame,
                color=rgb_colors[bounding_box.class_id],
                box=bounding_box.box,
                flip_image=flip_image,
                cv2_font=cv2_font,
                label=bounding_box.class_name,
                draw_caption=draw_caption,
                thickness=thickness,
                font_scale=font_scale,
                score=bounding_box.score,
            )

    if segmentations is not None:
        for segmentation in segmentations:
            frame = draw_polygon_cv2(
                frame=frame,
                polygon=segmentation.polygon,
                color=rgb_colors[segmentation.class_id],
                flip_image=flip_image,
                cv2_font=cv2_font,
                label=segmentation.class_name,
                draw_caption=draw_caption,
                thickness=thickness,
                font_scale=font_scale,
                score=segmentation.score,
            )

    return frame


def draw_polygon_cv2(
    frame: np.ndarray,  # type: ignore[type-arg]
    color: Tuple[int, int, int],
    polygon: Optional[PolygonType],
    flip_image: bool = False,
    cv2_font: int = cv2.FONT_HERSHEY_COMPLEX,
    label: Optional[str] = None,
    draw_caption: Optional[bool] = True,
    thickness: Optional[int] = None,
    font_scale: float = 0.9,
    score: Optional[float] = None,
) -> np.ndarray:  # type: ignore[type-arg]
    """
    Draw a polygon on a given image
    Args:
        frame: Numpy array, the image
        color: Tuple of three int values, a rgb color
        polygon: Optional List of Tuples, the polygon coordinates # TODO why Optional?
        flip_image: Bool, whether to flip the image or not
        cv2_font: int, font of cv2 textual annotations
        label: Optional string, label (class information) of polygon
        draw_caption: Optional bool, whether to draw a caption text or not
        thickness: Optional int, defines the thickness of the polygon lines
        font_scale: float, defines the size of a font
        score: Optional float, defines the confidence for the label of the polygon

    Returns: Numpy array, the given image decorated with a polygon

    """

    if polygon is None:
        return frame

    if thickness is None:
        thickness = (frame.shape[0] + frame.shape[1]) // 450

    # TODO: add box.to_tuple(...) ?
    if flip_image:
        # TODO: what to do when image is flipped?
        pass
    else:
        pts = np.array(polygon, np.int32)
        pts = pts.reshape((-1, 1, 2))

        frame = cv2.polylines(
            img=frame, pts=[pts], isClosed=True, color=color, thickness=thickness
        )

    # TODO: add caption
    if draw_caption and label is not None:

        if score is not None:
            caption = f"{label}_{score:.2f}"
        else:
            caption = label

        cv2.putText(
            img=frame,
            text=caption,
            org=(int(polygon[0][0]), int(polygon[0][1])),
            fontFace=cv2_font,
            fontScale=font_scale,
            color=color,
            thickness=thickness,
        )

    return frame


def draw_bbox_cv2(
    frame: np.ndarray,  # type: ignore[type-arg]
    color: Tuple[int, int, int],
    box: Box,
    flip_image: bool = False,
    cv2_font: int = cv2.FONT_HERSHEY_COMPLEX,
    label: Optional[str] = None,
    draw_caption: Optional[bool] = True,
    thickness: Optional[int] = None,
    font_scale: float = 0.9,
    score: Optional[float] = None,
    text_origin: Optional[Tuple[int, int]] = None,
) -> np.ndarray:  # type: ignore[type-arg]
    """
    Draws a bounding box on the given image
    Args:
        frame: Numpy array, the image
        color: Tuple of three int values, a rgb color
        box: Box, a bounding box object
        flip_image: Bool, whether to flip the image or not
        cv2_font: int, font of cv2 textual annotations
        label: Optional string, label (class information) of polygon
        draw_caption: Optional bool, whether to draw a caption text or not
        thickness: Optional int, defines the thickness of the box lines
        font_scale: float, defines the size of a font
        score: Optional float, defines the confidence for the label of the polygon
        text_origin: position of text in image

    Returns: Numpy array, the given image decorated with a bounding box

    """

    if box is None:
        return frame

    img_w = frame.shape[0]

    if thickness is None:
        thickness = (frame.shape[0] + frame.shape[1]) // 450

    # TODO: add box.to_tuple(...) ?
    if flip_image:
        frame = cv2.rectangle(
            frame,
            (img_w - box.xmin, box.ymin),
            (img_w - box.xmax, box.xmin),
            color,
            thickness,
        )
    else:
        frame = cv2.rectangle(frame, (box.xmin, box.ymin), (box.xmax, box.ymax), color, thickness)

    if draw_caption and label is not None:

        # TODO: adapt position?
        # if box.ymin - label_size[1] >= 0:
        #     if flip_image:
        #         text_origin = (img_w - box.xmin, box.ymin - label_size[1])
        #     else:
        #         text_origin = (box.xmin, box.ymin - label_size[1])
        # else:
        #     if flip_image:
        #         text_origin = (img_w - box.xmin, box.ymin + 1)
        #     else:
        #         pass
        #
        # label_size = cv2.getTextSize(label, cv2_font, font_scale, thickness)

        if text_origin is None:
            text_x = box.xmin
            text_y = max(box.ymin - 5, 20)
            text_origin = (text_x, text_y)

        if score is not None:
            caption = f"{label}_{score:.2f}"
        else:
            caption = label

        cv2.putText(
            img=frame,
            text=caption,
            org=text_origin,
            fontFace=cv2_font,
            fontScale=font_scale,
            color=color,
            thickness=thickness,
        )

    return frame


def draw_on_pil_image(
    image: Union[np.ndarray, Image.Image],  # type: ignore[type-arg]
    bounding_boxes: List[BoundingBox],
    font_path: str,
    rgb_colors: List[Tuple[int, int, int]],
    thickness: int = 2,
    fill_background: bool = True,
    is_ground_truth: bool = False,
) -> np.ndarray:  # type: ignore[type-arg]
    """
    Draw a given list of bounding-boxes on a given image using pillow.

    Args:
        image: either a Numpy array or a PIL Image object
        bounding_boxes: List of BoundingBox objects
        font_path: String, path to the font file which should be used
        rgb_colors: List of colors, for matching a class-name to an index of the rgb-color list
        thickness: int, thickness of the box lines
        fill_background: Bool, whether to put the label on white background or not
        is_ground_truth: Bool, depending on ground truth or not, the label will be drawn
            in the upper left corner (no gt) or in the lower left corner (is gt)

    Returns:
        Numpy array, the given image decorated with annotations
    """

    white_color = (255, 255, 255, 15)

    if type(image) is np.ndarray:
        image = Image.fromarray(image)

    assert isinstance(image, Image.Image)

    font = ImageFont.truetype(
        font=font_path, size=np.floor(0.042 * image.size[1] + 0.1).astype("int32")
    )

    draw = ImageDraw.Draw(image)

    for bounding_box in bounding_boxes:

        label = "{} {:.2f}".format(bounding_box.class_name, bounding_box.score)
        label_size = draw.textsize(label, font)

        if is_ground_truth:
            text_origin = (
                float(bounding_box.box.xmin),
                float(bounding_box.box.ymax - label_size[1]),
            )
        else:
            if bounding_box.box.ymin - label_size[1] >= 0:
                text_origin = (
                    float(bounding_box.box.xmin),
                    float(bounding_box.box.ymin - label_size[1]),
                )
            else:
                text_origin = (
                    float(bounding_box.box.xmin),
                    float(bounding_box.box.ymin + 1),
                )

        color = rgb_colors[bounding_box.class_id]

        if fill_background:
            draw.rectangle(
                (
                    text_origin,
                    (text_origin[0] + label_size[0], text_origin[1] + label_size[1]),
                ),
                fill=white_color,
            )

            draw.text(text_origin, label, fill=(0, 0, 0, 15), font=font)
        else:
            draw.text(text_origin, label, fill=color, font=font)

        for draw_step in range(thickness):
            draw.rectangle(
                (
                    float(bounding_box.box.xmin + draw_step),
                    float(bounding_box.box.ymin + draw_step),
                    float(bounding_box.box.xmax - draw_step),
                    float(bounding_box.box.ymax - draw_step),
                ),
                outline=color,
            )

    del draw

    return np.asarray(image)
