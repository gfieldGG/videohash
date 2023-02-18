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
def test_videohash_all(tmp_path: Path, videofile: Path):
    videohash = vh.VideoHash(videofile, tmp_path)

    # paths and files
    assert videohash.video_path == videofile.resolve()
    assert videohash.storage_path.parent == tmp_path
    assert videohash.storage_path.exists()
    assert videohash.frames_dir == Path(videohash.storage_path / "frames")
    assert videohash.frames_dir.exists()
    assert videohash.collage_dir == Path(videohash.storage_path / "collage")
    assert videohash.collage_dir.exists()
    assert videohash.collage_path == Path(videohash.collage_dir / "collage.jpg")

    # defaults
    assert videohash.frame_count == 16
    assert videohash.frame_size == 240
    assert videohash.ffmpeg_threads == 16
    assert videohash.ffmpeg_path == "ffmpeg"
    assert videohash.hashlength == 64

    # extracted frames
    assert len(list(videohash.frames_dir.glob("*"))) == videohash.frame_count

    # collage properties
    expectedsize = round(sqrt(videohash.frame_count)) * videohash.frame_size
    assert videohash.image.size == (expectedsize, expectedsize)

    # calculated results
    assert (
        videohash.hash
        == "0b1011000010110001011110110000110011011000110110101000011100101011"
    )
    assert videohash.duration == 52.079

    # cleanup
    videohash.delete_storage_path()
    assert tmp_path.exists()
    assert not next(tmp_path.iterdir(), None)


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_phash(videofile: Path):
    ph, dur = vh.phash(videofile)
    assert ph == "0b1011000010110001011110110000110011011000110110101000011100101011"
    assert dur == 52.079


@pytest.mark.gold
@pytest.mark.integration
def test_videohash_phash_cleanup(videofile: Path, tmp_path):
    ph, dur = vh.phash(videofile, storage_path=tmp_path)
    assert not next(tmp_path.iterdir(), None)
