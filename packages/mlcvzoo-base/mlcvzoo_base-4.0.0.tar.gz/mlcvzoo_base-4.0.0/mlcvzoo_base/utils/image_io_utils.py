# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for different utility operations regarding image files"""

from __future__ import annotations

import copy
import logging
import os
import time
from typing import Any, Iterator, List, Optional, Tuple

import cv2
import imageio
import numpy as np

from mlcvzoo_base.utils.file_utils import ensure_dir

logger = logging.getLogger(__name__)


def _scale_frame(
    frame: np.ndarray, output_shape: int  # type: ignore[type-arg]
) -> Tuple[np.ndarray, Tuple[int, int]]:  # type: ignore[type-arg]
    """

    Args:
        frame: Numpy array, image
        output_shape: int, shape of the output

    Returns: Tuple of the scaled frame and shape of the frame in (x,y)

    """

    # TODO: check if this results in memory issues

    if output_shape > 0:
        scaled_frame = copy.deepcopy(frame)

        scale_factor = output_shape / scaled_frame.shape[0]
        resize_shape = (
            int(frame.shape[1] * scale_factor),
            int(frame.shape[0] * scale_factor),
        )

        scaled_frame = cv2.resize(scaled_frame, resize_shape, interpolation=cv2.INTER_AREA)
        return scaled_frame, resize_shape
    else:
        return frame, (frame.shape[1], frame.shape[0])


class VideoLiveOutput:
    """Class for displaying a video"""

    MODE_TERMINATE = "terminate"
    MODE_GO = "go"
    MODE_STEP = "step"

    KEY_CLOSE = "q"
    KEY_STEP = "s"
    KEY_GO = "c"
    KEY_NEXT = "n"

    MODES = [MODE_TERMINATE, MODE_GO, MODE_STEP]

    # TODO: Better name for use_mode?
    def __init__(
        self,
        use_mode: bool = True,
        show_fps: bool = False,
        window_name: str = "Video stream",
        resize_window: bool = True,
        window_size: int = 500,
        mode: Optional[str] = None,
    ):
        self.use_mode = use_mode
        self.show_fps = show_fps
        self.window_name = window_name
        self.resize_window = resize_window
        self.window_size = window_size

        self.mode = VideoLiveOutput.MODE_STEP
        if mode is not None:
            if mode not in self.MODES:
                raise ValueError("Invalid mode='%s' has to be one of '%s'" % (mode, self.MODES))

            self.mode = mode
        self.frame = 0
        self.resized_window = False
        self.current_fps = 0.0

        self.start = time.time()
        self.end = time.time() - self.start

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        logger.info(
            "Create VideoLiveOutput with title '%s'. "
            "Step and continuous mode.\n"
            "Press %s to continue, %s to step. "
            "Press %s for next frame.",
            self.window_name,
            VideoLiveOutput.KEY_GO,
            VideoLiveOutput.KEY_STEP,
            VideoLiveOutput.KEY_NEXT,
        )

    def output_frame(self, frame: np.ndarray, img_info: str = "") -> None:  # type: ignore[type-arg]
        """
        Creates and shows the output frame based on class attributes and parameters

        Args:
            frame: Numpy array, the frame
            img_info: String, any information that should be printed on the image

        Returns: None

        """

        if self.mode != VideoLiveOutput.MODE_TERMINATE:

            self.end = time.time() - self.start

            # will only be executed once
            if not self.resized_window:
                scale_factor = frame.shape[1] / frame.shape[0]

                if self.resize_window is True:
                    window_height = self.window_size
                else:
                    window_height = frame.shape[0]

                cv2.resizeWindow(
                    winname=self.window_name,
                    height=window_height,
                    width=int(window_height * scale_factor),
                )

                self.resized_window = True

            if self.show_fps:
                self.current_fps = 1 / self.end if self.end != 0.0 else 0.0

                # put image name in visible image
                cv2.putText(
                    img=frame,
                    text="{:.4f}".format(self.current_fps),
                    org=(20, 20),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.75,
                    color=(255, 255, 255),
                    thickness=2,
                    lineType=cv2.LINE_AA,
                )

            if img_info != "":
                # put image name in visible image
                cv2.putText(
                    img=frame,
                    text="{}".format(os.path.basename(img_info)),
                    org=(20, 40),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.75,
                    color=(255, 255, 255),
                    thickness=2,
                    lineType=cv2.LINE_AA,
                )

            cv2.imshow(self.window_name, frame)
            key = 0

            if self.use_mode:
                while self.mode == VideoLiveOutput.MODE_STEP and key != ord(
                    VideoLiveOutput.KEY_NEXT
                ):
                    key = cv2.waitKey(0) & 0xFF
                    if key == ord(VideoLiveOutput.KEY_GO):
                        self.mode = VideoLiveOutput.MODE_GO

                    if key == 27 or key == ord(VideoLiveOutput.KEY_CLOSE):
                        self.close()

                if self.mode == VideoLiveOutput.MODE_GO:
                    key = cv2.waitKey(1) & 0xFF

                if key == ord(VideoLiveOutput.KEY_STEP):
                    self.mode = VideoLiveOutput.MODE_STEP

                if key == 27 or key == ord(VideoLiveOutput.KEY_CLOSE):
                    self.close()

            self.frame += 1

            self.start = time.time()

    def close(self) -> None:
        """Closes open windows"""

        self.mode = VideoLiveOutput.MODE_TERMINATE
        cv2.destroyAllWindows()

    def is_terminated(self) -> bool:
        """Returns current termination status of the class"""

        return self.mode == VideoLiveOutput.MODE_TERMINATE


class VideoFileInput:
    """Class for handling a video and navigating through its frames"""

    def __init__(self, path: str):

        logger.debug("Init VideoFileInput for video '%s'", path)

        self.cap = cv2.VideoCapture(path)

        self.current_frame: Optional[np.ndarray] = None  # type: ignore[type-arg]

    def goto_frame(self, num: int) -> None:
        """Sets current frame to given position

        Args:
            num: int, number of frame that is to be reached

        Returns: None

        """

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, num)

    def next_frame(self) -> Iterator[Optional[np.ndarray]]:  # type: ignore[type-arg]
        """
        Jumps to the next frame

        Returns: Iterator object based on the current frame

        """

        while True:
            finished_stream, self.current_frame = self.get_image()
            if not finished_stream:
                self.current_frame = None
                break

            yield self.current_frame
        yield self.current_frame

    def get_image(self, frame_num: Optional[int] = None) -> Any:
        """
        Returns image at the given frame or the next video frame

        Args:
            frame_num: Optional int, position of frame

        Returns: Any, either the requested frame or the next video frame

        """

        if frame_num is not None:
            self.goto_frame(frame_num)

        return self.cap.read()

    def has_next(self) -> bool:
        """
        Checks whether the current frame is available

        Returns: Bool, the availability of current_frame attribute
        """

        return self.current_frame is not None

    def skip_frames(self, number_frames: int) -> None:
        """
        Skips the given amount of frames, sets the current_frame attribute to the new frame

        Args:
            number_frames: int, the number of frames to be skipped

        Returns: None

        """

        for i in range(0, number_frames):
            finished_stream = self.cap.grab()

            if finished_stream:
                self.current_frame = None

    def number_of_frames(self) -> int:
        """Returns: int, number of overall frames in the video"""

        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def __del__(self):  # type: ignore
        self.cap.release()


class GifFileOutput:
    """Class for creating and saving gifs"""

    gif_frame_list: List[np.ndarray] = []  # type: ignore[type-arg]

    def __init__(
        self,
        output_path: str,
        fps: int,
        output_shape: int,
        ask_for_dir_creation: bool = True,
    ):
        self.output_path = output_path
        self.fps = fps
        self.output_shape = output_shape
        self.ask_for_dir_creation = ask_for_dir_creation

    def add_frame(self, frame: np.ndarray) -> None:  # type: ignore[type-arg]
        """
        Adds a frame to the gif_frame_list attribute
        Args:
            frame: Numpy array, the frame to be added

        Returns: None

        """

        scaled_frame, _ = _scale_frame(frame=frame, output_shape=self.output_shape)

        self.gif_frame_list.append(scaled_frame)

    def save_gif(self) -> None:
        """
        Saves the gif_frame_list to a file specified in the output_path attribute

        Returns: None

        """

        if len(self.gif_frame_list) > 0:
            self.__ensure_gif_dir()

            if os.path.isdir(os.path.dirname(self.output_path)):
                logger.debug("Creating gif ...")
                imageio.mimsave(
                    uri=self.output_path, ims=self.gif_frame_list, fps=self.fps  # type: ignore
                )
                logger.info("Saved gif to: %s", self.output_path)
        else:
            logger.warning(
                "WARNING: image list for gif creation is emtpy! Will not generate gif..."
            )

    def __ensure_gif_dir(self) -> None:
        if not os.path.isdir(os.path.dirname(self.output_path)):
            if self.ask_for_dir_creation:
                logger.info(
                    "Create directory for gif-path: %s?\n <y> or <n>",
                    self.output_path,
                )

                keyboard_input = input()

                if keyboard_input == "y":
                    os.makedirs(name=self.output_path, exist_ok=True)


class VideoFileOutput:
    """Class for writing a video to a file"""

    def __init__(
        self,
        path: str,
        output_shape: int,
        fps: int = 25,
    ):
        self.path = path
        self.fps = fps
        self.output_shape = output_shape

        self.open = False

        assert len(path) > 0

    def add_frame(self, frame: np.ndarray, img_info: str = "") -> None:  # type: ignore[type-arg]
        """
        Adds a frame to a video by adding frame information if available, resizing the frame
        and writing it to the location specified in path attribute

        Args:
            frame: Numpy array, the frame to be added
            img_info: String, any information that should be printed on the image

        Returns: None

        """

        if not self.open:
            ensure_dir(file_path=self.path, verbose=True)

            logger.info("Open VideoWriter for video-path: %s", self.path)

            scaled_frame, resize_shape = _scale_frame(frame=frame, output_shape=self.output_shape)

            self.video_writer = cv2.VideoWriter(
                filename=self.path,
                fourcc=cv2.VideoWriter_fourcc(*"mp4v"),
                fps=self.fps,
                frameSize=(
                    resize_shape[0],
                    resize_shape[1],
                ),  # opencv uses (y,x) format
            )
            # filename, fourcc, fps, frameSize, isColor = None
            self.open = True

        if img_info != "":
            # put image name in visible image
            cv2.putText(
                img=frame,
                text="{}".format(os.path.basename(img_info)),
                org=(20, 40),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.75,
                color=(255, 255, 255),
                thickness=2,
                lineType=cv2.LINE_AA,
            )

        scaled_frame, resize_shape = _scale_frame(frame=frame, output_shape=self.output_shape)
        self.video_writer.write(scaled_frame)

    def close(self) -> None:
        """Closing the VideoWriter"""

        if self.open:
            logger.info("Write video to: %s", self.path)
            self.video_writer.release()
