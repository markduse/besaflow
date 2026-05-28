"""
Stage 1: Externalize ElevenLabs audio from index.html.

Reads AUDIO_MALE / AUDIO_FEMALE base64 maps from current index.html,
walks WORDS/PHRASES/SENTENCES order, writes per-entry mp3s to audio/{male,female}/NNNN.mp3,
emits audio/manifest.json (text -> "NNNN") for runtime lookup.

Does NOT modify index.html — that's done in patch_index.py after we verify the audio dir.
"""
import base64
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "index.html"
AUDIO_DIR = ROOT / "audio"

def slice_const(src, name):
    """Return body string between { and matching }; for `const NAME = { ... };`."""
    m = re.search(rf"const {name} = \{{", src)
    if not m:
        raise RuntimeError(f"{name} not found")
    start = m.end() - 1  # the opening '{'
    # Walk forward counting brace depth, but our map has no nested objects, so first '};' is the end.
    end = src.index("};", start)
    return src[start+1:end]  # inside braces

def parse_map(body):
    """Parse {"key": "base64", ...} body into a dict. Keys may have escaped quotes."""
    out = {}
    # Pattern: a quoted key (which may include \'), colon, quoted base64 value.
    # Keys are simple — no embedded double quotes in our data — but may have \' (escaped single quote).
    pattern = re.compile(r'"((?:[^"\\]|\\.)+)"\s*:\s*"([A-Za-z0-9+/=]+)"')
    for m in pattern.finditer(body):
        raw_key = m.group(1)
        # Unescape JS string escapes that appear in our data: \' -> '
        key = raw_key.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
        out[key] = m.group(2)
    return out

def extract_array_a(src, name):
    """Return list of .a values from `const NAME = [ ... ];` in declaration order."""
    m = re.search(rf"const {name} = \[(.*?)\];", src, re.DOTALL)
    return re.findall(r'a:"([^"]+)"', m.group(1))

def main():
    print(f"Reading {SRC} ({SRC.stat().st_size:,} bytes)...")
    src = SRC.read_text()

    print("Extracting AUDIO_MALE...")
    male = parse_map(slice_const(src, "AUDIO_MALE"))
    print(f"  {len(male)} male entries")

    print("Extracting AUDIO_FEMALE...")
    female = parse_map(slice_const(src, "AUDIO_FEMALE"))
    print(f"  {len(female)} female entries")

    words     = extract_array_a(src, "WORDS")
    phrases   = extract_array_a(src, "PHRASES")
    sentences = extract_array_a(src, "SENTENCES")
    all_texts = words + phrases + sentences
    print(f"\nData arrays: WORDS={len(words)} PHRASES={len(phrases)} SENTENCES={len(sentences)} TOTAL={len(all_texts)}")

    # Build numeric index for runtime: text -> "NNNN"
    manifest = {t: f"{i:04d}" for i, t in enumerate(all_texts)}

    # Write male files
    male_dir = AUDIO_DIR / "male"
    male_dir.mkdir(parents=True, exist_ok=True)
    male_written = male_missing = 0
    for i, text in enumerate(all_texts):
        b64 = male.get(text)
        if b64:
            (male_dir / f"{i:04d}.mp3").write_bytes(base64.b64decode(b64))
            male_written += 1
        else:
            male_missing += 1

    # Write female files
    female_dir = AUDIO_DIR / "female"
    female_dir.mkdir(parents=True, exist_ok=True)
    female_written = female_missing = 0
    missing_female_texts = []
    for i, text in enumerate(all_texts):
        b64 = female.get(text)
        if b64:
            (female_dir / f"{i:04d}.mp3").write_bytes(base64.b64decode(b64))
            female_written += 1
        else:
            female_missing += 1
            missing_female_texts.append(text)

    # Write manifest
    manifest_path = AUDIO_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

    # Write a list of missing female texts so we can regen later
    gaps_path = AUDIO_DIR / "missing_female.json"
    gaps_path.write_text(json.dumps(missing_female_texts, ensure_ascii=False, indent=2))

    print(f"\nMale:   wrote {male_written}/{len(all_texts)}  (missing {male_missing})")
    print(f"Female: wrote {female_written}/{len(all_texts)}  (missing {female_missing})")
    print(f"Manifest: {manifest_path}")
    print(f"Missing-female list: {gaps_path}")

    # Total size on disk
    total = sum(p.stat().st_size for p in AUDIO_DIR.rglob("*.mp3"))
    print(f"Total audio bytes: {total:,} ({total/1024/1024:.1f} MB)")

if __name__ == "__main__":
    main()
