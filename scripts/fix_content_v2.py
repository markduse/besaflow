"""
Content fixes (Mark's UX review):

1. Tighten every song snippet to its actual sung window (durations were too
   generous; Lumi Une snippet 1 startAt was inside the instrumental intro).
   New values come from re-reading the medium Whisper SRT for each track —
   segments map cleanly to snippets in the same order, so duration =
   Whisper segment duration, capped where the line is shorter than the
   segment Whisper grouped it with.

2. Strip the Numbers category from WORDS (doesn't help conversational
   learning; user has them memorized from school). Also drop the matching
   AUDIO_MANIFEST keys.

3. Collapse slash-pair .a values (e.g. "macë / mace") to just the Gheg
   form (left of the slash). User: "1 word per concept."

All changes are idempotent.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"


# (song_id, [(startAt, duration), ...]) — derived from the medium SRT.
TIGHTENED_TIMINGS = {
    "lumi-une": [
        (18, 10),   # 1  O e lumja unë (skip ~18s instrumental intro)
        (28, 12),   # 2  Shtatin si selvie
        (40,  6),   # 3  Po vjen nusja gjithë lezet
        (46,  6),   # 4  E bukur si zanë e malit
        (57,  6),   # 5  Kom me dasht si syt e ballit
        (63, 12),   # 6  O i lumi unë (groom's refrain)
        (86, 10),   # 7  Hedhim valle me tupan
        (95,  9),   # 8  Kena dasëm, dasëm t'madhe
       (104,  5),   # 9  Po vjen nusja, po vjen dhandri
    ],
    "vajze-me-zemer-guri": [
        ( 26,  8),  # 1  Sa e gjat o eshte kjo dit
        ( 34,  8),  # 2  E un rri vetem e t'pres  (was 38, too late)
        ( 52,  7),  # 3  Ti je vajz me zemer guri (chorus)
        ( 59,  7),  # 4  A e shkreta imja zemer
        ( 99,  7),  # 5  Ditet kalojn nji nga nji (verse 2)
        (171,  8),  # 6  Kalojn dit e koha shkon  (was 175, too late)
    ],
    "jem-ilira": [
        (16, 19),   # 1  Tan kto male sikur thërrasin (multi-line opening)
        (37,  5),   # 2  Mos harroni n'kangë
        (43,  8),   # 3  Jem Ilira, jem Teuta (chorus)
        (51,  8),   # 4  T'gjithë Shqiptarët kudo jan
        (93,  8),   # 5  Tanë kto male (verse 2)
    ],
    "lum-kush-rrin": [
        ( 29, 10),  # 1  Heeeej / N'Malesite tona
        ( 40,  8),  # 2  Kurre pa za s'e la kengetarin
        ( 49, 12),  # 3  Pa urti s'e la kuvendin
        ( 79, 10),  # 4  Nuk je trim pse vret filanin
        ( 99, 11),  # 5  Trim i thojne per sa t'jet jeta
        (129,  9),  # 6  Gja me t'madhe n'jet nuk ka
        (148, 12),  # 7  Kur me burra rrin n'kuvend
        (198, 11),  # 8  N'kohe te mire e n'kohe te veshtire (chorus)
    ],
}


def update_song_timings(src):
    m = re.search(r"const SONGS = (\[.*?\n\]);\n", src, re.DOTALL)
    if not m:
        raise SystemExit("SONGS block not found")
    songs_text = m.group(1)
    songs = json.loads(songs_text)
    for song in songs:
        sid = song["id"]
        if sid not in TIGHTENED_TIMINGS:
            continue
        new_times = TIGHTENED_TIMINGS[sid]
        if len(new_times) != len(song["snippets"]):
            print(f"  WARN {sid}: timing count {len(new_times)} != snippet count {len(song['snippets'])}")
            continue
        for snip, (start, dur) in zip(song["snippets"], new_times):
            snip["startAt"]  = start
            snip["duration"] = dur
        print(f"  songs/{sid}: {len(new_times)} snippet timings tightened")
    new_songs = json.dumps(songs, ensure_ascii=False, indent=2)
    return src.replace(songs_text, new_songs, 1)


def remove_numbers(src):
    m = re.search(r"const WORDS = \[(.*?)\];\n", src, re.DOTALL)
    body = m.group(1)
    before = body.count("cat:\"Numbers\"")
    if before == 0:
        print("  numbers: already absent")
        return src
    # Collect the .a values we're about to remove (for AUDIO_MANIFEST cleanup).
    numbers_a = set()
    for entry in re.findall(r'\{[^{}]*?cat:"Numbers"[^{}]*?\}', body):
        ma = re.search(r'a:"([^"]+)"', entry)
        if ma:
            numbers_a.add(ma.group(1))
    new_body = re.sub(
        r"  \{[^{}]*?cat:\"Numbers\"[^{}]*?\},?\n",
        "",
        body,
    )
    src = src.replace(body, new_body, 1)
    mm = re.search(r"const AUDIO_MANIFEST = (\{.*?\});\n", src, re.DOTALL)
    if mm:
        manifest = json.loads(mm.group(1))
        before_count = len(manifest)
        for t in numbers_a:
            manifest.pop(t, None)
        new_manifest_js = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
        src = src.replace(mm.group(1), new_manifest_js, 1)
        print(f"  numbers: removed {before} entries; manifest {before_count} -> {len(manifest)}")
    else:
        print(f"  numbers: removed {before} entries (manifest not found)")
    return src


def dedupe_slash_a(src):
    """ Replace a:"foo / bar" -> a:"foo" everywhere across all 3 data arrays. """
    # Find every a:"... / ..." occurrence and keep just the left side.
    pattern = re.compile(r'a:"([^"]+?)\s*/\s*[^"]+?"')
    matches = pattern.findall(src)
    if not matches:
        print("  slashes: none found")
        return src
    print(f"  slashes: collapsing {len(matches)} entries to Gheg form")
    new_src = pattern.sub(lambda m: 'a:"' + m.group(1).strip() + '"', src)
    return new_src


def main():
    src = SRC.read_text()
    before = len(src)
    print("Applying content fixes:")
    src = update_song_timings(src)
    src = remove_numbers(src)
    src = dedupe_slash_a(src)
    SRC.write_text(src)
    print(f"\nFile: {before:,} -> {len(src):,} bytes")


if __name__ == "__main__":
    main()
