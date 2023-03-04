from pathlib import Path
import re

from .utils import runn
from .exceptions import FFmpegVideoDurationReadError


def _timestamp_to_s(timestamp: str) -> float:
    hours, minutes, seconds = map(float, timestamp.split(":"))
    total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds


def video_duration(video_path: Path, ffmpeg_path: Path | str):
    args = [
        f"{ffmpeg_path}",
        "-v",
        "32",
        "-hide_banner",
        "-i",
        f"{video_path}",
    ]
    succ, outs = runn([args], 1, getout=False, geterr=True, raw=False)

    match = re.search(
        r"Duration\:\s(\d?\d\d\:\d\d\:\d\d\.\d+)\,",
        outs[0],  # type:ignore
    )
    if match:
        return _timestamp_to_s(match.group(1))

    raise FFmpegVideoDurationReadError(
        f"Failed to read duration for file '{video_path}'"
    )
