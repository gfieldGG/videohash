from pathlib import Path
from subprocess import check_output
from math import isqrt

import imagehash
import numpy as np

from .exceptions import (
    FFmpegError,
    FFmpegNotFound,
    FFmpegVideoDurationReadError,
    VideoHashNoDuration,
)
from .extract import extract_frames
from .collage import make_collage
from .videoduration import video_duration
from .utils import runn


class VideoHash:

    """
    VideoHash class provides an interface for computing a perceptual video hash for videos supported by FFmpeg.
    """

    def __init__(
        self,
        video_path: Path | str,
        hash_length: int = 256,
        frame_count: int = 16,
        frame_size: int = 240,
        ffmpeg_threads: int = 4,
        ffmpeg_path: Path | str = "ffmpeg",
    ) -> None:
        """
        :param video_path: Absolute path of the input video file.
        :return: None
        """
        if hash_length < 4 or isqrt(hash_length) ** 2 != hash_length:
            raise ValueError(
                f"Invalid hash length '{hash_length}'.\nMust be greater than or equal to 4 and a perfect square."
            )
        self.hashlength = hash_length

        if not isinstance(video_path, Path):
            video_path = Path(video_path)
        self.video_path = video_path.resolve()
        if not video_path.is_file():
            raise FileNotFoundError(f"No video found at '{self.video_path}'")

        ffmpeg_path = _check_ffmpeg(ffmpeg_path=ffmpeg_path)

        try:
            self.duration = video_duration(self.video_path, ffmpeg_path)
        except FFmpegVideoDurationReadError as e:
            raise VideoHashNoDuration(
                f"Failed to get video duration using ffprobe. Cannot generate phash without duration."
            ) from e

        self._frame_count = frame_count
        self._frame_size = frame_size

        frames = extract_frames(
            self.video_path,
            duration=self.duration,
            frame_count=self._frame_count,
            frame_size=self._frame_size,
            ffmpeg_threads=ffmpeg_threads,
            ffmpeg_path=ffmpeg_path,
        )

        self._collage = make_collage(
            image_list=frames,
            frame_size=self._frame_size,
        )
        for f in frames:
            f.close()

        self.hash, self.hex = _calc_hash(self._collage, self.hashlength)
        self._collage.close()

    def __str__(self) -> str:
        """
        The perceptual hash as a hex string.
        """

        return self.hex

    def __repr__(self) -> str:
        """
        Developer's representation of the VideoHash object.

        :return: Developer's representation of the instance.
        """

        return f"VideoHash(hash={self.hex}, hashlength={self.hashlength}"

    def __len__(self) -> int:
        """
        Bit length of the the perceptual hash value.
        """
        return len(self.hash)


def _calc_hash(img, hashlen: int) -> tuple[np.ndarray, str]:
    """
    Calculate the hash value by calling the phash (perceptual hash) method of ImageHash package. The perceptual hash of the collage is the VideoHash for the original input video.
    """
    ih = imagehash.phash(img, hash_size=isqrt(hashlen))

    hash: np.ndarray = ih.hash.flatten()
    hex: str = f"{ih}"
    return hash, hex


def _check_ffmpeg(ffmpeg_path: Path | str) -> Path | str:
    """
    Check the FFmpeg path and run 'ffmpeg -version' to verify that FFmpeg is found and works.
    """
    if isinstance(ffmpeg_path, Path):
        ffmpeg_path = ffmpeg_path.resolve()

    try:
        succ, outs = runn(
            [[f"{ffmpeg_path}", "-version"]],
            n=1,
            getout=True,
            geterr=True,
            raw=False,
        )
    except (FileNotFoundError, OSError):
        raise FFmpegNotFound(f"FFmpeg not found at '{ffmpeg_path}'")
    else:
        if "ffmpeg version" not in outs[0]:
            raise FFmpegError(
                f"Unexpected response for '{ffmpeg_path} -version':\n{outs[0]}"  # type:ignore
            )
    return ffmpeg_path


def phash(video_path: Path, **kwargs) -> tuple[np.ndarray, float]:
    """
    Convenience function to generate a perceptual hash for a video file and return both the hash (bool array) and video duration as a tuple.

    See `VideoHash` class for other available kwargs.

    :return: `(phash, video_duration)`
    """
    vh = VideoHash(video_path=video_path, **kwargs)
    return vh.hash, vh.duration


def phex(video_path: Path, **kwargs) -> tuple[str, float]:
    """
    Convenience function to generate a perceptual hash for a video file and return both the hash (hex string) and video duration as a tuple.

    See `VideoHash` class for other available kwargs.

    :return: `(phash, video_duration)`
    """
    vh = VideoHash(video_path=video_path, **kwargs)
    return vh.hex, vh.duration
