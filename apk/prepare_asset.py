#!/usr/bin/env python3
"""Create the offline APK asset: replace Tailwind CDN with a compiled local stylesheet."""
import re, shutil, os

BASE = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(BASE)
for _name in ("Backcountry Hunter.html", "index.html"):
    _candidate = os.path.join(parent, _name)
    if os.path.isfile(_candidate):
        src = _candidate
        break
else:
    raise SystemExit("ERROR: no source HTML found in " + parent +
                     " (looked for 'Backcountry Hunter.html' and 'index.html')")
dst = os.path.join(BASE, "app/src/main/assets/index.html")

html = open(src, encoding="utf-8").read()

# Remove the Play CDN script tag
html = re.sub(r'\s*<script src="https://cdn\.tailwindcss\.com"></script>', '', html)

# Remove the inline tailwind.config script block
html = re.sub(r'\s*<script>\s*tailwind\.config = \{.*?\};?\s*</script>', '',
              html, flags=re.S)

# Point Leaflet at the locally bundled copy so the map works in the offline APK
html = html.replace(
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />',
    '<link rel="stylesheet" href="leaflet/leaflet.css" />', 1)
html = html.replace(
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>',
    '<script src="leaflet/leaflet.js"></script>', 1)

# Inject compiled stylesheet just before </head>
html = html.replace('</head>', '  <link rel="stylesheet" href="tailwind.css" />\n</head>', 1)

os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, "w", encoding="utf-8").write(html)
print("wrote", dst, len(html), "bytes")

# Bundle the Hunting Pics folder so the Campfire gallery works offline in the APK
pics_src = os.path.join(os.path.dirname(BASE), "Hunting Pics")
pics_dst = os.path.join(BASE, "app/src/main/assets/Hunting Pics")
if os.path.isdir(pics_src):
    shutil.copytree(pics_src, pics_dst, dirs_exist_ok=True)
    n = len(os.listdir(pics_dst))
    print("bundled", n, "pics into", pics_dst)
else:
    print("WARNING: Hunting Pics folder not found at", pics_src)

# Bundle Leaflet so the Maps tab works offline in the APK
leaflet_src = os.path.join(BASE, "leaflet")
leaflet_dst = os.path.join(BASE, "app/src/main/assets/leaflet")
if os.path.isdir(leaflet_src):
    shutil.copytree(leaflet_src, leaflet_dst, dirs_exist_ok=True)
    print("bundled leaflet into", leaflet_dst)
else:
    print("WARNING: leaflet folder not found at", leaflet_src)
