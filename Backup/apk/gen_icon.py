#!/usr/bin/env python3
"""Generate launcher PNGs without external imaging libs (pure zlib/struct)."""
import zlib, struct, os, math

SS = 3  # supersample factor for anti-aliasing

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
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")

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
                    t = fy / size
                    col = lerp(bg_top, bg_bot, t)
                    d = math.hypot(fx - cx, fy - cy)
                    # ring
                    if abs(d - R) <= ring_w / 2.0:
                        col = ring
                    # crosshair ticks
                    if (abs(fx - cx) < size * 0.022 and (d < R - ring_w or d > R + ring_w)
                            and abs(fy - cy) < size * 0.40):
                        if d < R - ring_w * 1.0 or d > R + ring_w:
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

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app/src/main/res")
dens = {48: "mipmap-mdpi", 72: "mipmap-hdpi", 96: "mipmap-xhdpi",
        144: "mipmap-xxhdpi", 192: "mipmap-xxxhdpi"}
for s, d in dens.items():
    folder = os.path.join(out, d)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "ic_launcher.png"), "wb") as f:
        f.write(make_icon(s))
    print("wrote", folder, s)
print("done")