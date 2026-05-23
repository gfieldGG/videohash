import pytest

import uuid
from pathlib import Path

from videohash.videoduration import video_duration
from videohash import FFmpegNotFound, FFmpegVideoDurationReadError


@pytest.mark.gold
def test_video_duration():
    assert video_duration(Path("./tests/gold/rocket/video.mkv"), "ffmpeg") == 52.08
    assert (
        video_duration(Path("./tests/gold/rocket-fadeout1s/video.mp4"), "ffmpeg")
        == 52.1
    )
    assert (
        video_duration(Path("./tests/gold/rocket-start8f/video.mp4"), "ffmpeg") == 52.29
    )


@pytest.mark.gold
def test_video_duration_error():
    with pytest.raises(FFmpegVideoDurationReadError):
        video_duration(Path("./tests/gold/rocket-noduration/video.mp4"), "ffmpeg")


def test_video_duration_ffmpeg_not_found():
    rand = f"{uuid.uuid4()}"
    assert not Path(rand).exists()

    with pytest.raises(FFmpegNotFound):
        video_duration(Path("./tests/gold/rocket/video.mkv"), ffmpeg_path=rand)


def test_video_duration_ffmpeg_not_executable():
    with pytest.raises(FFmpegNotFound):
        video_duration(
            Path("./tests/gold/rocket/video.mkv"),
            ffmpeg_path="./tests/gold/rocket/video.mkv",
        )


def test_video_duration_wrong_executable():
    with pytest.raises(FFmpegVideoDurationReadError):
        video_duration(Path("./tests/gold/rocket/video.mkv"), ffmpeg_path="python")
