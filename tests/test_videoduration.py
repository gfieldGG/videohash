import pytest

from pathlib import Path

from videohash.videoduration import video_duration


@pytest.mark.gold
@pytest.mark.integration
def test_video_duration():
    assert video_duration(Path("./tests/gold/rocket/video.mkv"), "ffmpeg") == 52.08
    assert (
        video_duration(Path("./tests/gold/rocket-fadeout1s/video.mp4"), "ffmpeg")
        == 52.1
    )
    assert (
        video_duration(Path("./tests/gold/rocket-start8f/video.mp4"), "ffmpeg") == 52.29
    )
