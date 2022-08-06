import os
import re
import shlex
from shutil import which
from subprocess import PIPE, Popen, check_output
from typing import Optional, Union

from .exceptions import (
    FFmpegError,
    FFmpegFailedToExtractFrames,
    FFmpegNotFound,
    FramesExtractorOutPutDirDoesNotExist,
)
from .utils import does_path_exists, runn

# python module to extract the frames from the input video.
# Uses the FFmpeg Software to extract the frames.


class FramesExtractor:

    """
    Extract frames from the input video file and save at the output directory(frame storage directory).
    """

    def __init__(
        self,
        video_path: str,
        output_dir: str,
        duration: float,
        frame_count: int,
        frame_size: int,
        ffmpeg_threads: int,
        fixed: bool,
        ffmpeg_path: Optional[str] = None,
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
        self.ffmpeg_threads = ffmpeg_threads
        self.fixed = fixed
        self.ffmpeg_path = ""
        if ffmpeg_path:
            self.ffmpeg_path = ffmpeg_path

        if not does_path_exists(self.video_path):
            raise FileNotFoundError(
                f"No video found at '{self.video_path}' for frame extraction."
            )

        if not does_path_exists(self.output_dir):
            raise FramesExtractorOutPutDirDoesNotExist(
                f"No directory called '{self.output_dir}' found for storing the frames."
            )

        self._check_ffmpeg()

        self.extract()

    def _check_ffmpeg(self) -> None:
        """
        Checks the ffmpeg path and runs 'ffmpeg -version' to verify that the
        software, ffmpeg is found and works.

        :return: None

        :rtype: NoneType
        """

        if not self.ffmpeg_path:

            if not which("ffmpeg"):

                raise FFmpegNotFound(
                    "FFmpeg is not on the system path. Install FFmpeg and add it to the path."
                    + "Or you can also pass the path via the 'ffmpeg_path' parameter."
                )
            else:

                self.ffmpeg_path = str(which("ffmpeg"))

        # Check the ffmpeg path
        try:
            # check_output will raise FileNotFoundError if it does not find ffmpeg
            output = check_output([str(self.ffmpeg_path), "-version"]).decode()

        except FileNotFoundError:
            raise FFmpegNotFound(f"FFmpeg not found at '{self.ffmpeg_path}'.")

        else:

            if "ffmpeg version" not in output:
                raise FFmpegError(
                    f"ffmpeg at '{self.ffmpeg_path}' is not really ffmpeg. Output of ffmpeg -version is \n'{output}'."
                )

    @staticmethod
    def detect_crop(
        video_path: str,
        duration: float,
        ffmpeg_path: str,
        frames: int = 3,
    ) -> list[str]:
        """
        Detects the the amount of cropping to remove black bars.

        The method uses [ffmpeg.git] / libavfilter /vf_cropdetect.c
        to detect_crop for some fixed intervals.

        The mode of the detected crops is selected as the crop required.

        :return: FFmpeg argument -vf filter and confromable crop parameter.

        :rtype: str
        """
        # generate timestamps to test
        length = 4  # amount of samples to test
        timestamps = [1 + x * (duration - 1) / length for x in range(length)]

        commands: list[list[str]] = []
        for ts in timestamps:
            commands.append(
                [
                    ffmpeg_path,
                    "-ss",
                    f"{ts}",
                    "-i",
                    video_path,
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

        mode = None
        if crop_list:
            mode = max(crop_list, key=crop_list.count)

        if mode:
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

        crop = FramesExtractor.detect_crop(
            video_path=video_path,
            duration=duration,
            frames=3,
            ffmpeg_path=ffmpeg_path,
        )

        if self.fixed:
            # generate timestamps to extract
            length = self.frame_count
            timestamps = [0 + x * duration / length for x in range(length)]

            commands: list[list[str]] = []
            for i, ts in enumerate(timestamps):
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
                        output_dir
                        + f"video_frame_{f'{i}'.zfill(len(str(length)))}.jpeg",
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
                output_dir + "video_frame_%07d.jpeg",
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
