"""
Remove obvious English loanwords from WORDS. User instruction:
"if it sounds super american word or english we can assume and move on.
we are trying to learn albanian"

Curated removal list — entries where the Albanian word is essentially the
English word plus an Albanian suffix and the meaning is trivially clear from
English alone (no learning value). Cultural / heritage borrowings (familje,
Bajrami) and time units (minutë, sekondë) that lack native alternatives are
kept.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# Albanian .a values to remove.
LOANWORDS = {
    "banane", "bankë", "bicikletë", "doktor", "garazh", "hotel",
    "internet", "laptop", "limon", "mikrovala", "motor",
    "pantallona", "pantolla", "park", "parking", "patate",
    "polic", "projekt", "restorant", "sendviç", "stacion",
    "supermarket", "test", "universitet", "video",
    # Additional obvious loans not caught by the prefix heuristic
    "avion", "ambulancë", "biletë", "gazetë", "kompjuter",
    "telefon", "televizor", "frigorifer", "tarifë",
    "kamera", "barkode", "kodi",
}


def main():
    src = SRC.read_text()
    before = len(src)
    removed = []

    m = re.search(r"const WORDS = \[(.*?)\];\n", src, re.DOTALL)
    body = m.group(1)

    # Match each entry; drop if its .a is in LOANWORDS.
    def keep_or_drop(match):
        a_match = re.search(r'a:"([^"]+)"', match.group(0))
        if a_match and a_match.group(1) in LOANWORDS:
            removed.append(a_match.group(1))
            return ""
        return match.group(0)

    new_body = re.sub(r"  \{[^{}]*?\},?\n", keep_or_drop, body)
    src = src.replace(body, new_body, 1)

    print(f"Removed {len(removed)} loanword entries:")
    for w in removed:
        print(f"  - {w}")

    # Clean up matching AUDIO_MANIFEST entries.
    mm = re.search(r"const AUDIO_MANIFEST = (\{.*?\});\n", src, re.DOTALL)
    if mm:
        manifest = json.loads(mm.group(1))
        before_count = len(manifest)
        for t in removed:
            manifest.pop(t, None)
        new_manifest_js = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
        src = src.replace(mm.group(1), new_manifest_js, 1)
        print(f"\nAUDIO_MANIFEST: {before_count} -> {len(manifest)} entries")

    SRC.write_text(src)
    print(f"File: {before:,} -> {len(src):,} bytes")


if __name__ == "__main__":
    main()
