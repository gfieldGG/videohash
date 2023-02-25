import pytest

from pathlib import Path

from videohash.extract import _detect_crop


@pytest.mark.gold
def test_crop_bb_hor():
    crop = _detect_crop(
        Path("./tests/gold/rocket-blackbars/video.mp4"),
        duration=52.079,
        ffmpeg_path="ffmpeg",
    )
    assert crop == ["-vf", "crop=480:256:0:112"]
