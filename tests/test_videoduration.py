import pytest

from pathlib import Path

from videohash.videoduration import video_duration


@pytest.fixture
def videofile():
    vf = Path("./tests/gold/rocket/video.mkv")
    assert vf.exists()
    return vf


@pytest.mark.gold
@pytest.mark.integration
def test_video_duration(videofile):
    assert (video_duration(videofile, "ffmpeg") - 52.08) < 0.001
