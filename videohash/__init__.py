# ██╗░░░██╗██╗██████╗░███████╗░█████╗░██╗░░██╗░█████╗░░██████╗██╗░░██╗
# ██║░░░██║██║██╔══██╗██╔════╝██╔══██╗██║░░██║██╔══██╗██╔════╝██║░░██║
# ╚██╗░██╔╝██║██║░░██║█████╗░░██║░░██║███████║███████║╚█████╗░███████║
# ░╚████╔╝░██║██║░░██║██╔══╝░░██║░░██║██╔══██║██╔══██║░╚═══██╗██╔══██║
# ░░╚██╔╝░░██║██████╔╝███████╗╚█████╔╝██║░░██║██║░░██║██████╔╝██║░░██║
# ░░░╚═╝░░░╚═╝╚═════╝░╚══════╝░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝


"""
The Python package for near duplicate video detection

https://github.com/gfieldGG/videohash


:copyright: (c) 2021 Akash Mahanty
:license: MIT, see LICENSE for more details.
"""

from .exceptions import (
    CollageOfZeroFramesError,
    FFmpegError,
    FFmpegFailedToExtractFrames,
    FFmpegNotFound,
    VideoHashError,
    VideoHashNoDuration,
    FFmpegVideoDurationReadError,
)
from .videohash import VideoHash, phash, phex
