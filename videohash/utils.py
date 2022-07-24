import os
import tempfile
from pathlib import Path
from typing import List
import subprocess


def get_list_of_all_files_in_dir(directory: str) -> List[str]:
    """
    Returns a list containing all the file paths(absolute path) in a directory.
    The list is sorted.

    :return: List of absolute path of all files in a directory.

    :rtype: List[str]
    """
    return sorted([(directory + filename) for filename in os.listdir(directory)])


def does_path_exists(path: str) -> bool:
    """
    If a directory is supplied then check if it exists.
    If a file is supplied then check if it exists.

    Directory ends with "/" on posix or "\" in windows and files do not.

    If directory/file exists returns True else returns False

    :return: True if dir or file exists else False.

    :rtype: bool
    """
    if path.endswith("/") or path.endswith("\\"):
        # it's directory
        return os.path.isdir(path)

    else:
        # it's file
        return os.path.isfile(path)


def create_and_return_temporary_directory() -> str:
    """
    create a temporary directory where we can store the video, frames and the
    collage.

    :return: Absolute path of the empty directory.

    :rtype: str
    """
    path = os.path.join(tempfile.mkdtemp(), ("temp_storage_dir" + os.path.sep))
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def runn(commands: list[list[str]] | list[str], n: int = 4) -> int:
    """
    Run list of commands in batches of `n`.

    https://stackoverflow.com/a/71743719/9356410

    :param commands: List of commands to run as either arglists or strings.
    :param n: Number of commands to run in parallel per batch, defaults to 4. Has to be a multiple of `len(commands)`. TODO
    :return int: Count of non-zero returncodes.
    """
    totalerrs = 0
    for j in range(max(int(len(commands) / n), 1)):
        procs = [
            subprocess.Popen(i, shell=False)
            for i in commands[j * n : min((j + 1) * n, len(commands))]
        ]
        for p in procs:
            if p.wait():
                totalerrs += 1

    return totalerrs
