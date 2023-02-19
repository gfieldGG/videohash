import pytest

from pathlib import Path

from videohash import videohash as vh

phashes: list[tuple[str, str]] = [
    ("rocket", "0b1011000010110001011110110000110011011000110110101000011100101011"),
    (
        "rocket-fadein1s",
        "0b1011000010110001011110110000110011011000110110101000011100101011",
    ),
    (
        "rocket-fadeout1s",
        "0b1011000010110001011110110000110011011000110110101000011100101011",
    ),
    (
        "rocket-start8f",
        "0b1011000010110001011110110000111011011000010110101000011100101011",
    ),
    (
        "rocket-blackbars",
        "0b1011000010110001011110110000110011011000110110101000011100101011",
    ),
]


def _hash_from_name(videoname: str) -> str:
    vf = next(Path(f"./tests/gold/{videoname}/").glob("video.*"))
    assert vf.exists()
    ph, dur = vh.phash(vf)
    return ph


def read_samples():
    sf = Path("./tests/gold/samples.txt")
    if sf.exists() and sf.is_file():
        with open(sf, "r") as f:
            return [tuple(l.strip("\n").rsplit(" ", 1)) for l in f.readlines()]


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("videoname,phash", phashes)
def test_hashes_rocket(videoname, phash):
    assert _hash_from_name(videoname) == phash


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("sample", read_samples())
def test_hashes_sample(sample):
    ph, dur = vh.phash(sample[0])
    assert ph == sample[1]
