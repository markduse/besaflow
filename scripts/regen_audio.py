"""
Regenerate ElevenLabs audio for every entry that lacks it.

Work list (in priority order):
  1. MALE clips for entries not yet in AUDIO_MANIFEST  (default voice first)
  2. FEMALE clips for those same new entries
  3. FEMALE clips for old manifest entries whose file is missing (the
     original 118-gap backlog, minus removed content)
  4. MALE gap fill (safety; should be ~zero)

Resumable: files already on disk are skipped. On quota errors the run
aborts cleanly — rerun after reset and it continues where it left off.

At the end, AUDIO_MANIFEST in index.html and audio/manifest.json gain
entries for every text whose MALE file exists (male is the fallback
voice, so a manifest entry is only useful once male audio is real).

Usage:
  python3 scripts/regen_audio.py --dry-run    # plan + char estimate only
  python3 scripts/regen_audio.py              # full run
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
AUDIO = ROOT / "audio"

VOICES = {"male": "K2OjOkcdDAvKe6CqQvbR", "female": "4NbUAKMO4XEu9VtIlvDL"}
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.5, "similarity_boost": 0.75}


def get_key():
    k = os.environ.get("ELEVENLABS_API_KEY", "")
    if not k:
        # Fallback: parse ~/.zshrc (harness shells may not source it)
        zshrc = Path.home() / ".zshrc"
        if zshrc.exists():
            m = re.search(r'ELEVENLABS_API_KEY="(sk_[^"]+)"', zshrc.read_text())
            if m:
                k = m.group(1)
    if not k:
        sys.exit("No ELEVENLABS_API_KEY in env or ~/.zshrc")
    return k


def tts_text(a):
    # Safety: if any slash-pair survived dedupe, speak only the first form.
    return a.split("/")[0].strip() if " / " in a else a.strip()


def main():
    dry = "--dry-run" in sys.argv
    key = get_key()
    src = SRC.read_text()

    mm = re.search(r"const AUDIO_MANIFEST = (\{.*?\});", src, re.DOTALL)
    manifest = json.loads(mm.group(1))

    # Ordered distinct .a across the three data arrays
    seen, ordered = set(), []
    for name in ["WORDS", "PHRASES", "SENTENCES"]:
        m = re.search(rf"const {name} = \[(.*?)\];\n", src, re.DOTALL)
        for a in re.findall(r'a:"((?:[^"\\]|\\.)+)"', m.group(1)):
            a = a.replace('\\"', '"').replace("\\\\", "\\")
            if a not in seen:
                seen.add(a)
                ordered.append(a)

    next_id = max(int(v) for v in manifest.values()) + 1
    new_texts = [a for a in ordered if a not in manifest]
    new_ids = {}
    for a in new_texts:
        new_ids[a] = f"{next_id:04d}"
        next_id += 1

    def missing(gender, text_id):
        return not (AUDIO / gender / f"{text_id}.mp3").exists()

    work = []
    for a in new_texts:
        if missing("male", new_ids[a]):
            work.append((new_ids[a], a, "male"))
    for a in new_texts:
        if missing("female", new_ids[a]):
            work.append((new_ids[a], a, "female"))
    for a, i in manifest.items():
        if missing("female", i):
            work.append((i, a, "female"))
    for a, i in manifest.items():
        if missing("male", i):
            work.append((i, a, "male"))

    chars = sum(len(tts_text(t)) for _, t, _ in work)
    print(f"Entries in data: {len(ordered)} distinct")
    print(f"New (no manifest entry): {len(new_texts)}")
    print(f"Work items: {len(work)} clips  (~{chars:,} characters)")
    by = {}
    for _, _, g in work:
        by[g] = by.get(g, 0) + 1
    print(f"By voice: {by}")
    if dry:
        return

    ok = fail = 0
    consec_err = 0
    t0 = time.time()
    for n, (tid, text, gender) in enumerate(work, 1):
        out = AUDIO / gender / f"{tid}.mp3"
        body = json.dumps({
            "text": tts_text(text),
            "model_id": MODEL,
            "voice_settings": SETTINGS,
            "output_format": "mp3_22050_32",
        }).encode()
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES[gender]}",
            data=body,
            headers={"xi-api-key": key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                out.write_bytes(r.read())
            ok += 1
            consec_err = 0
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:200]
            if "quota" in detail.lower():
                print(f"\nQUOTA EXHAUSTED after {ok} clips — rerun after reset to resume.")
                break
            fail += 1
            consec_err += 1
            print(f"  ERR {gender}/{tid} {text!r}: {e.code} {detail}")
            if consec_err >= 8:
                print("8 consecutive errors — aborting.")
                break
            time.sleep(2)
        except Exception as e:
            fail += 1
            consec_err += 1
            print(f"  ERR {gender}/{tid} {text!r}: {e}")
            if consec_err >= 8:
                print("8 consecutive errors — aborting.")
                break
            time.sleep(2)
        if n % 25 == 0:
            rate = n / (time.time() - t0)
            eta = (len(work) - n) / rate / 60
            print(f"  {n}/{len(work)}  ok={ok} fail={fail}  eta {eta:.0f} min")
        time.sleep(0.15)

    print(f"\nDone: {ok} generated, {fail} failed, {len(work)-ok-fail} skipped/remaining")

    # ── Update manifests for every new text whose MALE file now exists ──
    added = {a: i for a, i in new_ids.items() if (AUDIO / "male" / f"{i}.mp3").exists()}
    if added:
        manifest.update(added)
        new_js = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
        src2 = SRC.read_text()  # re-read in case anything changed
        mm2 = re.search(r"const AUDIO_MANIFEST = (\{.*?\});", src2, re.DOTALL)
        src2 = src2.replace(mm2.group(1), new_js, 1)
        SRC.write_text(src2)
        (AUDIO / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        print(f"AUDIO_MANIFEST updated: +{len(added)} entries -> {len(manifest)} total")
    else:
        print("No new male files — manifest unchanged.")


if __name__ == "__main__":
    main()
