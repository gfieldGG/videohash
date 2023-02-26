import pytest

from pathlib import Path

import numpy as np

from videohash import videohash as vh


@pytest.fixture
def videofile():
    vf = Path("./tests/gold/rocket/video.mkv")
    assert vf.exists()
    return vf


@pytest.fixture()
def vhobject(videofile, tmp_path):
    return vh.VideoHash(videofile, tmp_path)


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_videohash(videofile: Path):
    vhobj = vh.VideoHash(videofile)
    assert (
        vhobj.hex == "b052b1537b5a0cf0d8a4da8686872b242fa5f8456d472dcd705f521f862f0fbd"
    )
    assert vhobj.duration == 52.079


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_phash(videofile: Path):
    ph, dur = vh.phash(videofile)
    # fmt:off
    assert np.array_equal(ph, np.array([True,False,True,True,False,False,False,False,False,True,False,True,False,False,True,False,True,False,True,True,False,False,False,True,False,True,False,True,False,False,True,True,False,True,True,True,True,False,True,True,False,True,False,True,True,False,True,False,False,False,False,False,True,True,False,False,True,True,True,True,False,False,False,False,True,True,False,True,True,False,False,False,True,False,True,False,False,True,False,False,True,True,False,True,True,False,True,False,True,False,False,False,False,True,True,False,True,False,False,False,False,True,True,False,True,False,False,False,False,True,True,True,False,False,True,False,True,False,True,True,False,False,True,False,False,True,False,False,False,False,True,False,True,True,True,True,True,False,True,False,False,True,False,True,True,True,True,True,True,False,False,False,False,True,False,False,False,True,False,True,False,True,True,False,True,True,False,True,False,True,False,False,False,True,True,True,False,False,True,False,True,True,False,True,True,True,False,False,True,True,False,True,False,True,True,True,False,False,False,False,False,True,False,True,True,True,True,True,False,True,False,True,False,False,True,False,False,False,False,True,True,True,True,True,True,False,False,False,False,True,True,False,False,False,True,False,True,True,True,True,False,False,False,False,True,True,True,True,True,False,True,True,True,True,False,True]))

    assert dur == 52.079
    # fmt:on


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_phex(videofile: Path):
    ph, dur = vh.phex(videofile)
    assert ph == "b052b1537b5a0cf0d8a4da8686872b242fa5f8456d472dcd705f521f862f0fbd"
    assert dur == 52.079


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_ffmpeg_threads(videofile):
    ph1, dur1 = vh.phex(video_path=videofile, ffmpeg_threads=1)
    ph1, dur1 = vh.phex(video_path=videofile, ffmpeg_threads=4)
    ph2, dur2 = vh.phex(video_path=videofile, ffmpeg_threads=8)
    ph3, dur3 = vh.phex(video_path=videofile, ffmpeg_threads=16)
    assert ph1 == ph2 == ph3
    assert dur1 == dur2 == dur3


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("hash_length", [0, 1, 2, 128])
def test_videohash_hash_length_invalid(tmp_path, hash_length):
    # exception is raised before video file is accessed
    videofile = tmp_path / "abc"
    assert not videofile.exists()

    with pytest.raises(ValueError) as e_info:
        vh.VideoHash(videofile, hash_length=hash_length)


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("hash_length", [4, 36, 64, 144, 256])
def test_videohash_hash_length(videofile, hash_length):
    ph, dur = vh.phash(videofile, hash_length=hash_length)
    assert len(ph) == hash_length


def test_videohash_videopathtype():
    vh.VideoHash("./tests/gold/rocket/video.mkv")
    vh.VideoHash(Path("./tests/gold/rocket/video.mkv"))
