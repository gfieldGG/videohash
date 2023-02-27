"""
videohash.exceptions
~~~~~~~~~~~~~~~~~~~
This module contains videohash's exceptions.
"""


class VideoHashError(Exception):
    """Base Exception for the videohash package."""

    pass


class VideoHashNoDuration(VideoHashError):
    """No video duration for phash generation."""

    pass


class CollageOfZeroFramesError(VideoHashError):
    """Raised if zero frames are passed for collage making."""

    pass


class FFmpegError(VideoHashError):
    """Base error for FFmpeg exceptions."""

    pass


class FFmpegNotFound(FFmpegError):
    """FFmpeg is either not installed or not in the executable path of the system."""

    pass


class FFmpegFailedToExtractFrames(FFmpegError):
    """FFmpeg failed to extract any frame at all. Maybe the input video is damaged or corrupt."""

    pass


class FFmpegVideoDurationReadError(FFmpegError):
    """FFmpeg failed to get duration from video file."""

    pass
