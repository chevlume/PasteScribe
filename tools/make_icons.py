#!/usr/bin/env python3
"""Genera los iconos PNG de la extensión (sin dependencias externas)."""
import struct
import sys
import zlib
from pathlib import Path

SS = 4  # supersampling para suavizar bordes


def png(size, pixels):
    raw = b"".join(b"\x00" + bytes(pixels[y * size * 4:(y + 1) * size * 4]) for y in range(size))
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def inside_round_rect(x, y, n, r):
    cx = min(max(x, r), n - r)
    cy = min(max(y, r), n - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def render(size):
    n = size * SS
    ibeam = [  # rectángulos (x0, y0, x1, y1) en proporción del lado
        (0.44, 0.22, 0.56, 0.78),   # tallo
        (0.32, 0.22, 0.68, 0.30),   # serif superior
        (0.32, 0.70, 0.68, 0.78),   # serif inferior
    ]
    out = bytearray()
    for py in range(size):
        for px in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(SS):
                for sx in range(SS):
                    x, y = px * SS + sx + 0.5, py * SS + sy + 0.5
                    if not inside_round_rect(x, y, n, n * 0.22):
                        continue
                    t = y / n
                    col = (int(37 + 20 * t), int(99 - 10 * t), int(235 - 30 * t))  # degradado azul
                    if any(x0 * n <= x <= x1 * n and y0 * n <= y <= y1 * n for x0, y0, x1, y1 in ibeam):
                        col = (255, 255, 255)
                    acc[0] += col[0]; acc[1] += col[1]; acc[2] += col[2]; acc[3] += 255
            cnt = SS * SS
            a = acc[3] // cnt
            if acc[3]:
                out += bytes([acc[0] * 255 // acc[3], acc[1] * 255 // acc[3], acc[2] * 255 // acc[3], a])
            else:
                out += bytes([0, 0, 0, 0])
    return png(size, out)


if __name__ == "__main__":
    dest = Path(sys.argv[1] if len(sys.argv) > 1 else "chrome-extension/icons")
    dest.mkdir(parents=True, exist_ok=True)
    for s in (16, 48, 128):
        (dest / f"icon-{s}.png").write_bytes(render(s))
        print("wrote", dest / f"icon-{s}.png")
