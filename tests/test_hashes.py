import pytest

from pathlib import Path

from videohash import videohash as vh

phashes: list[tuple[str, str]] = [
    ("rocket", "b052b1537b5a0cf0d8a4da8686872b242fa5f8456d472dcd705f521f862f0fbd"),
    (
        "rocket-fadein1s",
        "b052b1537b5a0cf0d8a4da8686872b242fa5f8456d472dcd705f521f862f0fbd",
    ),
    (
        "rocket-fadeout1s",
        "b052b1537b5a0cf0d8a4da8686872b242fe5f8456d072dcd705f521f862f0fbd",
    ),
    (
        "rocket-start8f",
        "b050b1537b5b0ef0d8a45a8687872b242fe5fc456d0725cf505f501f862f0fbd",
    ),
    (
        "rocket-blackbars",
        "b052b1537b5a0cf0d8a4da8686872b242ee5fc456d472dcd501f521f863f0fbd",
    ),
]


def _hash_from_name(videoname: str) -> str:
    vf = next(Path(f"./tests/gold/{videoname}/").glob("video.*"))
    assert vf.exists()
    ph, dur = vh.phex(vf)
    return ph


def read_samples():
    sf = Path("./tests/gold/samples.txt")
    if sf.exists() and sf.is_file():
        with open(sf, "r") as f:
            return [tuple(l.strip("\n").rsplit(" ", 1)) for l in f.readlines()]
    return []


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("videoname,phash", phashes)
def test_hashes_rocket(videoname, phash):
    assert _hash_from_name(videoname) == phash


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("sample", read_samples())
def test_hashes_sample(sample):
    ph, dur = vh.phex(sample[0])
    assert ph == sample[1]
