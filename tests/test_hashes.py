import pytest

from pathlib import Path

from videohash import videohash as vh

phashes: list[tuple[str, str]] = [
    ("rocket", "0b1010110010101100010001111111010010001101000010011001011100110011"),
    (
        "rocket-fadein1s",
        "0b1010110010001111010001111101010010101000000010011111001100110011",
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
