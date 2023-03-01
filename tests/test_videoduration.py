import pytest

from pathlib import Path

from videohash.videoduration import video_duration
from videohash import FFmpegVideoDurationReadError


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
