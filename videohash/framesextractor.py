import os
import re
from pathlib import Path

import numpy as np

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
        timestamps = np.linspace(0, self.duration - 0.1, length)

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

    def _extract_seek(self, crop: list[str]):
        # generate timestamps to extract (-0.1 cuz FFmpeg baka)
        timestamps = np.linspace(0, self.duration - 0.1, self.frame_count)

        # build all commands
        commands: list[list[str]] = []
        for i, ts in enumerate(timestamps):
            frame_path = (
                self.output_dir
                / f"frame_{f'{i}'.zfill(len(str(self.frame_count)))}.jpeg"
            ).as_posix()
            commands.append(
                [
                    f"{self.ffmpeg_path}",
                    "-ss",
                    f"{ts}",
                    "-i",
                    f"{self.video_path}",
                    *crop,
                    "-frames:v",
                    "1",
                    "-s",
                    f"{self.frame_size}x{self.frame_size}",
                    frame_path,
                ]
            )

        return runn(commands, self.ffmpeg_threads)

    def _extract_framerate(self, crop: list[str]):
        command = [
            f"{self.ffmpeg_path}",
            "-i",
            f"{self.video_path}",
            *crop,
            "-s",
            f"{self.frame_size}x{self.frame_size}",
            "-r",
            f"{self.frame_count-2}/{self.duration}",
            "-vframes",
            f"{self.frame_count}",
            (self.output_dir / "frame_%07d.jpeg").as_posix(),
        ]
        return runn([command], n=1)

    def extract(self) -> None:
        """
        Extract the frames at every n seconds where n is the
        integer set to self.interval.

        :return: None

        :rtype: NoneType
        """
        crop = self.detect_crop(frames=3)

        if self.fixed:
            succ, outs = self._extract_seek(crop)

        else:
            succ, outs = self._extract_framerate(crop)

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
