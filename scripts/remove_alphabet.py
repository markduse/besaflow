"""
Remove all cat:"Alphabet" entries from WORDS and from AUDIO_MANIFEST.
Audio files for those entries become orphans on disk (audio/{male,female}/*.mp3)
but cause no functional harm — they're just unreferenced. They can be deleted
manually later if you want the directories tidy.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"


def main():
    src = SRC.read_text()

    # 1. Strip Alphabet entries from WORDS by line-matching cat:"Alphabet".
    m = re.search(r"const WORDS = \[(.*?)\];\n", src, re.DOTALL)
    words_body = m.group(1)
    before_count = words_body.count("cat:\"Alphabet\"")
    if before_count == 0:
        print("No Alphabet entries to remove.")
        return

    # Collect the .a values we'll remove from the manifest.
    alphabet_a = re.findall(
        r'\{[^{}]*?cat:"Alphabet"[^{}]*?\}',
        words_body,
    )
    removed_texts = set()
    for entry in alphabet_a:
        ma = re.search(r'a:"([^"]+)"', entry)
        if ma:
            removed_texts.add(ma.group(1))
    print(f"Found {before_count} Alphabet entries to remove ({len(removed_texts)} unique .a values).")

    # Remove each entry line (including trailing comma + newline).
    new_words_body = re.sub(
        r"  \{[^{}]*?cat:\"Alphabet\"[^{}]*?\},?\n",
        "",
        words_body,
    )
    new_words_body = re.sub(
        r"\{[^{}]*?cat:\"Alphabet\"[^{}]*?\},?",
        "",
        new_words_body,
    )

    new_src = src.replace(words_body, new_words_body, 1)

    # 2. Strip those texts from AUDIO_MANIFEST.
    mm = re.search(r"const AUDIO_MANIFEST = (\{.*?\});\n", new_src, re.DOTALL)
    if mm:
        manifest = json.loads(mm.group(1))
        manifest_before = len(manifest)
        for t in removed_texts:
            manifest.pop(t, None)
        new_manifest_js = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
        new_src = new_src.replace(mm.group(1), new_manifest_js, 1)
        print(f"AUDIO_MANIFEST: {manifest_before} -> {len(manifest)} entries.")
    else:
        print("Warning: AUDIO_MANIFEST not found; skipping manifest cleanup.")

    SRC.write_text(new_src)
    print(f"File: {len(src):,} -> {len(new_src):,} bytes.")


if __name__ == "__main__":
    main()
