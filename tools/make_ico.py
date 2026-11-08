#!/usr/bin/env python3
"""Builds desktop-app/pastescribe.ico (the .exe icon) from the extension's icon drawing."""
import importlib.util
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("make_icons", root / "tools" / "make_icons.py")
make_icons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_icons)

SIZES = (16, 32, 48, 64, 256)
images = [(size, make_icons.render(size)) for size in SIZES]  # PNG bytes (ICO accepts PNG entries)

header = struct.pack("<HHH", 0, 1, len(images))
offset = 6 + 16 * len(images)
entries, blobs = b"", b""
for size, data in images:
    entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
    blobs += data
    offset += len(data)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "desktop-app" / "pastescribe.ico"
out.write_bytes(header + entries + blobs)
print("wrote", out, f"({out.stat().st_size} bytes, sizes {SIZES})")
