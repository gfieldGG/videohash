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
]


def _hash_from_name(videoname: str) -> str:
    vf = next(Path(f"./tests/gold/{videoname}/").glob("video.*"))
    assert vf.exists()
    ph, dur = vh.phash(vf)
    return ph


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("videoname,phash", phashes)
def test_hashes_rocket(videoname, phash):
    assert _hash_from_name(videoname) == phash
