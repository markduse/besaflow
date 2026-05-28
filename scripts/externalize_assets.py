"""
Stage 1 extension: externalize the remaining base64 blobs in index.html.

  - 4 milestone-song <audio> tags  -> audio/milestones/{id}.mp3
  - 3x duplicated eagle PNG inline -> assets/eagle.png + replace inline with href/src
  - 2x duplicated favicon/og PNGs  -> use the actual favicon.png / og-image.png that exist in repo

After this, index.html should be ~500 KB (pure code).
Idempotent: skips if data URIs are already gone.
"""
import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "index.html"
BAK  = ROOT / "index.html.bak-before-assets"

MILESTONE_DIR = ROOT / "audio" / "milestones"
ASSETS_DIR    = ROOT / "assets"  # already exists with reference art

SONG_IDS = ["shotaAudio", "gjovalinAudio", "lekeAudio", "nikolleAudio"]

def main():
    src = SRC.read_text()
    if 'data:audio/mpeg;base64,' not in src and 'data:image/png;base64,' not in src:
        print("Already externalized. No changes.")
        return

    print(f"Before: {len(src):,} bytes ({len(src)/1024/1024:.2f} MB)")
    BAK.write_text(src)

    MILESTONE_DIR.mkdir(parents=True, exist_ok=True)

    # ---- 1. Externalize the 4 milestone song <audio> tags ----
    # Pattern: <audio id="X" preload="none">\n  <source src="data:audio/mpeg;base64,YYY" type="audio/mpeg">\n  </audio>
    # Or: <audio id="X" preload="none" src="data:audio/mpeg;base64,YYY"></audio>
    # We'll match either by looking for the id then the next data:audio URI within ~50MB.

    for song_id in SONG_IDS:
        m = re.search(rf'<audio[^>]*id="{song_id}"[^>]*>', src)
        if not m:
            print(f"  WARN: no <audio id={song_id!r}> tag found, skipping")
            continue
        tag_start = m.start()
        # Find the next data:audio URI after this tag (within reasonable distance)
        data_match = re.search(r'data:audio/mpeg;base64,([A-Za-z0-9+/=]+)', src[tag_start:tag_start + 10_000_000])
        if not data_match:
            print(f"  WARN: no base64 src for {song_id}, skipping")
            continue
        b64 = data_match.group(1)
        decoded = base64.b64decode(b64)
        out_path = MILESTONE_DIR / f"{song_id}.mp3"
        out_path.write_bytes(decoded)
        print(f"  {song_id} -> audio/milestones/{song_id}.mp3 ({len(decoded)/1024:.0f} KB)")

        # Replace data URI with relative URL
        old_uri = data_match.group(0)
        new_uri = f"audio/milestones/{song_id}.mp3"
        src = src.replace(old_uri, new_uri, 1)

    # ---- 2. Externalize duplicate eagle PNGs ----
    # Find all remaining base64 image URIs, group by base64 content
    img_matches = list(re.finditer(r'data:image/png;base64,([A-Za-z0-9+/=]+)', src))
    print(f"\n  Found {len(img_matches)} inline PNG data URIs after song extraction")

    # Group by base64 fingerprint (first 64 chars)
    groups = {}
    for m in img_matches:
        fp = m.group(1)[:64]
        groups.setdefault(fp, []).append(m)
    for fp, occurrences in groups.items():
        b64 = occurrences[0].group(1)
        decoded = base64.b64decode(b64)
        size_kb = len(decoded)/1024

        # Identify which asset this is. Compare against existing favicon.png / og-image.png.
        favicon_bytes = (ROOT / "favicon.png").read_bytes()
        og_bytes      = (ROOT / "og-image.png").read_bytes()
        if decoded == favicon_bytes:
            relpath = "favicon.png"
        elif decoded == og_bytes:
            relpath = "og-image.png"
        else:
            # Must be the eagle. Save to assets/eagle.png if not already there.
            eagle_path = ASSETS_DIR / "eagle.png"
            if not eagle_path.exists() or eagle_path.read_bytes() != decoded:
                eagle_path.write_bytes(decoded)
                print(f"  Wrote eagle.png to assets/ ({size_kb:.0f} KB)")
            relpath = "assets/eagle.png"

        print(f"  PNG group ({size_kb:.0f} KB, {len(occurrences)} occurrences) -> {relpath}")
        # Replace each occurrence with the relpath
        old_uri = "data:image/png;base64," + b64
        src = src.replace(old_uri, relpath)

    print(f"\nAfter:  {len(src):,} bytes ({len(src)/1024/1024:.2f} MB)")
    SRC.write_text(src)

if __name__ == "__main__":
    main()
