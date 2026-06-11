"""
Phase A2+A3: the glue words (pronouns, conjunctions, prepositions, adverbs)
and the meaningful core-concept gaps found in the frequency audit.

These are the words that turn a noun collection into a language. Gheg forms
throughout (i randë not i rëndë, i gjanë not i gjerë, pluhun not pluhur,
i kalbun not i kalbur, venë not verë-Tosk-spelling, etc).

Idempotent: skips .a values already present.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# (emoji, english, gheg, phonetic, cat, pos)
ENTRIES = [
    # ── Pronouns (the #1 gap: only 2 existed) — cat Conversation, pos Pronoun
    ("👤", "I",                  "unë",        "oo-nuh",        "Conversation", "Pronoun"),
    ("👉", "you (singular)",     "ti",         "tee",           "Conversation", "Pronoun"),
    ("👨", "he",                 "ai",         "ah-ee",         "Conversation", "Pronoun"),
    ("👥", "you all (plural)",   "ju",         "yoo",           "Conversation", "Pronoun"),
    ("👬", "they",               "ata",        "ah-tah",        "Conversation", "Pronoun"),
    ("🫵", "yours",              "i yti",      "ee ue-tee",     "Conversation", "Pronoun"),
    ("🙋", "mine",               "i jemi",     "ee yeh-mee",    "Conversation", "Pronoun"),

    # ── Conjunctions / connectors — pos Function Word
    ("➕", "and / also",         "edhe",       "eh-theh",       "Conversation", "Function Word"),
    ("🔗", "that / because",     "se",         "seh",           "Conversation", "Function Word"),
    ("❓", "if",                 "nëse",       "nuh-seh",       "Conversation", "Function Word"),
    ("⚖️", "or else / otherwise","ndryshe",    "ndrue-sheh",    "Conversation", "Function Word"),
    ("🆚", "than (comparison)",  "sesa",       "seh-sah",       "Conversation", "Function Word"),
    ("🤝", "like / as",          "sikur",      "see-koor",      "Conversation", "Function Word"),
    ("📌", "other / another",    "tjetër",     "tyeh-tuhr",     "Conversation", "Function Word"),
    ("🎯", "because",            "sepse",      "seh-pseh",      "Conversation", "Function Word"),

    # ── Prepositions — pos Function Word
    ("📍", "at / to (place)",    "te",         "teh",           "Conversation", "Function Word"),
    ("🤏", "near",               "afër",       "ah-fuhr",       "Conversation", "Function Word"),
    ("🛣", "far",                "larg",       "lahrg",         "Conversation", "Function Word"),
    ("↔️", "between",            "mes",        "mehs",          "Conversation", "Function Word"),
    ("🔄", "around",             "rreth",      "rreth",         "Conversation", "Function Word"),
    ("⏳", "until",              "deri",       "deh-ree",       "Conversation", "Function Word"),
    ("⬅️", "after",              "mbas",       "mbahs",         "Conversation", "Function Word"),
    ("🚫", "against",            "kundër",     "koon-duhr",     "Conversation", "Function Word"),

    # ── Adverbs — pos Adverb
    ("💯", "very / much",        "shumë",      "shoo-muh",      "Conversation", "Adverb"),
    ("⚡", "fast / quickly",     "shpejt",     "shpayt",        "Conversation", "Adverb"),
    ("🐢", "slowly",             "kadal",      "kah-dahl",      "Conversation", "Adverb"),
    ("👍", "well",               "mirë",       "mee-ruh",       "Conversation", "Adverb"),
    ("👎", "badly",              "keq",        "kech",          "Conversation", "Adverb"),
    ("♾", "always",             "gjithmonë",  "gyeeth-moh-nuh","Conversation", "Adverb"),
    ("🕐", "sometimes",          "nganjëherë", "ngah-nyuh-heh-ruh", "Conversation", "Adverb"),
    ("1️⃣", "only / alone",      "vetëm",      "veh-tuhm",      "Conversation", "Adverb"),
    ("🔁", "again",              "prap",       "prahp",         "Conversation", "Adverb"),
    ("🤝", "together",           "bashkë",     "bahsh-kuh",     "Conversation", "Adverb"),
    ("📍", "there",              "atje",       "aht-yeh",       "Conversation", "Adverb"),
    ("✅", "enough",             "mjaft",      "myahft",        "Conversation", "Adverb"),

    # ── Core concept gaps: nouns
    ("🐾", "animal",             "kafshë",     "kahf-shuh",     "Nature & Animals", "Noun"),
    ("🍎", "fruit",              "pemë",       "peh-muh",       "Food & Drink", "Noun"),
    ("🍷", "wine",               "venë",       "veh-nuh",       "Food & Drink", "Noun"),
    ("🍺", "beer",               "birrë",      "beer-ruh",      "Food & Drink", "Noun"),
    ("💨", "smoke",              "tym",        "tuem",          "Nature & Animals", "Noun"),
    ("🌫", "fog",                "mjegull",    "myeh-gool",     "Nature & Animals", "Noun"),
    ("🌪", "dust",               "pluhun",     "ploo-hoon",     "Nature & Animals", "Noun"),
    ("🪵", "stick",              "shkop",      "shkohp",        "Nature & Animals", "Noun"),
    ("🪢", "rope",               "litar",      "lee-tahr",      "Home & Things", "Noun"),
    ("🌱", "seed",               "farë",       "fah-ruh",       "Nature & Animals", "Noun"),
    ("🌳", "root",               "rranjë",     "rrah-nyuh",     "Nature & Animals", "Noun"),
    ("🪶", "tail",               "bisht",      "beesht",        "Nature & Animals", "Noun"),
    ("🦴", "fat (on meat)",      "dhjamë",     "thyah-muh",     "Food & Drink", "Noun"),

    # ── Core concept gaps: adjectives (Gheg forms)
    ("💧", "wet",                "i lagët",    "ee lah-guht",   "Describing", "Adjective"),
    ("🏜", "dry",                "i thatë",    "ee thah-tuh",   "Describing", "Adjective"),
    ("🏋️", "heavy",             "i randë",    "ee rahn-duh",   "Describing", "Adjective"),
    ("📏", "thick",              "i trashë",   "ee trah-shuh",  "Describing", "Adjective"),
    ("↔️", "wide",               "i gjanë",    "ee gyah-nuh",   "Describing", "Adjective"),
    ("🔪", "sharp",              "i mprehtë",  "ee mpreh-tuh",  "Describing", "Adjective"),
    ("🤢", "rotten",             "i kalbun",   "ee kahl-boon",  "Describing", "Adjective"),

    # ── Core concept gaps: verbs (me + Gheg participle)
    ("🦅", "to fly",             "me fluturu", "meh floo-too-roo", "Verbs", "Verb"),
    ("🏊", "to swim",            "me notu",    "meh noh-too",   "Verbs", "Verb"),
    ("🥊", "to fight",           "me u rrah",  "meh oo rrah",   "Verbs", "Verb"),
    ("👊", "to hit",             "me gjuajt",  "meh gyoo-ahyt", "Verbs", "Verb"),
    ("🔥", "to burn",            "me djeg",    "meh dyeg",      "Verbs", "Verb"),
    ("🦷", "to bite",            "me kafshu",  "meh kahf-shoo", "Verbs", "Verb"),
    ("💨", "to blow",            "me fry",     "meh frue",      "Verbs", "Verb"),
    ("🫁", "to breathe",         "me marr frymë", "meh mahrr frue-muh", "Verbs", "Verb"),
    ("⛏", "to dig",             "me gërmu",   "meh guhr-moo",  "Verbs", "Verb"),
    ("🪢", "to tie",             "me lidh",    "meh leeth",     "Verbs", "Verb"),
    ("🧹", "to wipe / sweep",    "me fshi",    "meh fshee",     "Verbs", "Verb"),
    ("🛣", "to travel",          "me udhëtu",  "meh oo-thuh-too", "Verbs", "Verb"),
]


def main():
    src = SRC.read_text()
    existing = set(re.findall(r'a:"([^"]+)"', src))

    keep, skipped = [], []
    for e in ENTRIES:
        (keep, skipped)[e[2] in existing].append(e)
    print(f"Adding {len(keep)} entries ({len(skipped)} already present).")
    for e in skipped:
        print(f"  skip: {e[2]} ({e[1]})")

    def fmt(emoji, eng, gheg, pron, cat, pos):
        def esc(s): return s.replace('\\', '\\\\').replace('"', '\\"')
        return ('{e:"' + esc(emoji) + '",w:"' + esc(eng) + '",a:"' + esc(gheg)
                + '",p:"' + esc(pron) + '",cat:"' + cat + '",pos:"' + pos + '"}')

    if keep:
        marker = "const WORDS = ["
        start = src.index(marker)
        end = src.index("];", start)
        body = ",\n  " + ",\n  ".join(fmt(*e) for e in keep) + "\n"
        src = src[:end] + body + src[end:]
        SRC.write_text(src)
    print(f"File now {len(src):,} bytes")


if __name__ == "__main__":
    main()
