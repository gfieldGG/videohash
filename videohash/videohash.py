import shutil
from pathlib import Path
from subprocess import check_output
from math import isqrt

from PIL import Image
import imagehash

from .collagemaker import MakeCollage
from .exceptions import (
    StoragePathDoesNotExist,
    FFmpegError,
    FFmpegNotFound,
    FFprobeError,
    VideoHashNoDuration,
)
from .framesextractor import FramesExtractor
from .utils import get_tempdir, get_files_in_dir
from .videoduration import video_duration


class VideoHash:

    """
    VideoHash class provides an interface for computing a perceptual video hash for videos supported by FFmpeg.
    """

    def __init__(
        self,
        video_path: Path | str,
        storage_path: Path = None,
        hash_length: int = 64,
        frame_count: int = 16,
        frame_size: int = 240,
        ffmpeg_threads: int = 4,
        ffmpeg_path: Path | str = "ffmpeg",
    ) -> None:
        """
        :param video_path: Absolute path of the input video file.

        :param storage_path: Base storage path for the files created by
                             the instance.
                             If no argument is passed then the instance will itself create a directory inside the temporary directory of the system.

        :return: None
        """
        if hash_length < 2 or isqrt(hash_length) ** 2 != hash_length:
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

        self._base_dir = storage_path
        self._check_and_create_working_dirs()

        if isinstance(ffmpeg_path, Path):
            self.ffmpeg_path = ffmpeg_path.resolve().as_posix()
        else:
            self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()

        self.ffmpeg_threads = ffmpeg_threads

        self.frame_count = frame_count
        self.frame_size = frame_size

        FramesExtractor(
            self.video_path,
            self.frames_dir,
            duration=self.duration,
            ffmpeg_path=self.ffmpeg_path,
            ffmpeg_threads=self.ffmpeg_threads,
            frame_count=self.frame_count,
            frame_size=frame_size,
        )

        self.collage_path = Path(self.collage_dir / "collage.jpg")

        MakeCollage(
            image_list=get_files_in_dir(self.frames_dir),
            output_path=self.collage_path,
            frame_size=self.frame_size,
        )

        self.image = Image.open(self.collage_path)

        self._calc_hash()

    def __str__(self) -> str:
        """
        The video hash value of the instance. The hash value is 64 bit string
        prefixed with '0b', indicating the that the hash value is a bitstring.

        :return: The string representation of the instance. The video hash value
                 itself is the returned value.

        :rtype: str
        """

        return self.hash

    def __repr__(self) -> str:
        """
        Developer's representation of the VideoHash object.

        :return: Developer's representation of the instance.

        :rtype: str
        """

        return (
            f"VideoHash(hash={self.hash}, "
            + f"collage_path={self.collage_path}, hashlength={self.hashlength})"
        )

    def __len__(self) -> int:
        """
        Length of the hash value string. Total length is 66 characters, 64 for
        the bitstring and 2 for the prefix '0b'.

        :return: Length of the the hash value, including the prefix '0b'.

        :rtype: int
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

    def _check_and_create_working_dirs(self) -> None:
        """
        Creates important directories before the main processing starts.

        The instance files are stored in these directories, no need to worry
        about the end user or some other processes interfering with the instance
        generated files.


        :raises StoragePathDoesNotExist: If the storage path specified by the user does not exist.

        :return: None

        :rtype: NoneType
        """
        if self._base_dir:
            if not self._base_dir.is_dir():
                raise StoragePathDoesNotExist(
                    f"Storage base path '{self._base_dir}' does not exist."
                )
            self._base_dir = self._base_dir.resolve()
        self.storage_path = get_tempdir(self._base_dir)

        self.frames_dir = self.storage_path / "frames"
        self.frames_dir.mkdir(parents=False, exist_ok=False)

        self.collage_dir = self.storage_path / "collage"
        self.collage_dir.mkdir(parents=False, exist_ok=False)

    def delete_storage_path(self) -> None:
        """
        Delete the storage_path directory tree.

        Remember that deleting the storage directory will also delete the
        collage and the extracted frames. If you passed an
        argument to the storage_path that directory will not be deleted but
        only the files and directories created inside that directory by the
        instance will be deleted, this is a feature(not a bug) to ensure that
        multiple instances of the same program are not deleting the storage
        path while other instances still require that storage directory.

        Many OS delete the temporary directory on boot or they never delete it.
        If you will be calculating videohash-value for many videos and don't
        want to run out of storage don't forget to delete the storage path.

        :return: None

        :rtype: NoneType
        """
        shutil.rmtree(self.storage_path, ignore_errors=True, onerror=None)

    def _calc_hash(self) -> None:
        """
        Calculates the hash value by calling the whash(wavelet hash) method of
        imagehash package. The wavelet hash of the collage is the videohash for
        the original input video.

        End-user is not provided any access to the imagehash instance but
        instead the binary and hexadecimal equivalent of the result of
        wavelet-hash.

        :return: None

        :rtype: NoneType
        """
        bitlist = imagehash.phash(
            self.image, hash_size=isqrt(self.hashlength)
        ).hash.flatten()

        self.hash: str = "0b" + "".join([f"{i}" for i in bitlist.astype(int)])


def phash(video_path: Path, **kwargs) -> tuple[str, float]:
    """
    Convenience function to generate a perceptual hash for a video file.

    Instantiates a `VideoHash` object, passing all `kwargs`, cleans up temp files and returns generated perceptual hash and video duration.

    See `VideoHash` class for other available kwargs.

    :return: `(phash, video_duration)`
    """
    vh = VideoHash(video_path=video_path, **kwargs)
    vh.delete_storage_path()
    return vh.hash, vh.duration
