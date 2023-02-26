from pathlib import Path
from subprocess import check_output
from math import isqrt

import imagehash

from .exceptions import (
    FFmpegError,
    FFmpegNotFound,
    FFprobeError,
    VideoHashNoDuration,
)
from .extract import extract_frames
from .collage import make_collage
from .videoduration import video_duration


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

        try:
            self.duration = video_duration(self.video_path)
        except FFprobeError as e:
            raise VideoHashNoDuration(
                f"Failed to get video duration using ffprobe. Cannot generate phash without duration."
            ) from e

        if isinstance(ffmpeg_path, Path):
            self.ffmpeg_path = ffmpeg_path.resolve().as_posix()
        else:
            self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()

        self.ffmpeg_threads = ffmpeg_threads

        self.frame_count = frame_count
        self.frame_size = frame_size

        frames = extract_frames(
            self.video_path,
            duration=self.duration,
            frame_count=self.frame_count,
            frame_size=self.frame_size,
            ffmpeg_threads=self.ffmpeg_threads,
            ffmpeg_path=self.ffmpeg_path,
        )

        self._collage = make_collage(
            image_list=frames,
            frame_size=self.frame_size,
        )

        self._calc_hash()
        self._collage.close()

    def __str__(self) -> str:
        """
        The perceptual hash as a bitstring prefixed with '0b'.
        """

        return self.hash

    def __repr__(self) -> str:
        """
        Developer's representation of the VideoHash object.

        :return: Developer's representation of the instance.
        """

        return f"VideoHash(hash={self.hash}, hashlength={self.hashlength}"

    def __len__(self) -> int:
        """
        Length of the the perceptual hash value, including the prefix '0b'.
        """
        return len(self.hash)

    def _check_ffmpeg(self) -> None:
        """
        Check the FFmpeg path and runs 'ffmpeg -version' to verify that FFmpeg is found and works.
        """
        try:
            # check_output will raise FileNotFoundError if it does not find ffmpeg
            output = check_output([self.ffmpeg_path, "-version"]).decode()
        except FileNotFoundError:
            raise FFmpegNotFound(f"FFmpeg not found at '{self.ffmpeg_path}'")

        else:
            if "ffmpeg version" not in output:
                raise FFmpegError(
                    f"Unexpected response for '{self.ffmpeg_path} -version':\n{output}"
                )

    def _calc_hash(self) -> None:
        """
        Calculate the hash value by calling the phash (perceptual hash) method of ImageHash package. The perceptual hash of the collage is the VideoHash for the original input video.
        """
        bitlist = imagehash.phash(
            self._collage, hash_size=isqrt(self.hashlength)
        ).hash.flatten()

        self.hash: str = "0b" + "".join([f"{i}" for i in bitlist.astype(int)])


def phash(video_path: Path, **kwargs) -> tuple[str, float]:
    """
    Convenience function to generate a perceptual hash for a video file and return both the hash and video duration as a tuple.

    See `VideoHash` class for other available kwargs.

    :return: `(phash, video_duration)`
    """
    vh = VideoHash(video_path=video_path, **kwargs)
    return vh.hash, vh.duration
