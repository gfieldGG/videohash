# videohash

Near-duplicate video detection via perceptual hashing. Extracts frames from a video, tiles them into a collage, and computes a pHash — producing a 256-bit value you can compare across videos to measure similarity.

> [!WARNING]
> Hashes are only comparable within the same major version (e.g. `9.x.x`). Cross-version comparisons may produce incorrect results.

Forked from [akamhy/videohash](https://github.com/akamhy/videohash).
Key improvements:

- **Input-side seeking** — FFmpeg seeks directly to each timestamp without full decode, dramatically faster on large files and slow/network drives
- **Fixed frame count at predictable timestamps** — upstream extracts one frame per second (variable count); this fork samples a fixed number of evenly-spaced frames regardless of duration, making hashes stable across speed-altered versions of the same video
- **Configurable hash length** — any perfect square bit length, default 256-bit

---

## Requirements

- Python 3.11–3.15
- [FFmpeg](https://ffmpeg.org) (on `PATH`, or specify via `ffmpeg_path`)

---

## Installation

```bash
pip install git+https://github.com/gfieldGG/videohash.git@v9
```

Or with Poetry:

```bash
poetry add git+https://github.com/gfieldGG/videohash.git@v9
```

The `@v9` floating tag always points to the latest `9.x.x` release.

---

## Usage

### Basic

```python
from videohash import phex

hex_hash, duration = phex("path/to/video.mkv")
print(hex_hash)   # e.g. "b052b1537b5a0cf0..."
print(duration)   # seconds, e.g. 52.08
```

### Class interface

```python
from videohash import VideoHash

vh = VideoHash("path/to/video.mkv")
print(vh.hex)       # hex string (64 chars at default hash_length=256)
print(vh.hash)      # numpy bool array of length 256
print(vh.duration)  # float, seconds
```

### Custom parameters

```python
vh = VideoHash(
    "path/to/video.mkv",
    hash_length=64,     # must be a perfect square >= 4
    frame_count=9,      # must be a perfect square
    ffmpeg_threads=8,
    ffmpeg_path="/usr/local/bin/ffmpeg",
)
```

### Comparing videos

```python
import numpy as np
from videohash import phash

hash_a, _ = phash("video_a.mp4")
hash_b, _ = phash("video_b.mp4")

distance = np.count_nonzero(hash_a != hash_b)  # 0 = identical
```

Lower Hamming distance means more similar content.

---

## License

MIT
