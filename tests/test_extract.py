import pytest

from pathlib import Path

from videohash.extract import extract_frames
from videohash import FFmpegFailedToExtractFrames


@pytest.mark.gold
def test_extract_singleerror_allow():
    extract_frames(
        video_path=Path("./tests/gold/rocket/video.mkv"),
        duration=57.0,  # too long, to make last frame fail
        frame_count=16,
        frame_size=240,
        maxerrors=1,
        ffmpeg_threads=4,
        ffmpeg_path="ffmpeg",
    )


@pytest.mark.gold
def test_extract_singleerror_error():
    with pytest.raises(FFmpegFailedToExtractFrames):
        extract_frames(
            video_path=Path("./tests/gold/rocket/video.mkv"),
            duration=57.0,  # too long, to make last frame fail
            frame_count=16,
            frame_size=240,
            maxerrors=0,
            ffmpeg_threads=4,
            ffmpeg_path="ffmpeg",
        )


@pytest.mark.gold
def test_extract_twoerror_error():
    with pytest.raises(FFmpegFailedToExtractFrames):
        extract_frames(
            video_path=Path("./tests/gold/rocket/video.mkv"),
            duration=63.0,  # too long, to make last two frames fail
            frame_count=16,
            frame_size=240,
            maxerrors=1,
            ffmpeg_threads=4,
            ffmpeg_path="ffmpeg",
        )
