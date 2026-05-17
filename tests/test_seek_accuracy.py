import pytest
from pathlib import Path
from PIL import Image
import numpy as np
import imagehash

from videohash import VideoHash
from videohash.videoduration import video_duration
from videohash.extract import extract_frames


GOLD_DIR = Path("./tests/gold/synthetic-seek")
VIDEO_PATH = GOLD_DIR / "video.mp4"

# Pre-computed values from the reference synthetic video
EXPECTED_DURATION = 60.1
EXPECTED_VIDEO_HASH = "826fc860c2ac96fae807ac5137fb8ac9a2e8ff94228d17a957f8e806fd72026b"
EXPECTED_FRAME_HASHES = [
    "93e90717ad16e856",
    "a289a56699769976",
    "892387dc2bdc32dc",
    "a983a57c0b7c927c",
    "8b2987563dc6b0d6",
    "bb89a73749368076",
    "a903a56c1bec927e",
    "8923879d2bdc32dc",
    "ab81a7651d769076",
    "832987c639d6b8d6",
    "b983a73d097c827c",
    "a913a56d1bec12ec",
    "8963879d2f94a2dc",
    "a389a76699769866",
    "8b2987d539d6b0d4",
    "a983a5bd037c927c",
]


@pytest.fixture(scope="module")
def synthetic_video():
    if not VIDEO_PATH.exists():
        pytest.skip("Synthetic seek gold video not found")
    return VIDEO_PATH


@pytest.mark.gold
@pytest.mark.integration
def test_synthetic_duration(synthetic_video):
    """Duration parsing must match the container value FFmpeg reports."""
    dur = video_duration(synthetic_video, "ffmpeg")
    assert dur == EXPECTED_DURATION


@pytest.mark.gold
@pytest.mark.integration
def test_synthetic_video_hash(synthetic_video):
    """Full VideoHash must remain stable for the synthetic reference."""
    vh = VideoHash(synthetic_video)
    assert vh.hex == EXPECTED_VIDEO_HASH
    assert vh.duration == EXPECTED_DURATION


@pytest.mark.gold
@pytest.mark.integration
def test_synthetic_frame_pixels(synthetic_video):
    """Each extracted frame must match the committed reference pixel-for-pixel."""
    frames = extract_frames(
        video_path=synthetic_video,
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


@pytest.mark.gold
@pytest.mark.integration
def test_synthetic_frame_hashes(synthetic_video):
    """Perceptual hashes of individual frames must remain stable."""
    frames = extract_frames(
        video_path=synthetic_video,
        duration=EXPECTED_DURATION,
        frame_count=16,
        frame_size=240,
        ffmpeg_threads=4,
        ffmpeg_path="ffmpeg",
        maxerrors=0,
    )

    assert len(frames) == 16

    for i, frame in enumerate(frames):
        ph = imagehash.phash(frame, hash_size=8)
        assert str(ph) == EXPECTED_FRAME_HASHES[i]
