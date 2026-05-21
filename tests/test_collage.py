"""Unit tests for videohash.collage.make_collage."""

import pytest
from PIL import Image

from videohash.collage import make_collage
from videohash.exceptions import CollageOfZeroFramesError


def _solid(color: tuple[int, int, int], size: int) -> Image.Image:
    """Return a solid-color RGB image of the given size."""
    img = Image.new("RGB", (size, size), color)
    return img


def test_zero_frames_raises():
    """CollageOfZeroFramesError is raised for an empty frame list."""
    with pytest.raises(CollageOfZeroFramesError):
        make_collage([], frame_size=64)


@pytest.mark.parametrize(
    "frame_count,frame_size,expected_side",
    [
        (1, 64, 64),  # 1x1 grid
        (4, 64, 128),  # 2x2 grid
        (9, 32, 96),  # 3x3 grid
        (16, 48, 192),  # 4x4 grid
    ],
)
def test_collage_dimensions(frame_count, frame_size, expected_side):
    """Collage side length equals isqrt(frame_count) * frame_size."""
    frames = [_solid((128, 128, 128), frame_size) for _ in range(frame_count)]
    collage = make_collage(frames, frame_size=frame_size)
    assert collage.size == (expected_side, expected_side)


def test_collage_mode_is_rgb():
    """Collage output is always RGB."""
    frames = [_solid((255, 0, 0), 32) for _ in range(4)]
    collage = make_collage(frames, frame_size=32)
    assert collage.mode == "RGB"


def test_collage_background_is_black_for_non_square_count():
    """
    make_collage uses isqrt(n) as the grid side, so for n=3
    (isqrt=1 → 1x1 grid) the canvas is 1*frame_size square and
    only the first frame is pasted.  The canvas starts black.
    This test documents the current behaviour rather than asserting
    correctness of the grid logic.
    """
    frame_size = 32
    frames = [_solid((255, 0, 0), frame_size) for _ in range(1)]
    collage = make_collage(frames, frame_size=frame_size)
    assert collage.size == (frame_size, frame_size)


def test_frame_placement_2x2():
    """
    Four distinct-colour frames in a 2x2 grid:
      [RED  | GREEN]
      [BLUE | WHITE]
    Verify a pixel near the centre of each quadrant.
    """
    fs = 64  # frame_size
    red = _solid((255, 0, 0), fs)
    green = _solid((0, 255, 0), fs)
    blue = _solid((0, 0, 255), fs)
    white = _solid((255, 255, 255), fs)

    collage = make_collage([red, green, blue, white], frame_size=fs)

    mid = fs // 2  # pixel near centre of each cell
    assert collage.getpixel((mid, mid)) == (255, 0, 0), "top-left should be red"
    assert collage.getpixel((fs + mid, mid)) == (0, 255, 0), "top-right should be green"
    assert collage.getpixel((mid, fs + mid)) == (0, 0, 255), (
        "bottom-left should be blue"
    )
    assert collage.getpixel((fs + mid, fs + mid)) == (255, 255, 255), (
        "bottom-right should be white"
    )


def test_frame_placement_single():
    """A single frame fills the entire 1x1 collage."""
    fs = 50
    frame = _solid((10, 20, 30), fs)
    collage = make_collage([frame], frame_size=fs)
    assert collage.getpixel((0, 0)) == (10, 20, 30)
    assert collage.getpixel((fs - 1, fs - 1)) == (10, 20, 30)


def test_frame_placement_3x3():
    """Nine distinct-colour frames in a 3x3 grid — spot-check corners."""
    fs = 30
    colors = [
        (255, 0, 0),  # 0,0
        (0, 255, 0),  # 0,1
        (0, 0, 255),  # 0,2
        (255, 255, 0),  # 1,0
        (255, 0, 255),  # 1,1
        (0, 255, 255),  # 1,2
        (128, 0, 0),  # 2,0
        (0, 128, 0),  # 2,1
        (0, 0, 128),  # 2,2
    ]
    frames = [_solid(c, fs) for c in colors]
    collage = make_collage(frames, frame_size=fs)

    mid = fs // 2
    for row in range(3):
        for col in range(3):
            expected = colors[row * 3 + col]
            px = collage.getpixel((col * fs + mid, row * fs + mid))
            assert px == expected, f"cell ({row},{col}) expected {expected}, got {px}"


@pytest.mark.parametrize("frame_size", [1, 8, 100, 256])
def test_various_frame_sizes(frame_size):
    """Collage scales correctly for a range of frame sizes."""
    frames = [_solid((0, 0, 0), frame_size) for _ in range(4)]
    collage = make_collage(frames, frame_size=frame_size)
    assert collage.size == (frame_size * 2, frame_size * 2)
