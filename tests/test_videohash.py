import pytest

from pathlib import Path

import numpy as np

from videohash import phex, phash, VideoHash, VideoHashNoDuration


@pytest.fixture
def videofile():
    vf = Path("./tests/gold/rocket/video.mkv")
    assert vf.exists()
    return vf


@pytest.fixture()
def vhobject(videofile, tmp_path):
    return VideoHash(videofile, tmp_path)


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_videohash(videofile: Path):
    vhobj = VideoHash(videofile)
    assert (
        vhobj.hex == "b052b1537b5a0cf0d8a4da8686872b242fa5fc456d472dcd705f501f862f0fbd"
    )
    assert vhobj.duration == 52.08


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_phash(videofile: Path):
    ph, dur = phash(videofile)
    # fmt:off
    assert np.array_equal(ph, np.array([True,False,True,True,False,False,False,False,False,True,False,True,False,False,True,False,True,False,True,True,False,False,False,True,False,True,False,True,False,False,True,True,False,True,True,True,True,False,True,True,False,True,False,True,True,False,True,False,False,False,False,False,True,True,False,False,True,True,True,True,False,False,False,False,True,True,False,True,True,False,False,False,True,False,True,False,False,True,False,False,True,True,False,True,True,False,True,False,True,False,False,False,False,True,True,False,True,False,False,False,False,True,True,False,True,False,False,False,False,True,True,True,False,False,True,False,True,False,True,True,False,False,True,False,False,True,False,False,False,False,True,False,True,True,True,True,True,False,True,False,False,True,False,True,True,True,True,True,True,True,False,False,False,True,False,False,False,True,False,True,False,True,True,False,True,True,False,True,False,True,False,False,False,True,True,True,False,False,True,False,True,True,False,True,True,True,False,False,True,True,False,True,False,True,True,True,False,False,False,False,False,True,False,True,True,True,True,True,False,True,False,True,False,False,False,False,False,False,False,True,True,True,True,True,True,False,False,False,False,True,True,False,False,False,True,False,True,True,True,True,False,False,False,False,True,True,True,True,True,False,True,True,True,True,False,True]))

    assert dur == 52.08
    # fmt:on


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_phex(videofile: Path):
    ph, dur = phex(videofile)
    assert ph == "b052b1537b5a0cf0d8a4da8686872b242fa5fc456d472dcd705f501f862f0fbd"
    assert dur == 52.08


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("ffmpeg_threads", [1, 4, 8, 16])
def test_videohash_ffmpeg_threads(videofile, ffmpeg_threads):
    ph, dur = phex(video_path=videofile, ffmpeg_threads=ffmpeg_threads)
    assert ph == "b052b1537b5a0cf0d8a4da8686872b242fa5fc456d472dcd705f501f862f0fbd"
    assert dur == 52.08


@pytest.mark.parametrize("hash_length", [0, 1, 2, 128])
def test_videohash_hash_length_invalid(tmp_path, hash_length):
    # exception is raised before video file is accessed
    videofile = tmp_path / "abc"
    assert not videofile.exists()

    with pytest.raises(ValueError):
        VideoHash(videofile, hash_length=hash_length)


@pytest.mark.parametrize("frame_count", [0, 2, 3, 5, 8, 15])
def test_videohash_frame_count_invalid(tmp_path, frame_count):
    # exception is raised before video file is accessed
    videofile = tmp_path / "abc"
    assert not videofile.exists()

    with pytest.raises(ValueError):
        VideoHash(videofile, frame_count=frame_count)


@pytest.mark.gold
@pytest.mark.integration
@pytest.mark.parametrize("hash_length", [4, 36, 64, 144, 256])
def test_videohash_hash_length(videofile, hash_length):
    vh = VideoHash(videofile, hash_length=hash_length)

    assert len(vh.hash) == hash_length
    assert len(vh) == hash_length
    assert vh._hash_length == hash_length
    assert len(vh.hex) == hash_length // 4


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_videopathtype():
    VideoHash("./tests/gold/rocket/video.mkv")
    VideoHash(Path("./tests/gold/rocket/video.mkv"))


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_noduration():
    with pytest.raises(VideoHashNoDuration):
        VideoHash(Path("./tests/gold/rocket-noduration/video.mp4"))
