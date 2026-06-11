"""
Phase A1: frequency tiers.

Adds tier:1|2|3 to every WORDS/PHRASES/SENTENCES entry:
  tier 1 — the ~140 highest-value items (glue words, core verbs, survival
           nouns, family, courtesy phrases). What a beginner drills first.
  tier 2 — everyday single words and short phrases.
  tier 3 — long phrases, full sentences, niche vocabulary.

Assignment: explicit tier-1 list by .a value; everything else by rule:
  WORDS                → 2
  PHRASES  ≤3 tokens   → 2, else 3
  SENTENCES ≤2 tokens  → 2 (the bare conjugations like "Kam fjet"), else 3

Idempotent: skips if entries already carry tier:.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

TIER1 = {
    # pronouns & determiners
    "unë","ti","ai","ajo","na","ju","ata","ky","jem","jonë","i yti","i jemi",
    # question words
    "çka","kush","ku","kur","pse","qysh","sa",
    # function words
    "me","pa","në","mbi","nën","prej","për","por","ose","se","nëse","edhe",
    "tjetër","krejt","veç","sikur","te","mes","deri","mbas","sepse",
    # adverbs
    "shumë","pak","mirë","keq","tash","sot","nesër","dje","këtu","atje",
    "gjithmonë","kurrë","nashta","vetëm","shpejt","kadal","prap","bashkë","mjaft",
    "afër","larg",
    # core verbs
    "me qenë","me pas","me shku","me ardh","me hangër","me pi","me fjet",
    "me fol","me dit","me dasht","me punu","me lujt","me mësu","me pyt",
    "me marr","me dhanë","me ble","me pri","me ndihmu","me ec","me kqyr",
    "me ndëgju","me kuptu","me thanë","me bo","me ra",
    # family & people
    "nanë","babë","vlla","motër","djalë","qikë","familje","gjysh","gjyshe",
    "fëmijë","burrë","grua","njeri","shok","mik",
    # survival nouns
    "ujë","bukë","shpi","derë","dhomë","ditë","natë","javë","muaj","vit",
    "orë","punë","kafe","qumësht","mish","vezë","djathë","kerri","rrugë",
    "katun","mal","diell","hanë","zjarm","gjuhë","emën","pare",
    # core adjectives
    "i madh","i vogël","i mirë","i keq","i ri","i bukur","i fortë",
    "i lodhun","i gjatë","i nxehtë","i ftohtë",
    # courtesy / core phrases
    "Po","Jo","Faliminderit","M'fal","Të lutem","Ju lutem","Tung",
    "Qysh je?","Jam mirë, faliminderit","S'di","Kuptoj","S'kuptoj",
    "S'ka problem","Mirëmëngjes","Natën e mirë","Mirë se vjen","Po ti?",
    "A flet shqip?","Të dua","Kam un","Kam etje","Sa kushton?",
}


def token_count(a):
    return len([t for t in re.split(r"\s+", a.strip()) if t and t != "/"])


def main():
    src = SRC.read_text()
    if re.search(r'pos:"[^"]*",tier:\d', src):
        print("Tiers already present — no-op.")
        return

    found_t1 = set()
    counts = {1: 0, 2: 0, 3: 0}

    def tier_for(a, array):
        if a in TIER1:
            found_t1.add(a)
            return 1
        n = token_count(a)
        if array == "WORDS":
            return 2
        if array == "PHRASES":
            return 2 if n <= 3 else 3
        return 2 if n <= 2 else 3  # SENTENCES

    def process_array(src, name):
        m = re.search(rf"const {name} = \[(.*?)\];\n", src, re.DOTALL)
        body = m.group(1)

        def add_tier(em):
            entry = em.group(0)
            am = re.search(r'a:"([^"]+)"', entry)
            t = tier_for(am.group(1), name) if am else 2
            counts[t] += 1
            return entry[:-1] + ',tier:' + str(t) + '}'

        new_body = re.sub(r'\{e:"[^}]*?pos:"[^"]*"\}', add_tier, body)
        return src.replace(body, new_body, 1)

    for name in ["WORDS", "PHRASES", "SENTENCES"]:
        src = process_array(src, name)

    SRC.write_text(src)
    print(f"Tier distribution: {counts}")
    missing_t1 = TIER1 - found_t1
    print(f"\nTier-1 list entries NOT found in data ({len(missing_t1)}):")
    for a in sorted(missing_t1):
        print(f"  ? {a}")


if __name__ == "__main__":
    main()
