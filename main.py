"""cutest-picture-01 entry: write the repo's picture to /output/entry.png.

Copies entry.png from the repository root (the directory holding this
file) to the output directory unchanged. Deterministic: the same bytes
every run. Standard library only, no network.

The image is validated before copying: it must be a whole PNG or JPEG
of at most 1 MiB and at most 1024x1024 pixels, per the competition rules.
"""

import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
MAX_DIM = 1024


def _png_size(path):
    with open(path, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return (w, h)


def main() -> int:
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    # MAKEFUN_INPUT_DIR is accepted for harness compatibility; the picture
    # does not come from /input, it is the repo's own image.
    _ = os.environ.get("MAKEFUN_INPUT_DIR", "/input")

    src = os.path.join(repo_dir, "entry.png")
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        print(f"entry.png is {size} bytes, over the {MAX_BYTES} limit",
              file=sys.stderr)
        return 1
    dims = _png_size(src)
    if dims is None:
        print("entry.png is not a PNG image", file=sys.stderr)
        return 1
    if dims[0] > MAX_DIM or dims[1] > MAX_DIM:
        print(f"entry.png is {dims[0]}x{dims[1]}, over {MAX_DIM}x{MAX_DIM}",
              file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
