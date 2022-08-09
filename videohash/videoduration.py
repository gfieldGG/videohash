from pathlib import Path

from .utils import runn
from .exceptions import FFprobeNoVideoDurationSpecified, FFprobeVideoDurationReadError


def video_duration(video_path: Path) -> float:
    """Get video duration using FFprobe."""
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
        video_path.as_posix(),
    ]
    succ, outs = runn([args], 1, getout=True)

    if succ:
        try:
            return float(outs[0].strip())
        except ValueError as e:
            raise FFprobeNoVideoDurationSpecified(
                f"No duration on first video stream of '{video_path}'"
            ) from None

    raise FFprobeVideoDurationReadError(
        f"ffprobe error while trying to read video duration from '{video_path}':\n{outs[0]}"
    )
