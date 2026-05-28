"""
Stage 5: Auto-import 453 new entries from gheg_albanian_clean_beginner_core_v2.xlsx.

For each new Gheg entry:
  - Derive phonetic from Gheg text using a simple sound map (improves over raw Albanian for Web Speech).
  - Pick emoji from English keyword via lookup table; fall back to category default.
  - Map XLSX category/subcategory to existing app cat or new (Numbers, Alphabet).
  - Decide WORDS vs PHRASES based on category (Conversation -> PHRASES, else WORDS).

Output:
  - Appends new entries to WORDS and PHRASES arrays inside index.html.
  - Prints a summary by category + any rows that fell to default emoji.
  - Idempotent: detects already-present .a values and skips them.
"""
import openpyxl
import re
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
XLSX = Path("/Users/marksmacmini/Downloads/gheg_albanian_clean_beginner_core_v2.xlsx")

# ---------- Phonetic derivation ----------
# Order matters: replace digraphs/trigraphs before single chars. Approximates English-reader pronunciation.
PHONETIC_RULES = [
    # Lowercase the input first, then apply these in order.
    ("dh", "th"),  # voiced 'th' as in "this"
    ("th", "th"),  # voiceless 'th' as in "thin"
    ("gj", "gy"),
    ("nj", "ny"),
    ("sh", "sh"),
    ("zh", "zh"),
    ("xh", "j"),
    ("ll", "l"),
    ("rr", "rr"),
    ("ë",  "uh"),
    ("ç",  "ch"),
    ("q",  "ch"),
    ("c",  "ts"),
    ("x",  "dz"),
    ("y",  "ue"),
    ("a",  "ah"),
    ("e",  "eh"),
    ("i",  "ee"),
    ("o",  "oh"),
    ("u",  "oo"),
]

def derive_phonetic(gheg):
    if not gheg:
        return ""
    # Handle slash-separated alt forms: derive only from the first form
    base = gheg.split("/")[0].strip().lower()
    out = base
    # Greedy multi-char replacements first. We do passes left-to-right manually so we never
    # double-replace something we already mapped (e.g., 'th' result of 'dh' shouldn't re-trigger).
    result = []
    i = 0
    while i < len(out):
        matched = False
        for src, dst in PHONETIC_RULES:
            if out[i:i+len(src)] == src:
                result.append(dst)
                i += len(src)
                matched = True
                break
        if not matched:
            result.append(out[i])
            i += 1
    return "".join(result)

# ---------- Emoji lookup ----------
# Keyword → emoji. Matched against English (lowercase). Longest substrings checked first.
EMOJI_MAP = {
    # Numbers (default 🔢)
    # Alphabet (default 🔤)
    # Verbs (default 🎬)
    # Family
    "mother":"👩","father":"👨","brother":"👨‍👦","sister":"👧","son":"👦","daughter":"👧",
    "grandmother":"👵","grandfather":"👴","grandma":"👵","grandpa":"👴","aunt":"👩","uncle":"👨",
    "cousin":"👫","wife":"👰","husband":"🤵","baby":"👶","child":"👶","children":"👶",
    "family":"👨‍👩‍👧","bride":"👰","groom":"🤵","nephew":"👦","niece":"👧","friend":"🧑‍🤝‍🧑",
    # Body
    "head":"🗣","face":"😊","eyes":"👀","eye":"👁","ear":"👂","ears":"👂","nose":"👃",
    "mouth":"👄","tooth":"🦷","teeth":"🦷","tongue":"👅","hair":"💇","beard":"🧔","hand":"✋",
    "hands":"🙌","arm":"💪","leg":"🦵","foot":"🦶","feet":"🦶","heart":"❤️","stomach":"🤰",
    "back":"🔙","skin":"🤚","blood":"🩸","bone":"🦴","finger":"☝️",
    # Animals
    "dog":"🐕","cat":"🐈","horse":"🐎","cow":"🐄","sheep":"🐑","goat":"🐐","pig":"🐖",
    "chicken":"🐔","rooster":"🐓","bird":"🐦","fish":"🐟","wolf":"🐺","bear":"🐻","fox":"🦊",
    "eagle":"🦅","snake":"🐍","mouse":"🐁","rabbit":"🐰",
    # Nature
    "sun":"☀️","moon":"🌙","star":"⭐","stars":"⭐","sky":"🌌","cloud":"☁️","rain":"🌧",
    "snow":"❄️","wind":"💨","fire":"🔥","water":"💧","earth":"🌍","mountain":"🏔","sea":"🌊",
    "ocean":"🌊","river":"🏞","lake":"💧","tree":"🌳","flower":"🌸","grass":"🌿","leaf":"🍃",
    "stone":"🪨","sand":"🏖","forest":"🌲","valley":"⛰","field":"🌾",
    # Food
    "bread":"🍞","water":"💧","milk":"🥛","coffee":"☕","tea":"🍵","wine":"🍷","beer":"🍺",
    "salt":"🧂","sugar":"🍬","oil":"🫒","cheese":"🧀","butter":"🧈","egg":"🥚","meat":"🥩",
    "chicken":"🍗","fish":"🐟","rice":"🍚","soup":"🍲","apple":"🍎","banana":"🍌","grape":"🍇",
    "lemon":"🍋","orange":"🍊","tomato":"🍅","potato":"🥔","onion":"🧅","garlic":"🧄",
    "pepper":"🌶","cake":"🍰","honey":"🍯","food":"🍽","breakfast":"🥞","lunch":"🥗","dinner":"🍝",
    # Household / objects
    "house":"🏠","home":"🏡","door":"🚪","window":"🪟","table":"🪑","chair":"🪑","bed":"🛏",
    "kitchen":"🍳","bathroom":"🚽","key":"🗝","clock":"🕰","watch":"⌚","book":"📖","pen":"🖊",
    "pencil":"✏️","paper":"📄","phone":"📱","computer":"💻","tv":"📺","car":"🚗","bus":"🚌",
    "train":"🚆","plane":"✈️","bike":"🚲","money":"💰","clothes":"👕","shirt":"👕","pants":"👖",
    "shoe":"👟","shoes":"👟","hat":"🎩","bag":"👜",
    # Time
    "day":"📅","night":"🌙","morning":"🌅","afternoon":"☀️","evening":"🌆","week":"📆",
    "month":"🗓","year":"📅","today":"📍","tomorrow":"➡️","yesterday":"⬅️","now":"⏰",
    "monday":"📅","tuesday":"📅","wednesday":"📅","thursday":"📅","friday":"📅","saturday":"📅","sunday":"📅",
    "january":"❄️","february":"❄️","march":"🌱","april":"🌧","may":"🌸","june":"☀️",
    "july":"🌞","august":"🌻","september":"🍂","october":"🎃","november":"🍁","december":"🎄",
    # Colors & adjectives (general moods)
    "red":"🟥","blue":"🟦","green":"🟩","yellow":"🟨","black":"⬛","white":"⬜","brown":"🟫",
    "big":"🟫","small":"🤏","tall":"📏","short":"📐","fast":"⚡","slow":"🐢","hot":"🔥","cold":"🥶",
    "good":"👍","bad":"👎","beautiful":"😍","ugly":"😖","happy":"😊","sad":"😢","angry":"😠",
    "tired":"😴","strong":"💪","weak":"🤕","old":"👴","young":"🧒","new":"🆕","clean":"✨","dirty":"🪣",
    # Verbs
    "eat":"🍴","drink":"🥤","sleep":"😴","walk":"🚶","run":"🏃","go":"➡️","come":"⬅️",
    "see":"👀","look":"👀","hear":"👂","speak":"🗣","talk":"🗣","read":"📖","write":"✍️",
    "work":"💼","play":"🎮","sing":"🎤","dance":"💃","love":"❤️","know":"🧠","think":"🤔",
    "want":"🙋","need":"🤲","give":"🎁","take":"✋","buy":"🛒","sell":"💵","open":"🔓",
    "close":"🔒","wait":"⏳","stop":"✋","help":"🆘","learn":"📚","teach":"🧑‍🏫","ask":"❓",
    "answer":"💬","yes":"✅","no":"❌","please":"🙏","thank":"🙏","sorry":"😔","hello":"👋","goodbye":"👋",
    "be":"⭕","have":"🤝",
}

CATEGORY_DEFAULT_EMOJI = {
    "Numbers":              "🔢",
    "Alphabet":             "🔤",
    "Verbs":                "🎬",
    "Family & People":      "👤",
    "Adjectives & Colors":  "🎨",
    "Time & Function Words":"⏰",
    "Body & Health":        "🧍",
    "Nature & Animals":     "🌿",
    "Food & Eating":        "🍴",
    "Household & Objects":  "🏠",
    "Greetings & Small Talk":"💬",
    "Everyday Expressions":"💭",
}

def pick_emoji(english, app_cat):
    if not english:
        return CATEGORY_DEFAULT_EMOJI.get(app_cat, "📝")
    eng_lower = english.lower()
    # Multi-word keys (longer first)
    for keyword in sorted(EMOJI_MAP.keys(), key=lambda k: -len(k)):
        if keyword in eng_lower:
            return EMOJI_MAP[keyword]
    return CATEGORY_DEFAULT_EMOJI.get(app_cat, "📝")

# ---------- Category mapping ----------
# XLSX (category, subcategory) -> app cat
def map_category(xlsx_cat, xlsx_sub):
    sub = (xlsx_sub or "").lower()
    if xlsx_cat == "Numbers":
        return "Numbers"
    if xlsx_cat == "Alphabet":
        return "Alphabet"
    if xlsx_cat == "Verbs":
        return "Verbs"
    if xlsx_cat == "Family":
        return "Family & People"
    if xlsx_cat == "Adjectives / Adverbs":
        return "Adjectives & Colors"
    if xlsx_cat == "Conversation":
        return "Greetings & Small Talk"
    if xlsx_cat == "Basics":
        if any(k in sub for k in ("month", "day", "week", "year", "time")):
            return "Time & Function Words"
        if any(k in sub for k in ("color", "colour")):
            return "Adjectives & Colors"
        return "Everyday Expressions"
    if xlsx_cat == "Nouns":
        # subcategory tells us
        if any(k in sub for k in ("body", "health", "face")):
            return "Body & Health"
        if any(k in sub for k in ("animal", "nature", "plant", "weather")):
            return "Nature & Animals"
        if any(k in sub for k in ("food", "drink", "kitchen")):
            return "Food & Eating"
        if any(k in sub for k in ("clothing", "personal")):
            return "Clothing & Personal"
        if any(k in sub for k in ("school", "work", "tech", "office", "tools")):
            return "School, Work & Tech"
        if any(k in sub for k in ("place", "transport", "travel", "vehicle")):
            return "Places & Transport"
        if any(k in sub for k in ("time",)):
            return "Time & Function Words"
        return "Household & Objects"
    return "Everyday Expressions"

def map_pos(xlsx_cat):
    return {
        "Numbers": "Number",
        "Alphabet": "Letter",
        "Verbs": "Verb",
        "Family": "Noun",
        "Nouns": "Noun",
        "Adjectives / Adverbs": "Adjective",
        "Conversation": "Phrase",
        "Basics": "Other",
    }.get(xlsx_cat, "Other")

def is_phrase_category(xlsx_cat):
    return xlsx_cat == "Conversation"

# ---------- Main ----------
def main():
    src = SRC.read_text()

    def extract_a(name):
        m = re.search(rf"const {name} = \[(.*?)\];", src, re.DOTALL)
        return set(re.findall(r'a:"([^"]+)"', m.group(1)))

    existing = extract_a("WORDS") | extract_a("PHRASES") | extract_a("SENTENCES")
    print(f"Existing distinct .a values in app: {len(existing)}")

    wb = openpyxl.load_workbook(XLSX, read_only=True)
    rows = list(wb["Gheg Beginner Core"].iter_rows(values_only=True))
    data = [r for r in rows[1:] if r and r[3]]
    print(f"XLSX rows: {len(data)}")

    new_word_entries = []
    new_phrase_entries = []
    skipped_dupes = 0
    skipped_family_verify = 0
    fallback_emoji_count = 0
    summary = Counter()

    for row in data:
        xlsx_cat, xlsx_sub, english, gheg, pron_helper, notes, confidence = row[:7]
        if not gheg:
            continue
        gheg = gheg.strip()
        # Skip dupes already in app
        if gheg in existing:
            skipped_dupes += 1
            continue
        if confidence == "family-verify":
            skipped_family_verify += 1
            continue

        app_cat = map_category(xlsx_cat, xlsx_sub)
        pos = map_pos(xlsx_cat)
        # Use XLSX pronunciation if present, else derive
        if pron_helper and pron_helper.strip():
            phonetic = pron_helper.strip()
        else:
            phonetic = derive_phonetic(gheg)
        emoji = pick_emoji(english or "", app_cat)
        if emoji in CATEGORY_DEFAULT_EMOJI.values() or emoji == "📝":
            fallback_emoji_count += 1

        entry = {
            "e": emoji,
            "w": english or "",
            "a": gheg,
            "p": phonetic,
            "cat": app_cat,
            "pos": pos,
        }
        if is_phrase_category(xlsx_cat):
            new_phrase_entries.append(entry)
            summary[("PHRASES", app_cat)] += 1
        else:
            new_word_entries.append(entry)
            summary[("WORDS", app_cat)] += 1

    print(f"\nNew WORDS to add:   {len(new_word_entries)}")
    print(f"New PHRASES to add: {len(new_phrase_entries)}")
    print(f"Skipped (already in app): {skipped_dupes}")
    print(f"Skipped (family-verify):  {skipped_family_verify}")
    print(f"Used fallback/category emoji: {fallback_emoji_count}")

    print(f"\nBreakdown by target array + category:")
    for (arr, cat), n in sorted(summary.items()):
        print(f"  {arr:8s} [{cat}] +{n}")

    # ---------- Patch index.html ----------
    def fmt_entry(e):
        # JS object literal matching existing style
        # Escape backslash and double-quotes in string values
        def esc(s):
            return s.replace('\\', '\\\\').replace('"', '\\"')
        return ('{e:"' + esc(e["e"]) + '",w:"' + esc(e["w"]) + '",a:"' + esc(e["a"])
                + '",p:"' + esc(e["p"]) + '",cat:"' + esc(e["cat"]) + '",pos:"' + esc(e["pos"]) + '"}')

    # Inject before the closing `];` of WORDS and PHRASES respectively.
    def append_to_array(name, src_text, new_entries):
        if not new_entries:
            return src_text
        marker = f"const {name} = ["
        start = src_text.index(marker)
        end = src_text.index("];", start)
        body = src_text[start+len(marker):end]
        # Find last entry; insert before "];"
        new_text = ",\n  " + ",\n  ".join(fmt_entry(e) for e in new_entries) + "\n"
        return src_text[:end] + new_text + src_text[end:]

    patched = append_to_array("WORDS",   src,    new_word_entries)
    patched = append_to_array("PHRASES", patched, new_phrase_entries)
    SRC.write_text(patched)
    print(f"\nPatched index.html: {len(src):,} -> {len(patched):,} bytes")

if __name__ == "__main__":
    main()
