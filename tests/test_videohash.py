import pytest

from math import sqrt
from pathlib import Path

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
def test_videohash_phash(videofile: Path):
    ph, dur = vh.phash(videofile)
    assert ph == "0b1011000010110001011110110000110011011000110110101000011100101011"
    assert dur == 52.079


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_ffmpeg_threads(videofile):
    ph1, dur1 = vh.phash(video_path=videofile, ffmpeg_threads=1)
    ph1, dur1 = vh.phash(video_path=videofile, ffmpeg_threads=4)
    ph2, dur2 = vh.phash(video_path=videofile, ffmpeg_threads=8)
    ph3, dur3 = vh.phash(video_path=videofile, ffmpeg_threads=16)
    assert ph1 == ph2 == ph3
    assert dur1 == dur2 == dur3


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("hash_length", [1, 2, 128])
def test_videohash_hash_length_invalid(tmp_path, hash_length):
    # exception is raised before video file is accessed
    videofile = tmp_path / "abc"
    assert not videofile.exists()

    with pytest.raises(ValueError) as e_info:
        vh.VideoHash(videofile, hash_length=hash_length, storage_path=tmp_path)


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("hash_length", [4, 36, 64, 144, 256])
def test_videohash_hash_length(videofile, hash_length):
    ph, dur = vh.phash(videofile, hash_length=hash_length)
    assert len(ph) == hash_length + 2


def test_videohash_videopathtype():
    vh.VideoHash("./tests/gold/rocket/video.mkv")
    vh.VideoHash(Path("./tests/gold/rocket/video.mkv"))
