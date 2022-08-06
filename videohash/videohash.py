import os
import random
import re
import shutil
from pathlib import Path
from math import ceil, sqrt
from typing import List, Optional, Union

import imagehash
import numpy as np
from imagedominantcolor import DominantColor
from PIL import Image

from .collagemaker import MakeCollage
from .exceptions import DidNotSupplyPathOrUrl, StoragePathDoesNotExist
from .framesextractor import FramesExtractor
from .tilemaker import make_tile
from .utils import (
    create_and_return_temporary_directory,
    does_path_exists,
    get_list_of_all_files_in_dir,
)
from .videoduration import video_duration


class VideoHash:

    """
    VideoHash class provides an interface for computing & comparing the video
    hash values for videos(codec, containers etc) supported by FFmpeg.
    """

    def __init__(
        self,
        path: str,
        storage_path: Optional[str] = None,
        frame_count: int = 16,
        frame_size: int = 240,
        ffmpeg_threads: int = 16,
        fixed: bool = None,
    ) -> None:
        """
        :param path: Absolute path of the input video file.

        :param storage_path: Storage path for the files created by
                             the instance, pass the absolute path of the
                             directory.
                             If no argument is passed then the instance will
                             itself create the storage directory inside the
                             temporary directory of the system.

        :param frame_interval: Number of frames extracted per unit time, the
                               default value is 1 per unit time. For 1 frame
                               per 5 seconds pass 1/5 or 0.2. For 5 fps pass 5.
                               Smaller frame_interval implies fewer frames and
                               vice-versa.


        :return: None

        :rtype: NoneType
        """
        self.path = path

        self.storage_path = ""
        if storage_path:
            self.storage_path = storage_path

        self._storage_path = self.storage_path
        self.ffmpeg_threads = ffmpeg_threads
        self.video_duration = video_duration(self.path)

        self.frame_count = frame_count

        if fixed is None:
            self.fixed = self.video_duration >= 36  # TODO consider bitrate/fps
        else:
            self.fixed = fixed

        self.frame_size = frame_size

        self.task_uid = VideoHash._get_task_uid()

        self._create_required_dirs_and_check_for_errors()

        FramesExtractor(
            self.path,
            self.frames_dir,
            duration=self.video_duration,
            ffmpeg_threads=self.ffmpeg_threads,
            frame_count=self.frame_count,
            frame_size=frame_size,
            fixed=self.fixed,
        )

        self.collage_path = os.path.join(self.collage_dir, "collage.jpg")

        MakeCollage(
            get_list_of_all_files_in_dir(self.frames_dir),
            self.collage_path,
            collage_image_width=round(sqrt(self.frame_count)) * self.frame_size,
            frame_size=self.frame_size,
            fixed=self.fixed,
        )

        self.image = Image.open(self.collage_path)
        self.hashlength = 64

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

    def _create_required_dirs_and_check_for_errors(self) -> None:
        """
        Creates important directories before the main processing starts.

        The instance files are stored in these directories, no need to worry
        about the end user or some other processes interfering with the instance
        generated files.


        :raises StoragePathDoesNotExist: If the storage path specified by the user does not exist.

        :return: None

        :rtype: NoneType
        """
        if not self.storage_path:
            self.storage_path = create_and_return_temporary_directory()
        if not does_path_exists(self.storage_path):
            raise StoragePathDoesNotExist(
                f"Storage path '{self.storage_path}' does not exist."
            )

        os_path_sep = os.path.sep

        self.storage_path = os.path.join(
            self.storage_path, (f"{self.task_uid}{os_path_sep}")
        )

        self.frames_dir = os.path.join(self.storage_path, (f"frames{os_path_sep}"))
        Path(self.frames_dir).mkdir(parents=True, exist_ok=True)

        self.collage_dir = os.path.join(self.storage_path, (f"collage{os_path_sep}"))
        Path(self.collage_dir).mkdir(parents=True, exist_ok=True)

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
        directory = self.storage_path

        if not self._storage_path:
            directory = (
                os.path.dirname(os.path.dirname(os.path.dirname(self.storage_path)))
                + os.path.sep
            )

        shutil.rmtree(directory, ignore_errors=True, onerror=None)

    @staticmethod
    def _get_task_uid() -> str:
        """
        Returns an unique task id for the instance. Task id is used to
        differentiate the instance files from the other unrelated files.

        We want to make sure that only the instance is manipulating the instance files
        and no other process nor user by accident deletes or edits instance files while
        we are still processing.

        :return: instance's unique task id.

        :rtype: str
        """
        sys_random = random.SystemRandom()

        return "".join(
            sys_random.choice(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            )
            for _ in range(20)
        )

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
        bitlist: list[int] = (
            imagehash.phash(self.image).hash.flatten().astype(int).tolist()
        )
        self.hash: str = "".join([str(i) for i in bitlist])
