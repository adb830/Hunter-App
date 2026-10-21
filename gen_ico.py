#!/usr/bin/env python3
"""Generate a multi-resolution Windows .ico of the crosshair app icon."""
import zlib, struct, os, math

SS = 3

def png(width, height, pixels):
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
        return c
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r, g, b, a = pixels[y * width + x]
            raw += bytes((r, g, b, a))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make_icon(size):
    bg_top = (37, 80, 57)
    bg_bot = (14, 32, 22)
    ring = (249, 115, 22)
    heart = (239, 68, 68)
    cx = cy = size / 2.0
    R = size * 0.30
    ring_w = size * 0.055
    heart_r = size * 0.10
    px = []
    for y in range(size):
        for x in range(size):
            acc = [0.0, 0.0, 0.0]
            for sy in range(SS):
                for sx in range(SS):
                    fx = x + (sx + 0.5) / SS
                    fy = y + (sy + 0.5) / SS
                    col = lerp(bg_top, bg_bot, fy / size)
                    d = math.hypot(fx - cx, fy - cy)
                    if abs(d - R) <= ring_w / 2.0:
                        col = ring
                    if (abs(fx - cx) < size * 0.022 and abs(fy - cy) < size * 0.40):
                        if d < R - ring_w or d > R + ring_w:
                            col = ring
                    if (abs(fy - cy) < size * 0.022 and abs(fx - cx) < size * 0.40):
                        if d < R - ring_w or d > R + ring_w:
                            col = ring
                    if d <= heart_r:
                        col = heart
                    acc[0] += col[0]; acc[1] += col[1]; acc[2] += col[2]
            n = SS * SS
            px.append((int(acc[0] / n), int(acc[1] / n), int(acc[2] / n), 255))
    return png(size, size, px)

SIZES = [16, 24, 32, 48, 64, 128, 256]
images = [(s, make_icon(s)) for s in SIZES]

header = struct.pack("<HHH", 0, 1, len(images))
entries = b""
offset = 6 + 16 * len(images)
blob = b""
for s, img in images:
    entries += struct.pack("<BBBBHHII", s if s < 256 else 0, s if s < 256 else 0, 0, 0, 1, 32, len(img), offset)
    offset += len(img)
    blob += img

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Backcountry Hunter.ico")
with open(out, "wb") as f:
    f.write(header + entries + blob)
print("wrote", out, len(header) + len(entries) + len(blob), "bytes")