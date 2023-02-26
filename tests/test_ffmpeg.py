import pytest

import uuid
from pathlib import Path

from videohash import videohash as vh

from videohash import FFmpegError, FFmpegNotFound


def test_ffmpeg_not_found():
    rand = f"{uuid.uuid4()}"
    assert not Path(rand).exists()
    with pytest.raises(FFmpegNotFound) as e:
        vh._check_ffmpeg(ffmpeg_path=rand)


def test_ffmpeg_wrong_exe():
    with pytest.raises(FFmpegError) as e:
        vh._check_ffmpeg(ffmpeg_path="python")


def test_ffmpeg_not_exe():
    with pytest.raises(FFmpegNotFound) as e:
        vh._check_ffmpeg(ffmpeg_path="./tests/gold/rocket/video.mkv")


@pytest.mark.xfail
def test_ffmpeg_on_path_str():
    vh._check_ffmpeg(ffmpeg_path="ffmpeg")


@pytest.mark.xfail
def test_ffmpeg_on_path_path():
    with pytest.raises(FFmpegNotFound) as e:
        vh._check_ffmpeg(ffmpeg_path=Path("ffmpeg"))
