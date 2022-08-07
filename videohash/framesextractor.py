import os
import re
from pathlib import Path
from typing import Collection

import numpy as np
from decord import VideoReader
from decord import cpu, gpu

from .exceptions import (
    FFmpegFailedToExtractFrames,
    FramesExtractorOutPutDirDoesNotExist,
)
from .utils import runn


class FramesExtractor:

    """
    Extract frames from the input video file and save at the output directory(frame storage directory).
    """

    def __init__(
        self,
        video_path: Path,
        output_dir: Path,
        duration: float,
        frame_count: int,
        frame_size: int,
        ffmpeg_threads: int,
        fixed: bool,
        ffmpeg_path: str,
    ) -> None:
        """
        Raises Exeception if video_path does not exists.
        Raises Exeception if output_dir does not exists or if not a directory.

        Checks  the ffmpeg installation and the path; thus ensure that we can use it.

        :return: None

        :rtype: NoneType

        :param video_path: absolute path of the video

        :param output_dir: absolute path of the directory
                           where to save the frames.

        :param interval: interval is seconds. interval must be an integer.
                         Extract one frame every given number of seconds.
                         Default is 1, that is one frame every second.

        :param ffmpeg_path: path of the ffmpeg software if not in path.

        """
        self.video_path = video_path
        self.output_dir = output_dir
        self.duration = duration
        self.frame_count = frame_count
        self.frame_size = frame_size
        self.ffmpeg_path = ffmpeg_path
        self.ffmpeg_threads = ffmpeg_threads
        self.fixed = fixed

        if not self.output_dir.is_dir():
            raise FramesExtractorOutPutDirDoesNotExist(
                f"No directory called '{self.output_dir}' found for storing the frames."
            )

        self.extract()

    def detect_crop(self, frames: int = 3) -> list[str]:
        """
        Detects the the amount of cropping to remove black bars.

        The method uses [ffmpeg.git] / libavfilter /vf_cropdetect.c
        to detect_crop for some fixed intervals.

        The mode of the detected crops is selected as the crop required.

        :return: FFmpeg argument -vf filter with detected crop parameter.
        """
        # generate timestamps to test
        length = 4  # amount of samples to test
        timestamps = [1 + x * (self.duration - 1) / length for x in range(length)]

        commands: list[list[str]] = []
        for ts in timestamps:
            commands.append(
                [
                    self.ffmpeg_path,
                    "-ss",
                    f"{ts}",
                    "-i",
                    self.video_path.as_posix(),
                    "-vframes",
                    f"{frames}",
                    "-vf",
                    "cropdetect",
                    "-f",
                    "null",
                    "-",
                ]
            )

        succ, outs = runn(commands, n=length, geterr=True)

        crop_list: list[str] = []
        for out in outs:
            crop_list.extend(
                re.findall(r"crop\=[0-9]{1,4}:[0-9]{1,4}:[0-9]{1,4}:[0-9]{1,4}", out)
            )

        if crop_list:
            mode = max(crop_list, key=crop_list.count)
            return ["-vf", mode]

        return []

    def extract(self) -> None:
        """
        Extract the frames at every n seconds where n is the
        integer set to self.interval.

        :return: None

        :rtype: NoneType
        """

        ffmpeg_path = self.ffmpeg_path
        video_path = self.video_path
        duration = self.duration
        output_dir = self.output_dir

        # crop = self.detect_crop(frames=3)
        crop: list[str] = []  # TODO

        if self.fixed:
            # generate timestamps to extract
            length = self.frame_count
            timestamps = [0 + x * duration / length for x in range(length)]

            commands: list[list[str]] = []
            for i, ts in enumerate(timestamps):
                frame_path = (
                    output_dir / f"frame_{f'{i}'.zfill(len(str(length)))}.jpeg"
                ).as_posix()
                commands.append(
                    [
                        f"{ffmpeg_path}",
                        "-ss",
                        f"{ts}",
                        "-i",
                        f"{video_path}",
                        *crop,
                        "-frames:v",
                        "1",
                        "-s",
                        f"{self.frame_size}x{self.frame_size}",
                        frame_path,
                    ]
                )

            succ, outs = runn(commands, self.ffmpeg_threads)

        else:
            command = [
                f"{ffmpeg_path}",
                "-i",
                f"{video_path}",
                *crop,
                "-s",
                f"{self.frame_size}x{self.frame_size}",
                "-r",
                f"{self.frame_count-1}/{self.duration}",
                "-vframes",
                f"{self.frame_count}",
                (output_dir / "frame_%07d.jpeg").as_posix(),
            ]
            succ, outs = runn([command], n=1)

        filenum = len(os.listdir(self.output_dir))

        if filenum == self.frame_count:
            return  # return even if we had errors cuz sometimes files be weird

        if not succ:
            raise FFmpegFailedToExtractFrames(
                f"FFmpeg errors while extracting frames with:\n'{outs[-1]}'"
            )

        raise FFmpegFailedToExtractFrames(
            f"Wrong number of frames extracted by FFmpeg. \nExpected {self.frame_count} got {filenum} in {self.output_dir}."
        )


def extract_frames(
    video_file: Path, frame_count: int, frame_size: int
) -> np.ndarray:
    """
    Extract a number of evenly spaced frames from `video_file`.

    :param video_file: Video file to extract frames from.
    :param frame_count: Number of frames to extract.
    :param frame_size: Side length of resulting square frames.
    :return: Array of square Image arrays.
    """
    vr = VideoReader(video_file.as_posix(), height=frame_size, width=frame_size)

    # generate evenly spaced indices
    indices = np.linspace(0, len(vr) - 1, frame_count, dtype=np.uint64)

    frames: np.ndarray = vr.get_batch(indices).asnumpy()
    return frames


def extract_frames_seek(
    video_file: Path, frame_count: int, frame_size: int
) -> Collection[np.ndarray]:
    """
    Extract a number of evenly spaced frames from `video_file`.

    :param video_file: Video file to extract frames from.
    :param frame_count: Number of frames to extract.
    :param frame_size: Side length of resulting square frames.
    :return: Array of square Image arrays.
    """
    vr = VideoReader(video_file.as_posix(), height=frame_size, width=frame_size)

    frames = []
    # generate evenly spaced indices
    indices = np.linspace(0, len(vr) - 1, frame_count, dtype=np.uint64)
    for i in indices:
        vr.seek(i)
        frames.append(vr.next().asnumpy())

    # frames: np.ndarray = vr.get_batch(indices).asnumpy()
    return frames
