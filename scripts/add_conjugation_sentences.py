"""
Add a batch of simple Gheg conjugation sentences to SENTENCES.

Patterns covered:
  - Subject + verb (past): I slept, you slept, the boy slept, we slept...
  - Past with object: the mother cooked eggs, the boy ate apples
  - Subject + 'went' + place: I went home, the dad went to work
  - Subject + is + adjective: the boy is sad, the girl is happy
  - Noun + adjective: the green truck, the red car

Gheg patterns used:
  - kam/ke/ka/kena/keni/kan + participle  (Gheg perfect, dominant in speech)
  - osht (Gheg) instead of është (Tosk) for "is"
  - Gheg participles end in -un (lodhun) instead of -ur (lodhur)
  - Gheg na for "we", çika for "girl"

Idempotent: skips entries whose .a already exists.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# Tuple = (emoji, english, gheg, phonetic)
NEW_SENTENCES = [
    # ── Past tense: SLEEP
    ("😴", "I slept",                 "Kam fjet",                "kahm fyet"),
    ("😴", "You slept",               "Ke fjet",                 "keh fyet"),
    ("😴", "He slept",                "Ka fjet",                 "kah fyet"),
    ("😴", "She slept",               "Ajo ka fjet",             "ah-yoh kah fyet"),
    ("😴", "We slept",                "Kena fjet",               "keh-nah fyet"),
    ("😴", "They slept",              "Kan fjet",                "kahn fyet"),
    ("😴", "The boy slept",           "Djali ka fjet",           "jah-lee kah fyet"),
    ("😴", "The girl slept",          "Çika ka fjet",            "chee-kah kah fyet"),
    ("😴", "The dad slept",           "Babi ka fjet",            "bah-bee kah fyet"),
    ("😴", "The mom slept",           "Nana ka fjet",            "nah-nah kah fyet"),
    ("🛏️", "The boy went to bed",     "Djali shkoi me fjet",     "jah-lee shkoy meh fyet"),
    ("🛏️", "The girl went to bed",    "Çika shkoi me fjet",      "chee-kah shkoy meh fyet"),
    ("🛏️", "I went to bed",           "Shkova me fjet",          "shkoh-vah meh fyet"),

    # ── Past tense: EAT / COOK / DRINK
    ("🍞", "I ate bread",             "Kam hangër bukë",         "kahm hahn-guhr boo-kuh"),
    ("🍴", "We ate",                  "Kena hangër",             "keh-nah hahn-guhr"),
    ("🍎", "The boy ate apples",      "Djali ka hangër molla",   "jah-lee kah hahn-guhr moh-lah"),
    ("🥚", "The mother cooked eggs",  "Nana ka gatu vezë",       "nah-nah kah gah-too veh-zuh"),
    ("🍳", "The mom fried eggs",      "Nana ka piek vezë",       "nah-nah kah pyek veh-zuh"),
    ("☕", "The dad drank coffee",     "Babi ka pi kafe",         "bah-bee kah pee kah-feh"),
    ("💧", "The girl drank water",    "Çika ka pi ujë",          "chee-kah kah pee oo-yuh"),
    ("🥛", "I drank milk",            "Kam pi qumësht",          "kahm pee choo-muhsht"),

    # ── Past tense: GO
    ("🏡", "I went home",             "Kam shku n'shpi",         "kahm shkoo n-shpee"),
    ("🏫", "We went to school",       "Kena shku n'shkollë",     "keh-nah shkoo n-shkoh-luh"),
    ("💼", "He went to work",         "Ka shku n'punë",          "kah shkoo n-poo-nuh"),
    ("🛒", "The boy went to the store","Djali ka shku n'dyqan",  "jah-lee kah shkoo n-due-chahn"),
    ("⛪", "The mother went to church","Nana ka shku n'kishë",   "nah-nah kah shkoo n-kee-shuh"),

    # ── Subject + IS + adjective (Gheg: osht)
    ("😢", "The boy is sad",          "Djali osht i mërzit",     "jah-lee osht ee muhr-zeet"),
    ("😢", "The girl is sad",         "Çika osht e mërzitun",    "chee-kah osht eh muhr-zee-toon"),
    ("😊", "The boy is happy",        "Djali osht i lumtur",     "jah-lee osht ee loom-toor"),
    ("😊", "The girl is happy",       "Çika osht e lumtur",      "chee-kah osht eh loom-toor"),
    ("😴", "The boy is tired",        "Djali osht i lodhun",     "jah-lee osht ee loh-thoon"),
    ("💪", "The dad is strong",       "Babi osht i fortë",       "bah-bee osht ee fohr-tuh"),
    ("😍", "The mother is beautiful", "Nana osht e bukur",       "nah-nah osht eh boo-koor"),

    # ── Noun + adjective (the X Y)
    ("🚛", "The green truck",         "Kamioni i gjelbër",       "kah-mee-oh-nee ee gyel-buhr"),
    ("🚗", "The red car",             "Kerri i kuq",             "keh-rree ee kooch"),
    ("🏠", "The big house",           "Shpia e madhe",           "shpee-ah eh mah-theh"),
    ("🐕", "The small dog",           "Qeni i vogël",            "cheh-nee ee voh-guhl"),
    ("🐎", "The white horse",         "Kali i bardhë",           "kah-lee ee bahr-thuh"),
    ("🐈", "The black cat",           "Macja e zezë",            "mah-tsyah eh zeh-zuh"),
    ("🌌", "The blue sky",            "Qielli i kaltër",         "chyeh-lee ee kahl-tuhr"),

    # ── Present-state with kam / jam
    ("🍴", "I am hungry",             "Kam un",                  "kahm oon"),
    ("😴", "I am tired",              "Jam i lodhun",            "yahm ee loh-thoon"),
    ("😊", "I am happy",              "Jam i lumtur",            "yahm ee loom-toor"),
]


def main():
    src = SRC.read_text()
    existing = set(re.findall(r'a:"([^"]+)"', src))

    keep = []
    skipped = []
    for e in NEW_SENTENCES:
        if e[2] in existing:
            skipped.append(e[1])
        else:
            keep.append(e)
    print(f"Adding {len(keep)} sentences ({len(skipped)} skipped as duplicates).")
    for s in skipped:
        print(f"  skip (dupe): {s}")

    def fmt(emoji, eng, gheg, pron):
        def esc(s): return s.replace('\\', '\\\\').replace('"', '\\"')
        return ('{e:"' + esc(emoji) + '",w:"' + esc(eng) + '",a:"' + esc(gheg)
                + '",p:"' + esc(pron) + '",cat:"Sentences",pos:"Sentence"}')

    if not keep:
        print("Nothing to add.")
        return

    marker = "const SENTENCES = ["
    start = src.index(marker)
    end = src.index("];", start)
    body = ",\n  " + ",\n  ".join(fmt(*e) for e in keep) + "\n"
    new_src = src[:end] + body + src[end:]
    SRC.write_text(new_src)
    print(f"File: {len(src):,} -> {len(new_src):,} bytes.")


if __name__ == "__main__":
    main()
