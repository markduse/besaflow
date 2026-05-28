"""
Stage 1 patch: rewrite index.html to use external audio.

Changes:
  1. Replace `const AUDIO_MALE = {<53MB base64>};` with `const AUDIO_MANIFEST = {<text → "NNNN">};`
  2. Delete `const AUDIO_FEMALE = {<13MB base64>};` entirely (manifest covers both genders)
  3. Replace speak() function with externalized version

Idempotent: if index.html already has AUDIO_MANIFEST, this is a no-op.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "index.html"
BAK  = ROOT / "index.html.bak-before-externalize"
MANIFEST_PATH = ROOT / "audio" / "manifest.json"

def main():
    src = SRC.read_text()
    if "AUDIO_MANIFEST" in src:
        print("Already patched (AUDIO_MANIFEST present). No changes.")
        return

    print(f"Original index.html: {len(src):,} bytes ({len(src)/1024/1024:.1f} MB)")

    # Back up before mutating
    BAK.write_text(src)
    print(f"Backup written: {BAK.name}")

    # ---- 1. Find and delete the AUDIO_MALE block ----
    m_male = re.search(r'const AUDIO_MALE = \{', src)
    end_male = src.index("};\n", m_male.end()) + 3  # include "};\n"
    male_block = src[m_male.start():end_male]
    print(f"AUDIO_MALE block: {len(male_block):,} bytes")

    # ---- 2. Find and delete the AUDIO_FEMALE block ----
    m_female = re.search(r'const AUDIO_FEMALE = \{', src)
    end_female = src.index("};\n", m_female.end()) + 3
    female_block = src[m_female.start():end_female]
    print(f"AUDIO_FEMALE block: {len(female_block):,} bytes")

    # ---- 3. Build replacement: a single AUDIO_MANIFEST inline ----
    manifest = json.loads(MANIFEST_PATH.read_text())
    # Compact JSON to keep index.html small
    manifest_js = json.dumps(manifest, ensure_ascii=False, separators=(',', ':'))
    replacement = (
        "// AUDIO_MANIFEST: maps Albanian text -> 4-digit ID. Files served from /audio/{male,female}/NNNN.mp3\n"
        f"const AUDIO_MANIFEST = {manifest_js};\n"
    )
    print(f"AUDIO_MANIFEST: {len(replacement):,} bytes")

    # Replace male block with manifest, drop female block entirely
    new_src = src.replace(male_block, replacement, 1)
    new_src = new_src.replace(female_block, "", 1)

    # ---- 4. Replace speak() function ----
    # Old signature spans lines 1665..1685 — match by content.
    old_speak = (
        "function speak(albanian, phonetic) {\n"
        "  // Stop any currently playing clip\n"
        "  if (_speakAudio) { _speakAudio.pause(); _speakAudio = null; }\n"
        "\n"
        "  // Try pre-recorded audio first\n"
        "  const map = _voicePref === 'female' ? AUDIO_FEMALE : AUDIO_MALE;\n"
        "  const b64 = map[albanian];\n"
        "  if (b64) {\n"
        "    _speakAudio = new Audio('data:audio/mpeg;base64,' + b64);\n"
        "    _speakAudio.play().catch(() => {});\n"
        "    return;\n"
        "  }\n"
        "\n"
        "  // Fallback to Web Speech API with phonetic\n"
        "  if (!window.speechSynthesis) return;\n"
        "  speechSynthesis.cancel();\n"
        "  const u = new SpeechSynthesisUtterance(phonetic || albanian);\n"
        "  u.lang = 'en-US'; u.rate = 0.72; u.pitch = 1.0;\n"
        "  speechSynthesis.speak(u);\n"
        "}"
    )
    new_speak = (
        "function speak(albanian, phonetic) {\n"
        "  if (_speakAudio) { _speakAudio.pause(); _speakAudio = null; }\n"
        "  const idx = AUDIO_MANIFEST[albanian];\n"
        "  const wantFemale = _voicePref === 'female';\n"
        "  if (idx) {\n"
        "    const tryPlay = (gender) => {\n"
        "      _speakAudio = new Audio('audio/' + gender + '/' + idx + '.mp3');\n"
        "      return _speakAudio.play();\n"
        "    };\n"
        "    tryPlay(wantFemale ? 'female' : 'male').catch(() => {\n"
        "      // Female may be missing (~118 clips pending regen). Fall back to male, then Web Speech.\n"
        "      if (wantFemale) {\n"
        "        tryPlay('male').catch(() => speakViaSpeech(phonetic || albanian));\n"
        "      } else {\n"
        "        speakViaSpeech(phonetic || albanian);\n"
        "      }\n"
        "    });\n"
        "    return;\n"
        "  }\n"
        "  speakViaSpeech(phonetic || albanian);\n"
        "}\n"
        "function speakViaSpeech(text) {\n"
        "  if (!window.speechSynthesis) return;\n"
        "  speechSynthesis.cancel();\n"
        "  const u = new SpeechSynthesisUtterance(text);\n"
        "  u.lang = 'en-US'; u.rate = 0.72; u.pitch = 1.0;\n"
        "  speechSynthesis.speak(u);\n"
        "}"
    )
    if old_speak not in new_src:
        print("ERROR: could not locate exact speak() function — bailing.")
        # Restore by not writing
        sys.exit(1)
    new_src = new_src.replace(old_speak, new_speak, 1)

    SRC.write_text(new_src)
    print(f"\nNew index.html: {len(new_src):,} bytes ({len(new_src)/1024/1024:.2f} MB)")
    print(f"Reduction: {len(src) - len(new_src):,} bytes ({(1 - len(new_src)/len(src))*100:.1f}%)")

if __name__ == "__main__":
    main()
