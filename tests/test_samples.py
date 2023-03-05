import pytest

from pathlib import Path

from videohash import videohash as vh
from videohash.videoduration import video_duration


def read_samples():
    sf = Path("./tests/gold/samples.txt")
    if sf.exists() and sf.is_file():
        with open(sf, "r") as f:
            return [tuple(l.strip("\n").rsplit(" ", 2)) for l in f.readlines()]
    return []


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("sample", read_samples())
def test_samples_hash(sample):
    ph, dur = vh.phex(sample[0])
    assert ph == sample[1]


@pytest.mark.gold
@pytest.mark.parametrize("sample", read_samples())
def test_samples_duration(sample):
    dur = video_duration(sample[0], "ffmpeg")
    assert dur == float(sample[2])
