"""
Batch 1: practical phrases + holidays + house items.

Hand-curated to use Gheg forms (asht not është, shpi not shtëpi, n' contractions,
emni not emri). User can refine via the Report-word button.

Idempotent: skips entries whose .a already exists.
"""
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# -------- New PHRASES (cat='Greetings & Small Talk') --------
NEW_PHRASES = [
    # Identity / introductions
    ("👤", "What is your name?",      "Qysh quhesh? / Si t'thojnë?",  "chuesh kueshesh"),
    ("👤", "Who are you?",            "Kush je?",                      "koosh yeh"),
    ("👤", "Who is this?",            "Kush asht ky/kjo?",             "koosh ahsht kue/kyoh"),
    ("👤", "My dad's name is...",     "Babi jem quhet...",             "bahbee yem chooheht"),
    ("👤", "My mom's name is...",     "Nana ime quhet...",             "nahnah eemeh chooheht"),
    ("🤝", "Nice to meet you",        "M'vjen mirë t'a takoj",         "myen meeruh tah tahkohj"),
    ("📍", "Where do you live?",      "Ku jeton? / Ku rri?",           "koo yehtohn"),
    ("📍", "I live in America",       "Jetoj n'Amerikë",               "yehtohj nahmehreekuh"),
    # Family clarification
    ("👫", "Are we cousins?",         "A jena kushrij?",               "ah yehnah kooshreey"),
    ("👨‍👦", "Are you my cousin?",     "A je kushriri jem?",            "ah yeh kooshreeree yem"),
    ("👨", "Whose son are you?",      "Djali i kujt je?",              "jahlee ee kooyt yeh"),
    ("👧", "Whose daughter are you?", "Çika e kujt je?",               "chee-kah eh kooyt yeh"),
    # Practical asks
    ("🚻", "Can I use the bathroom?", "A muj me shku n'banjë?",         "ah mooy meh shkoo nbahnyuh"),
    ("🚻", "Where is the bathroom?",  "Ku asht banja?",                "koo ahsht bahnyah"),
    ("🍳", "Where is the kitchen?",   "Ku asht kuzhina?",              "koo ahsht koozheenah"),
    ("🍴", "I'm hungry",              "Kam un",                        "kahm oon"),
    ("💧", "I'm thirsty",             "Kam etje",                      "kahm ehtyeh"),
    ("💧", "Can I have water?",       "M'jep pak ujë?",                "myep pahk ooyuh"),
    # Communication
    ("🔁", "Can you repeat?",         "A mun e thua prap?",            "ah moon eh thoo-ah prahp"),
    ("🗣", "What did you say?",       "Çka the?",                      "chkah theh"),
    ("⏰", "Sorry I'm late",          "M'fal, po jam vonë",            "mfahl poh yahm vohnuh"),
    ("🗣", "I don't speak well",      "S'flas mirë",                   "sflahs meeruh"),
]

# -------- New WORDS — Holidays (cat='Holidays', pos='Noun') --------
NEW_HOLIDAYS = [
    ("🎉", "holiday",          "festë",                  "fehstuh"),
    ("🎊", "celebration",      "festim",                 "fehsteem"),
    ("🪗", "party",            "ahengu",                 "ah-hehn-goo"),
    ("📅", "anniversary",      "përvjetori",             "puhrvyehtohree"),
    ("🎆", "New Year",         "Viti i Ri",              "veetee ee ree"),
    ("🎄", "Christmas",        "Krishtlindja",           "kreesht-leenjah"),
    ("🐣", "Easter",           "Pashka",                 "pahshkah"),
    ("🇦🇱", "Independence Day", "Dita e Pavarësisë",      "deetah eh pahvahruhseesuh"),
    ("🦅", "Flag Day",         "Dita e Flamurit",        "deetah eh flahmooreet"),
    ("🌙", "Bajram (Eid)",     "Bajrami",                "bahy-rah-mee"),
    ("👩", "Mother's Day",     "Dita e Nanës",           "deetah eh nahnuhs"),
    ("👨", "Father's Day",     "Dita e Babës",           "deetah eh bahbuhs"),
    ("⚰️", "funeral",          "morti / varrimi",        "mohrtee"),
    ("🤝", "guest",            "mysafir / mik",          "muesahfeer"),
]

# -------- New WORDS — Household expansion (cat='Household & Objects', pos='Noun') --------
NEW_HOUSEHOLD = [
    ("⬆️", "ceiling",         "tavan",                  "tahvahn"),
    ("🪜", "stairs",          "shkallët",               "shkah-luht"),
    ("🏚", "basement",        "bodrum",                 "bohdroom"),
    ("🪟", "balcony",         "ballkon",                "bahl-kohn"),
    ("🌳", "yard",            "oborr",                  "oh-bohrr"),
    ("🌷", "garden",          "kopsht",                 "kohpsht"),
    ("🏠", "roof",            "kulm / çati",            "koolm"),
    ("🍽️", "dining room",     "dhomë ngrënie",          "thohmuh ngruhneeyeh"),
    ("🧊", "freezer",         "frizer",                 "freezer"),
    ("🔥", "stove",           "shporet",                "shpohreht"),
    ("🌊", "microwave",       "mikrovala",              "meekrohvahlah"),
    ("🍽️", "dishwasher",      "lavastovilje",           "lahvahstohveelyeh"),
    ("🧺", "washing machine", "lavatriçe",              "lahvah-tree-cheh"),
    ("🌬", "dryer",           "tharës",                 "thahruhs"),
    ("🟫", "rug",             "qilim",                  "cheeleem"),
    ("🪟", "curtain",         "perde",                  "pehrdeh"),
    ("🗄", "drawer",          "sirtar",                 "seer-tahr"),
    ("📚", "shelf",           "raft",                   "rahft"),
    ("🚪", "cabinet",         "dollap",                 "dohlahp"),
    ("👚", "closet",          "dollap rrobash",         "dohlahp rohbahsh"),
    ("🔒", "lock",            "bravë",                  "brahvuh"),
    ("🚿", "shower",          "dush",                   "doosh"),
    ("🚽", "toilet",          "tualet",                 "tooahleht"),
    ("🪥", "toothbrush",      "furçë dhambësh",         "foor-chuh thahmbuhsh"),
    ("🧴", "toothpaste",      "pastë dhambësh",         "pahstuh thahmbuhsh"),
    ("🧹", "broom",           "fshesë",                 "fshehsuh"),
    ("🗑", "trash can",       "kovë plehrash",          "kohvuh plehrahsh"),
]


def main():
    src = SRC.read_text()

    def extract_a(name):
        m = re.search(rf"const {name} = \[(.*?)\];", src, re.DOTALL)
        return set(re.findall(r'a:"([^"]+)"', m.group(1)))

    existing = extract_a("WORDS") | extract_a("PHRASES") | extract_a("SENTENCES")

    def filter_new(entries):
        keep = []
        skipped = []
        for e in entries:
            if e[2] in existing:
                skipped.append(e[1])
            else:
                keep.append(e)
        return keep, skipped

    phr, phr_skip = filter_new(NEW_PHRASES)
    hol, hol_skip = filter_new(NEW_HOLIDAYS)
    hh,  hh_skip  = filter_new(NEW_HOUSEHOLD)

    print(f"PHRASES (Greetings & Small Talk): +{len(phr)} new, {len(phr_skip)} skipped")
    for s in phr_skip: print(f"  skipped (dupe): {s}")
    print(f"WORDS    (Holidays NEW cat):     +{len(hol)} new, {len(hol_skip)} skipped")
    for s in hol_skip: print(f"  skipped (dupe): {s}")
    print(f"WORDS    (Household & Objects):  +{len(hh)} new, {len(hh_skip)} skipped")
    for s in hh_skip: print(f"  skipped (dupe): {s}")

    def fmt(e, cat, pos):
        emoji, eng, gheg, pron = e
        def esc(s): return s.replace('\\','\\\\').replace('"','\\"')
        return '{e:"'+esc(emoji)+'",w:"'+esc(eng)+'",a:"'+esc(gheg)+'",p:"'+esc(pron)+'",cat:"'+cat+'",pos:"'+pos+'"}'

    def append_array(arr, entries_with_meta):
        if not entries_with_meta:
            return arr
        marker = f"const {arr} = ["
        start = src_holder[0].index(marker)
        end = src_holder[0].index("];", start)
        block = ",\n  " + ",\n  ".join(fmt(e, cat, pos) for e, cat, pos in entries_with_meta) + "\n"
        src_holder[0] = src_holder[0][:end] + block + src_holder[0][end:]

    src_holder = [src]

    phrase_entries = [(e, "Greetings & Small Talk", "Phrase") for e in phr]
    holiday_entries = [(e, "Holidays", "Noun") for e in hol]
    household_entries = [(e, "Household & Objects", "Noun") for e in hh]

    append_array("PHRASES", phrase_entries)
    append_array("WORDS", holiday_entries + household_entries)

    SRC.write_text(src_holder[0])
    print(f"\nFile size: {len(src):,} -> {len(src_holder[0]):,} bytes")


if __name__ == "__main__":
    main()
