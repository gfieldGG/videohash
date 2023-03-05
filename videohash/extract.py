import io
import re
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from .exceptions import FFmpegFailedToExtractFrames
from .utils import runn


def _detect_crop(
    video_path: Path,
    duration: float,
    ffmpeg_path: Path | str,
    samples: int = 4,
    samplesize: int = 2,
):
    """
    Detect video crop using ffmpeg `cropdetect` and return crop values as `[-vf, ]` to use in ffmpeg commands.

    :param samples: The number of (evenly spaced) timestamps to analyze.
    :param samplesize: The amount of frames to analyze per timestamp (at least 2)
    """
    if samplesize < 2:
        raise ValueError(
            f"samplesize for crop detection must be at least two (got '{samplesize}')"
        )

    # generate timestamps to test
    timestamps = _get_timestamps(duration, samples)

    commands: list[list[str]] = []
    for ts in timestamps:
        commands.append(
            [
                f"{ffmpeg_path}",
                "-v",
                "32",
                "-hide_banner",
                "-ss",
                f"{ts}",
                "-i",
                f"{video_path}",
                "-frames:v",
                f"{samplesize}",
                "-vf",
                "cropdetect",
                "-f",
                "null",
                "-",
            ]
        )

    succ, outs = runn(commands, n=samples, getout=True, geterr=True, raw=False)

    crop_list: list[str] = []
    for out in outs:
        crop_list.extend(
            re.findall(
                r"crop\=[0-9]{1,4}:[0-9]{1,4}:[0-9]{1,4}:[0-9]{1,4}", out  # type:ignore
            )
        )

    if crop_list:
        mode = max(crop_list, key=crop_list.count)
        return ["-vf", mode]

    return []


def extract_frames(
    video_path: Path,
    duration: float,
    frame_count: int,
    frame_size: int,
    ffmpeg_threads: int,
    ffmpeg_path: Path | str,
    maxerrors: int,
) -> list[Image.Image]:
    crop = _detect_crop(
        video_path=video_path,
        duration=duration,
        ffmpeg_path=ffmpeg_path,
    )

    # timestamps to extract
    timestamps = _get_timestamps(duration, frame_count)

    # build all commands
    commands: list[list[str]] = []
    for i, ts in enumerate(timestamps):
        commands.append(
            [
                f"{ffmpeg_path}",
                "-v",
                "1",
                "-ss",
                f"{ts}",
                "-i",
                f"{video_path}",
                *crop,
                "-frames:v",
                "1",
                "-s",
                f"{frame_size}x{frame_size}",
                "-f",
                "image2pipe",
                "-",
            ]
        )

    succ, outs = runn(commands, n=ffmpeg_threads, getout=True, raw=True)

    # try to parse stdouts as Images
    frames: list[Image.Image] = []
    errs = 0
    for i, x in enumerate(outs):
        try:
            img = Image.open(io.BytesIO(x))  # type:ignore

        except UnidentifiedImageError:
            if errs < maxerrors:
                errs += 1
                img = Image.new("RGB", (frame_size, frame_size))
            else:
                raise FFmpegFailedToExtractFrames(
                    f"Too many errors extracting frames from '{video_path}'\nMost recently frame #{i} at timestamp '{timestamps[i]}'"
                ) from None

        frames.append(img)

    return frames


def _get_timestamps(duration: float, n: int) -> list[float]:
    """Generate a list of `n` evenly spaced timestamps in `duration` excluding the start and end time."""

    timestamps = np.linspace(0, duration, n + 1, endpoint=False)
    return timestamps[1:].tolist()
