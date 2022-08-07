import re
from shutil import which
from pathlib import Path

from .utils import runn


def video_duration(video_path: Path, ffmpeg_path: str = "ffmpeg") -> float:
    """
    Retrieve the exact video duration as echoed by FFmpeg and return
    the duration in seconds. Maximum duration supported is 999 hours, above
    which the regex is doomed to fail(no match).

    :param video_path: Absolute path of the video file.

    :param ffmpeg_path: Path of the FFmpeg software if not in path.

    :return: Video length(duration) in seconds.

    :rtype: float
    """
    command = [ffmpeg_path, "-i", video_path.as_posix()]
    succ, outs = runn([command], 1, geterr=True)

    match = re.search(
        r"Duration\:(\s\d?\d\d\:\d\d\:\d\d\.\d\d)\,",
        (outs[0]),
    )

    if match:
        duration_string = match.group(1)
    else:
        return 0.0

    hours, minutes, seconds = duration_string.strip().split(":")

    return float(hours) * 60.00 * 60.00 + float(minutes) * 60.00 + float(seconds)


def video_duration_ffprobe(video_path: str) -> float:
    args = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        "-i",
        video_path,
    ]

    succ, outs = runn([args], 1, getout=True)

    if succ:
        return float(outs[0])

    return 0.0


def video_frames(video_path: str) -> int:
    args = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_frames",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        "-i",
        video_path,
    ]
    succ, outs = runn([args], 1, getout=True)

    if succ:
        return int(outs[0])

    return 0
