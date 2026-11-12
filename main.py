#!/usr/bin/env python3
"""cutest-picture-01 entry: deliver the repo's picture to the output directory.

The picture lives beside this file as ``entry.png``; a JPEG named
``entry.jpg`` is accepted as a fallback when no PNG is present. The program
validates the image and copies it to the output directory byte-for-byte, so
every run produces identical output. Standard library only, no network.

Validation (competition rules): the file must be a whole PNG or JPEG of at
most 1 MiB and at most 1024x1024 pixels. "Whole" is checked, not just the
header: a PNG must end with its IEND chunk and a JPEG with its EOI marker,
so a truncated download is rejected instead of being submitted.
"""

import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
MAX_DIM = 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
JPEG_EOI = b"\xff\xd9"
# SOF markers that carry the frame dimensions (baseline, extended,
# progressive, lossless and their Huffman/arithmetic variants).
JPEG_SOF = (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF)


def _png_dimensions(data):
    """Return (width, height) for a PNG, or None if the header is bad."""
    if not data.startswith(PNG_MAGIC) or len(data) < 24:
        return None
    # After the 8-byte signature comes the IHDR chunk: 4-byte length,
    # 4-byte type "IHDR", then width and height as big-endian uint32.
    if data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def _jpeg_dimensions(data):
    """Return (width, height) for a JPEG, or None if no SOF frame found."""
    if not data.startswith(JPEG_MAGIC):
        return None
    i = 2
    n = len(data)
    while i + 4 <= n:
        if data[i] != 0xFF:
            return None
        marker = data[i + 1]
        if marker == 0xD9:  # EOI: no frame before the end of the file
            return None
        if marker == 0x01 or 0xD0 <= marker <= 0xD8:
            i += 2  # standalone markers carry no segment
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        if seg_len < 2 or i + 2 + seg_len > n:
            return None
        if marker in JPEG_SOF:
            if i + 9 > n:
                return None
            # SOF layout: length, precision, height, width.
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + seg_len
    return None


def _find_source(repo_dir):
    """Pick the picture file: entry.png first, entry.jpg as fallback."""
    for name in ("entry.png", "entry.jpg"):
        path = os.path.join(repo_dir, name)
        if os.path.isfile(path):
            return path
    return None


def _validate(path):
    """Check one image file; return an error string, or None if it passes."""
    name = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        return f"{name} is {len(data)} bytes, over the {MAX_BYTES} limit"
    if data.startswith(PNG_MAGIC):
        dims = _png_dimensions(data)
        if dims is None:
            return f"{name} has a PNG header but a bad IHDR chunk"
        if data[-8:-4] != b"IEND":
            return f"{name} is truncated: no IEND chunk at the end"
    elif data.startswith(JPEG_MAGIC):
        dims = _jpeg_dimensions(data)
        if dims is None:
            return f"{name} has a JPEG header but no SOF frame"
        if data[-2:] != JPEG_EOI:
            return f"{name} is truncated: no EOI marker at the end"
    else:
        return f"{name} is neither a PNG nor a JPEG"
    if dims[0] > MAX_DIM or dims[1] > MAX_DIM:
        return f"{name} is {dims[0]}x{dims[1]}, over {MAX_DIM}x{MAX_DIM}"
    return None


def main() -> int:
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    # MAKEFUN_INPUT_DIR is accepted for harness compatibility; the picture
    # does not come from /input, it is the repo's own image.
    _ = os.environ.get("MAKEFUN_INPUT_DIR", "/input")

    src = _find_source(repo_dir)
    if src is None:
        print("no entry.png or entry.jpg found next to main.py",
              file=sys.stderr)
        return 1
    error = _validate(src)
    if error is not None:
        print(error, file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, os.path.basename(src)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
