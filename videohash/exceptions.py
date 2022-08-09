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


class StoragePathDoesNotExist(VideoHashError):
    """
    The storage base path passed by the user does not exist.
    """

    pass


class FramesExtractorOutPutDirDoesNotExist(VideoHashError):
    """The frames output directory passed to the frame extractor does not exist."""

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


class FFprobeError(VideoHashError):
    """Base error for ffprobe exceptions."""

    pass


class FFprobeVideoDurationReadError(FFprobeError):
    """FFprobe failed to get duration from video file."""

    pass


class FFprobeNoVideoDurationSpecified(FFprobeError):
    """First video stream does not have a specified duration."""

    pass
