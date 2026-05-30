"""
Conversational question/answer pairs in Gheg.

User: "lets also have responses to conversation - like how are you and i
am good. hows your father? he is doing good. etc"

Each pair adds BOTH the question and a natural response as separate
PHRASES entries. They sit next to each other in the array so they're
likely to land near each other in shuffled flashcard sessions, and they
share cat="Conversation" so picking that category pulls both.

Uses informal singular Gheg ("ti" forms) — the family-and-friends register.
Gheg patterns: 'qysh' for 'how', 'asht' (not është), 'n'shpi' / 'n'punë'
contractions, '-um' / '-ume' for participles, 's'' for negation.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# (emoji, english_with_marker, gheg, phonetic)
# Use "→" markers in the English so it's clear which is Q vs A even in a shuffle.
PAIRS = [
    # ── Wellbeing
    ("🙋", "How are you?",                       "Qysh je?",                       "chuesh yeh"),
    ("🙂", "→ I'm good, thanks",                 "Jam mirë, faliminderit",         "yahm mee-ruh fah-lee-meen-deh-reet"),
    ("🙋", "How are you doing? (Gheg)",          "Si kalon?",                      "see kah-lohn"),
    ("🙂", "→ I'm doing well",                   "Po kaloj mirë",                  "poh kah-loy mee-ruh"),
    ("📅", "How was your day?",                  "Si t'shkoi dita?",               "see tshkoy dee-tah"),
    ("🙂", "→ It went well",                     "M'shkoi mirë",                   "mshkoy mee-ruh"),
    ("😴", "Are you tired?",                     "A je i lodhun?",                 "ah yeh ee loh-thoon"),
    ("😴", "→ Yes, a little",                    "Po, pak",                        "poh pahk"),
    ("💪", "→ No, I'm fine",                     "Jo, jam mirë",                   "yoh yahm mee-ruh"),

    # ── Family check-ins
    ("👨", "How is your father?",                "Qysh asht babi yt?",             "chuesh ahsht bah-bee uet"),
    ("🙂", "→ He is doing well",                 "Asht mirë",                      "ahsht mee-ruh"),
    ("👩", "How is your mother?",                "Qysh asht nana jote?",           "chuesh ahsht nah-nah yoh-teh"),
    ("🙂", "→ She is doing well",                "Asht mirë",                      "ahsht mee-ruh"),
    ("👨‍👩‍👧", "How is your family?",                 "Qysh asht familja jote?",        "chuesh ahsht fah-meel-yah yoh-teh"),
    ("🙂", "→ Everyone is well",                 "Krejt janë mirë",                "krayt yah-nuh mee-ruh"),
    ("👨‍👦", "Do you have brothers?",             "A ke vllazën?",                  "ah keh vlah-zuhn"),
    ("👬", "→ Yes, two brothers",                "Po, dy vllazën",                 "poh due vlah-zuhn"),
    ("👧", "Do you have sisters?",               "A ke motra?",                    "ah keh moht-rah"),
    ("👭", "→ Yes, one sister",                  "Po, një motër",                  "poh nyuh moh-tuhr"),
    ("💍", "Are you married?",                   "A je i martum?",                 "ah yeh ee mahr-toom"),
    ("💍", "→ Yes, I'm married",                 "Po, jam i martum",               "poh yahm ee mahr-toom"),
    ("🧑", "→ No, I'm single",                   "Jo, jam beqar",                  "yoh yahm beh-chahr"),
    ("👶", "Do you have children?",              "A ke fëmijë?",                   "ah keh fuh-mee-yuh"),
    ("👶", "→ Yes, two children",                "Po, dy fëmijë",                  "poh due fuh-mee-yuh"),
    ("🤷", "→ No, not yet",                      "Jo, jo akoma",                   "yoh yoh ah-koh-mah"),
    ("🏡", "How is everyone at home?",           "Qysh janë krejt n'shpi?",        "chuesh yah-nuh krayt nshpee"),
    ("🙂", "→ Everyone is well at home",         "Krejt janë mirë n'shpi",         "krayt yah-nuh mee-ruh nshpee"),

    # ── Daily check-ins
    ("📍", "Where are you?",                     "Ku je?",                         "koo yeh"),
    ("🏡", "→ I'm at home",                      "Jam n'shpi",                     "yahm nshpee"),
    ("💼", "→ I'm at work",                      "Jam n'punë",                     "yahm npoo-nuh"),
    ("➡️", "Where are you going?",               "Ku po shkon?",                   "koo poh shkohn"),
    ("🏡", "→ I'm going home",                   "Po shkoj n'shpi",                "poh shkoy nshpee"),
    ("💼", "→ I'm going to work",                "Po shkoj n'punë",                "poh shkoy npoo-nuh"),
    ("🛒", "→ I'm going to the store",           "Po shkoj n'dyqan",               "poh shkoy ndue-chahn"),

    # ── Food / wellbeing
    ("🍴", "Are you hungry?",                    "A je i ujshëm?",                 "ah yeh ee ooy-shuhm"),
    ("🍴", "→ Yes, very",                        "Po, shumë",                      "poh shoo-muh"),
    ("🙅", "→ No, thanks",                       "Jo, faliminderit",               "yoh fah-lee-meen-deh-reet"),
    ("🍞", "Did you eat?",                       "A ke hangër?",                   "ah keh hahn-guhr"),
    ("✅", "→ Yes, I ate",                       "Po, kam hangër",                 "poh kahm hahn-guhr"),
    ("⏳", "→ No, not yet",                      "Jo, jo akoma",                   "yoh yoh ah-koh-mah"),
    ("☕", "Do you want coffee?",                "A do kafe?",                     "ah doh kah-feh"),
    ("☕", "→ Yes, please",                      "Po, të lutem",                   "poh tuh loo-tem"),

    # ── Plans / yes-no
    ("➡️", "Are you coming?",                    "A po vjen?",                     "ah poh vyen"),
    ("✅", "→ Yes, I'm coming",                  "Po, po vij",                     "poh poh veey"),
    ("❓", "Do you understand?",                 "A kupton?",                      "ah koop-tohn"),
    ("✅", "→ Yes, I understand",                "Po, kuptoj",                     "poh koop-toy"),
    ("❌", "→ No, I don't understand",           "Jo, s'kuptoj",                   "yoh skoop-toy"),
    ("🆘", "Can you help me?",                   "A muj me m'ndihmu?",             "ah mooy meh mndee-mooh"),
    ("🤝", "→ Yes, of course",                   "Po, sigurisht",                  "poh see-goo-reesht"),

    # ── Time
    ("⏰", "What time is it?",                   "Sa asht ora?",                   "sah ahsht oh-rah"),
    ("⏰", "→ It's three o'clock",               "Asht tre",                       "ahsht treh"),
]


def main():
    src = SRC.read_text()
    existing = set(re.findall(r'a:"([^"]+)"', src))

    keep = []
    skipped = []
    for e in PAIRS:
        if e[2] in existing:
            skipped.append(e[1])
        else:
            keep.append(e)
    print(f"Adding {len(keep)} new pair entries ({len(skipped)} dupes skipped).")
    for s in skipped:
        print(f"  skip (dupe): {s}")

    def fmt(emoji, eng, gheg, pron):
        def esc(s): return s.replace('\\', '\\\\').replace('"', '\\"')
        return ('{e:"' + esc(emoji) + '",w:"' + esc(eng) + '",a:"' + esc(gheg)
                + '",p:"' + esc(pron) + '",cat:"Conversation",pos:"Phrase"}')

    if not keep:
        print("Nothing to add.")
        return

    marker = "const PHRASES = ["
    start = src.index(marker)
    end = src.index("];", start)
    body = ",\n  " + ",\n  ".join(fmt(*e) for e in keep) + "\n"
    new_src = src[:end] + body + src[end:]
    SRC.write_text(new_src)
    print(f"\nFile: {len(src):,} -> {len(new_src):,} bytes")


if __name__ == "__main__":
    main()
