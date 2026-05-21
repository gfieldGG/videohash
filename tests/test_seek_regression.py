import pytest
from pathlib import Path
from PIL import Image
import numpy as np

from videohash import VideoHash
from videohash.videoduration import video_duration
from videohash.extract import extract_frames


GOLD_DIR = Path("./tests/gold/seek-regression")
VIDEO_PATH = GOLD_DIR / "video.mov"
# To regenerate video.mov (first keyframe at ~0.066s — the condition that breaks single input-seek):
#   ffmpeg -f lavfi -i testsrc=duration=35:size=320x240:rate=30 \
#     -pix_fmt yuv420p -c:v libx265 -g 60 \
#     -x265-params "keyint=60:min-keyint=60:scenecut=0" -an source.mp4
#   ffmpeg -ss 0.5 -t 32.3 -i source.mp4 -c copy \
#     -avoid_negative_ts make_zero -movflags +faststart video.mov
# Then update EXPECTED_DURATION, EXPECTED_VIDEO_HASH, and re-commit frame_00.png…frame_15.png.

# Pre-computed values from the reference synthetic video
EXPECTED_DURATION = 32.87
EXPECTED_VIDEO_HASH = "8a6dc8b19ee4a24f4ab0e01a354e8ae08a624f355fa475ecf7cf0ab1e05fb44e"


@pytest.fixture(scope="module")
def regression_video():
    if not VIDEO_PATH.exists():
        pytest.skip("Seek-regression gold video not found")
    return VIDEO_PATH


@pytest.mark.gold
@pytest.mark.integration
def test_regression_duration(regression_video):
    """Duration parsing must match the container value FFmpeg reports."""
    dur = video_duration(regression_video, "ffmpeg")
    assert dur == EXPECTED_DURATION


@pytest.mark.gold
@pytest.mark.integration
def test_regression_video_hash(regression_video):
    """Full VideoHash must remain stable for the synthetic reference.

    This test guards against reverting from the dual-seek (hybrid) approach
    back to a single input seek.  The synthetic HEVC video was engineered so
    that single-seek lands on a different frame for at least one timestamp,
    which changes the final pHash.
    """
    vh = VideoHash(regression_video)
    assert vh.hex == EXPECTED_VIDEO_HASH
    assert vh.duration == EXPECTED_DURATION


@pytest.mark.gold
@pytest.mark.integration
def test_regression_frame_pixels(regression_video):
    """Each extracted frame must match the committed reference pixel-for-pixel.

    This is a stronger guarantee than the pHash test: it fails the moment
    *any* frame differs, making it obvious that the seek method changed.
    """
    frames = extract_frames(
        video_path=regression_video,
        duration=EXPECTED_DURATION,
        frame_count=16,
        frame_size=240,
        ffmpeg_threads=4,
        ffmpeg_path="ffmpeg",
        maxerrors=0,
    )

    assert len(frames) == 16

    for i, frame in enumerate(frames):
        ref_path = GOLD_DIR / f"frame_{i:02d}.png"
        if not ref_path.exists():
            pytest.skip(f"Reference frame {ref_path.name} not found")

        ref = Image.open(ref_path)
        assert frame.size == ref.size
        assert np.array_equal(np.array(frame), np.array(ref))
