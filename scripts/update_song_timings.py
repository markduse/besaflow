"""
Update startAt + duration for every song snippet based on Whisper timing
(medium model, manually aligned against user-verified Gheg lyrics).

The Whisper transcription is phonetically garbled (the model is trained on
standard Tosk Albanian, not Gheg) but the *timing* is solid — we use the
verified Gheg lyrics as the ground truth for content and Whisper as the
ground truth for when each line is sung.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# song_id -> list of (startAt_seconds, duration_seconds) in snippet order.
# Durations: ~12s typical (enough to hear the line clearly), longer for
# refrains, capped so the snippet doesn't bleed into the next one.
TIMINGS = {
    "lumi-une": [
        (0,   14),   # 1  O e lumja unë / Ç'paska rritur nona
        (28,  12),   # 2  Shtatin si selvie / Kangën po ja knojna
        (40,  10),   # 3  Po vjen nusja gjithë lezet
        (46,  11),   # 4  E bukur si zanë e malit
        (57,  10),   # 5  Kom me dasht si syt e ballit
        (63,  16),   # 6  O i lumi unë (groom's refrain)
        (86,  10),   # 7  Hedhim valle me tupan
        (95,  10),   # 8  Kena dasëm (estimated — Whisper grouped this with snippet 7)
        (104, 12),   # 9  Po vjen nusja, po vjen dhandri
    ],
    "vajze-me-zemer-guri": [
        (27,  12),   # 1  Sa e gjat o eshte kjo dit
        (38,  14),   # 2  E un rri vetem e t'pres
        (52,   8),   # 3  Ti je vajz me zemer guri (chorus)
        (59,   8),   # 4  A e shkreta imja zemer
        (99,  12),   # 5  Ditet kalojn nji nga nji (verse 2)
        (175, 12),   # 6  Kalojn dit e koha shkon (verse 3)
    ],
    "jem-ilira": [
        (16,  21),   # 1  Tan kto male sikur thërrasin
        (37,   7),   # 2  Mos harroni n'kangë
        (43,   8),   # 3  Jem Ilira, jem Teuta (chorus)
        (51,  12),   # 4  T'gjithë Shqiptarët kudo jan
        (93,  18),   # 5  Tanë kto male (verse 2)
    ],
    "lum-kush-rrin": [
        (30,  12),   # 1  Heeeej / N'Malesite tona
        (40,  10),   # 2  Kurre pa za s'e la kengetarin
        (49,  14),   # 3  Pa urti s'e la kuvendin
        (79,  12),   # 4  Nuk je trim pse vret filanin
        (99,  14),   # 5  Trim i thojne per sa t'jet jeta
        (129, 12),   # 6  Gja me t'madhe n'jet nuk ka
        (148, 14),   # 7  Kur me burra rrin n'kuvend
        (198, 14),   # 8  N'kohe te mire e n'kohe te veshtire (chorus)
    ],
}


def main():
    src = SRC.read_text()

    # Extract the SONGS literal so we can edit it as Python.
    m = re.search(r"const SONGS = (\[.*?\n\]);\n", src, re.DOTALL)
    if not m:
        raise SystemExit("SONGS block not found")
    songs_text = m.group(1)
    songs = json.loads(songs_text)

    # Apply timings.
    updates = 0
    for song in songs:
        sid = song["id"]
        if sid not in TIMINGS:
            print(f"  skip {sid} (no timings)")
            continue
        timings = TIMINGS[sid]
        if len(timings) != len(song["snippets"]):
            raise SystemExit(
                f"timing count mismatch for {sid}: have {len(timings)} "
                f"timings for {len(song['snippets'])} snippets"
            )
        for snip, (start, dur) in zip(song["snippets"], timings):
            snip["startAt"]  = start
            snip["duration"] = dur
            updates += 1
        print(f"  {sid}: updated {len(timings)} snippets")

    # Re-serialize as JSON (valid JS) and substitute.
    new_songs = json.dumps(songs, ensure_ascii=False, indent=2)
    new_src = src.replace(songs_text, new_songs, 1)
    SRC.write_text(new_src)
    print(f"\nWrote {updates} snippet timings. File: {len(src):,} -> {len(new_src):,} bytes.")


if __name__ == "__main__":
    main()
