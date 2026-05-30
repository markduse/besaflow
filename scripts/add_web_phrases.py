"""
Consolidated phrase batch from the 6 reference URLs Mark provided.

Sources used (in order of value):
  - omniglot.com Albanian-Gheg page          → highest priority, real Gheg
  - adventurousmiriam.com                    → great conversational/emotional
  - wikitravel.org Albanian phrasebook       → useful travel/emergency
  - others (ilanguages, corephrases, mylanguages) → mostly overlap

All entries here are Gheg-normalized:
  - omniglot's archaic diacritics (â, ã, ê, ô) collapsed to standard Gheg
  - Tosk forms converted where the Gheg equivalent is unambiguous
    (nuk→s', është→asht, vajzë→çikë, si→qysh, etc.)
  - Phonetics derived from the Gheg

Skips anything whose .a is already in WORDS / PHRASES / SENTENCES.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# (emoji, english, gheg, phonetic, category-target)
# category-target maps to one of: "Greetings & Small Talk", "Everyday Expressions",
# "Getting Around", "Food & Eating", "Emergency" (new), "Heritage & Honor"
PHRASES = [
    # ── Greetings & openings
    ("👋", "Welcome",                          "Mirë se vjen",                   "meeruh seh vyen",               "Greetings & Small Talk"),
    ("📞", "Hello (on the phone)",             "Alo",                            "ah-loh",                         "Greetings & Small Talk"),
    ("👋", "Hi (informal)",                    "Tjeta",                          "tyeh-tah",                       "Greetings & Small Talk"),
    ("👋", "Long time no see",                 "Ka shum koh që s'jemi pa",       "kah shoom koh chuh syeh-mee pah", "Greetings & Small Talk"),
    ("🤝", "Pleased to meet you",              "Gzu që të takova",               "gzoo chuh tuh tah-koh-vah",       "Greetings & Small Talk"),
    ("🌅", "Good evening",                     "Mirëmrama",                      "mee-ruh-mrah-mah",                "Greetings & Small Talk"),
    ("👋", "Goodbye",                          "Tung",                           "toong",                           "Greetings & Small Talk"),
    ("👋", "See you later",                    "Shihemi më vonë",                "shee-heh-mee muh voh-nuh",        "Greetings & Small Talk"),
    ("👋", "See you tomorrow",                 "Shihemi nesër",                  "shee-heh-mee neh-suhr",           "Greetings & Small Talk"),
    ("🛣️", "Have a good trip",                 "Udhëtim të mbarë",               "oo-thuh-teem tuh mbah-ruh",       "Greetings & Small Talk"),
    ("☀️", "Have a nice day",                  "Kalofsh ditë të mirë",           "kah-lohfsh dee-tuh tuh mee-ruh",  "Greetings & Small Talk"),
    ("🍽", "Bon appetit",                     "T'bëft mirë",                     "tbuhft mee-ruh",                  "Greetings & Small Talk"),
    ("🥂", "Cheers!",                          "Gzuar!",                         "gzoo-ahr",                        "Greetings & Small Talk"),
    ("🤞", "Good luck",                        "Paç fat",                        "pahch faht",                      "Greetings & Small Talk"),

    # ── Identity / conversation
    ("👤", "I'm fine, thanks",                 "Jam mirë, faleminderit",         "yahm mee-ruh fah-leh-meen-deh-reet", "Greetings & Small Talk"),
    ("🙋", "And you?",                         "Po ti?",                         "poh tee",                         "Greetings & Small Talk"),
    ("🌍", "Where are you from?",              "Prej ku je?",                    "prehj koo yeh",                   "Greetings & Small Talk"),
    ("🇺🇸", "I'm from America",                "Jam prej Amerikës",              "yahm prehj ah-meh-ree-kuhs",      "Greetings & Small Talk"),
    ("🇺🇸", "I'm American",                    "Jam amerikan",                   "yahm ah-meh-ree-kahn",            "Greetings & Small Talk"),
    ("🏠", "Where do you live?",               "Ku jeton?",                      "koo yeh-tohn",                    "Greetings & Small Talk"),
    ("🎓", "I'm a student",                    "Jam student",                    "yahm stoo-dent",                  "Greetings & Small Talk"),
    ("💼", "What do you do?",                  "Çfarë pune bën?",                "chfah-ruh poo-neh buhn",          "Greetings & Small Talk"),
    ("💍", "This is my wife",                  "Kjo asht gruja ime",             "kyoh ahsht groo-yah ee-meh",      "Greetings & Small Talk"),
    ("🤵", "This is my husband",               "Ky asht burri jem",              "kue ahsht boorree yem",           "Greetings & Small Talk"),
    ("👋", "It was nice meeting you",          "M'vjen mirë që u takum",         "myen mee-ruh chuh oo tah-koom",   "Greetings & Small Talk"),

    # ── Communication / understanding
    ("🗣", "Do you speak English?",           "A flet anglisht?",                "ah fleht ahn-gleesht",            "Greetings & Small Talk"),
    ("🗣", "Do you speak Albanian?",          "A flet shqip?",                   "ah fleht shcheep",                "Greetings & Small Talk"),
    ("🤏", "Yes, a little",                   "Po, pak",                         "poh pahk",                        "Greetings & Small Talk"),
    ("🐢", "Please speak slower",             "Mund të flasësh ma kadal?",       "moond tuh flah-suhsh mah kah-dahl", "Greetings & Small Talk"),
    ("🔁", "Please say that again",           "Mund ta përsëritësh?",            "moond tah puhr-suh-ree-tuhsh",     "Greetings & Small Talk"),
    ("✍️", "Please write it down",            "T'lutna, shkruje",                "tloot-nah shkroo-yeh",             "Greetings & Small Talk"),
    ("🤷", "I don't know",                    "S'di",                            "sdee",                            "Greetings & Small Talk"),
    ("✅", "I understand",                    "Kuptoj",                          "koop-toy",                        "Greetings & Small Talk"),

    # ── Politeness
    ("🙏", "Thank you very much",             "Shum faliminderit",                "shoom fah-lee-meen-deh-reet",     "Greetings & Small Talk"),
    ("🙏", "You're welcome",                  "S'ka përse",                      "skah puhr-seh",                   "Greetings & Small Talk"),
    ("🙏", "Excuse me",                       "M'fal",                           "mfahl",                           "Greetings & Small Talk"),
    ("🙏", "Please (informal)",               "Të lutem",                        "tuh loo-tem",                     "Greetings & Small Talk"),
    ("🙏", "Please (formal)",                 "Ju lutem",                        "yoo loo-tem",                     "Greetings & Small Talk"),
    ("👍", "No problem",                      "S'ka problem",                    "skah proh-blem",                  "Greetings & Small Talk"),
    ("🙋", "Don't worry",                     "Mos u bëj merak",                 "mohs oo buy meh-rahk",            "Greetings & Small Talk"),
    ("🙏", "I agree",                         "Jam dakord",                      "yahm dah-kohrd",                  "Greetings & Small Talk"),

    # ── Emotional / kind
    ("❤️", "I love you",                      "Të dua",                          "tuh doo-ah",                      "Greetings & Small Talk"),
    ("💔", "I miss you",                      "Po m'mungon",                     "poh mmoon-gohn",                  "Greetings & Small Talk"),
    ("❤️", "I missed you",                    "M'ka marrë malli për ty",         "mkah mahr-ruh mahl-lee puhr tue", "Heritage & Honor"),
    ("🙂", "Don't worry, I'm okay",           "S'ka problem, jam mirë",          "skah proh-blem yahm mee-ruh",     "Greetings & Small Talk"),
    ("😂", "I'm just kidding",                "Po bëj shaka",                    "poh buy shah-kah",                "Greetings & Small Talk"),
    ("😐", "I'm serious",                     "E kam seriozisht",                "eh kahm seh-ree-oh-zeesht",       "Greetings & Small Talk"),
    ("💖", "You're very kind",                "Je shumë zemërmirë",              "yeh shoo-muh zeh-muhr-mee-ruh",   "Greetings & Small Talk"),
    ("🥳", "Congratulations!",                "Urime!",                          "oo-ree-meh",                      "Greetings & Small Talk"),

    # ── Practical asks
    ("💰", "How much is it?",                 "Sa kushton?",                     "sah koosh-tohn",                  "Everyday Expressions"),
    ("👀", "I'm just looking",                "Vetëm po shikoj",                 "veh-tuhm poh shee-koy",           "Everyday Expressions"),
    ("💸", "That's too expensive",            "Asht shumë e shtrenjt",           "ahsht shoo-muh eh shtrent",       "Everyday Expressions"),
    ("💲", "Cheap",                           "I lirë",                          "ee lee-ruh",                      "Everyday Expressions"),
    ("💲", "Expensive",                       "I shtrenjt",                      "ee shtrent",                      "Everyday Expressions"),
    ("⏰", "What time is it?",                "Sa asht ora?",                    "sah ahsht oh-rah",                "Everyday Expressions"),
    ("💧", "I'm thirsty",                     "Jam i ujshëm",                    "yahm ee ooy-shuhm",               "Everyday Expressions"),

    # ── Getting Around
    ("📍", "Where is...?",                    "Ku asht...?",                     "koo ahsht",                       "Getting Around"),
    ("🚶", "Go straight",                     "Shko drejt",                      "shkoh drayt",                     "Getting Around"),
    ("👈", "Turn left",                       "Kthehu majtas",                   "kteh-hoo mahy-tahs",              "Getting Around"),
    ("👉", "Turn right",                      "Kthehu djathtas",                 "kteh-hoo jahth-tahs",             "Getting Around"),
    ("🆘", "I'm lost",                        "Kam humbur rrugën",               "kahm hoom-boor rroo-guhn",        "Getting Around"),
    ("🗺️", "Can you show me?",                "A mun me m'tregu?",               "ah moon meh mtreh-goo",           "Getting Around"),
    ("📏", "Is it far from here?",            "A asht larg që këtu?",            "ah ahsht lahrg chuh kuh-too",     "Getting Around"),
    ("📏", "Is it close?",                    "A asht këtu afër?",               "ah ahsht kuh-too ah-fuhr",        "Getting Around"),

    # ── Emergency (new category)
    ("🆘", "Help!",                            "Ndihmë!",                        "ndee-muh",                        "Emergency"),
    ("🔥", "Fire!",                            "Zjarm!",                         "zyahrm",                          "Emergency"),
    ("✋", "Stop!",                            "Nalu!",                          "nah-loo",                         "Emergency"),
    ("👮", "Call the police!",                 "Thirreni policin!",              "theer-reh-nee poh-lee-tseen",     "Emergency"),
    ("⛔", "Go away!",                         "Shko!",                          "shkoh",                           "Emergency"),
    ("🙏", "Leave me alone",                  "Lejëm rahat",                     "leh-yuhm rah-haht",               "Emergency"),
    ("🦹", "Thief!",                           "Hajdut!",                        "hahy-doot",                       "Emergency"),
    ("🚑", "I'm sick",                        "Jam i sëmurë",                    "yahm ee suh-moo-ruh",             "Emergency"),
    ("🩺", "I need a doctor",                 "M'duhet një mjek",                "mdoo-het nyuh myehk",             "Emergency"),
    ("👜", "I lost my bag",                   "Kam humbur çantën",               "kahm hoom-boor chahn-tuhn",       "Emergency"),
    ("👁", "Watch out!",                       "Kujdes!",                        "kooy-des",                        "Emergency"),
    ("🚨", "It's urgent",                     "Asht urgjente",                   "ahsht oor-jen-teh",               "Emergency"),

    # ── Question words
    ("❓", "What?",                            "Çka?",                            "chkah",                           "Everyday Expressions"),
    ("❓", "Why?",                             "Pse?",                            "pseh",                            "Everyday Expressions"),
    ("❓", "When?",                            "Kur?",                            "koor",                            "Everyday Expressions"),
    ("❓", "Where?",                           "Ku?",                             "koo",                             "Everyday Expressions"),
    ("❓", "Who?",                             "Kush?",                           "koosh",                           "Everyday Expressions"),
    ("❓", "How?",                             "Qysh?",                          "chuesh",                          "Everyday Expressions"),
    ("❓", "Really?",                          "Vërtet?",                         "vuhr-teht",                       "Everyday Expressions"),
    ("👀", "Look!",                            "Shiko!",                         "shee-koh",                        "Everyday Expressions"),
    ("🤔", "What's new?",                     "Ndonjë të re?",                  "ndoh-nyuh tuh reh",               "Everyday Expressions"),
    ("🤷", "Nothing new",                     "Asgjë e re",                     "ahs-gyuh eh reh",                 "Everyday Expressions"),

    # ── Time (Gheg)
    ("🕐", "Now",                              "Tash",                           "tahsh",                           "Time & Function Words"),
    ("🌞", "Today (Gheg)",                    "Sot",                             "soht",                            "Time & Function Words"),
    ("🌅", "Tomorrow (Gheg)",                 "Nesër",                          "neh-suhr",                        "Time & Function Words"),
    ("🌆", "Yesterday (Gheg)",                "Dje",                            "jeh",                             "Time & Function Words"),

    # ── Weather
    ("🥶", "It's cold",                       "Asht ftohtë",                    "ahsht ftoh-tuh",                  "Everyday Expressions"),
    ("🥵", "It's hot",                        "Asht vapë",                      "ahsht vah-puh",                   "Everyday Expressions"),
    ("🌧", "It's raining",                    "Po bjen shi",                    "poh byen shee",                   "Everyday Expressions"),

    # ── Food
    ("🍽", "A table for two",                 "Një tavolinë për dy",             "nyuh tah-voh-lee-nuh puhr due",   "Food & Eating"),
    ("🍽", "The check please",                "Faturën, ju lutem",               "fah-too-ruhn yoo loo-tem",        "Food & Eating"),
    ("🥩", "I don't eat pork",                "S'ha mish derri",                 "shah meesh dehr-ree",             "Food & Eating"),
    ("🍷", "Cheers (with drinks)!",           "N'shëndet!",                      "nshuhn-det",                      "Food & Eating"),

    # ── Heritage / cultural
    ("🦅", "Albania is beautiful",            "Shqipnia asht e bukur",          "shcheep-nyah ahsht eh boo-koor",  "Heritage & Honor"),
    ("🇦🇱", "I'm trying to learn Albanian",   "Po mundohem me mësu shqip",      "poh moon-doh-hem meh muh-soo shcheep", "Heritage & Honor"),
    ("🎓", "Can I practice with you?",        "A muj me praktiku me ty?",       "ah mooy meh prahk-tee-koo meh tue", "Heritage & Honor"),
]


def main():
    src = SRC.read_text()
    existing = set(re.findall(r'a:"([^"]+)"', src))

    keep = []
    skipped = []
    for entry in PHRASES:
        if entry[2] in existing:
            skipped.append(entry[1])
        else:
            keep.append(entry)

    print(f"Adding {len(keep)} new phrases ({len(skipped)} dupes skipped).")

    def fmt(emoji, eng, gheg, pron, cat):
        def esc(s): return s.replace('\\', '\\\\').replace('"', '\\"')
        return ('{e:"' + esc(emoji) + '",w:"' + esc(eng) + '",a:"' + esc(gheg)
                + '",p:"' + esc(pron) + '",cat:"' + cat + '",pos:"Phrase"}')

    if not keep:
        print("Nothing to add.")
        return

    marker = "const PHRASES = ["
    start = src.index(marker)
    end = src.index("];", start)
    body = ",\n  " + ",\n  ".join(fmt(*e) for e in keep) + "\n"
    new_src = src[:end] + body + src[end:]
    SRC.write_text(new_src)
    print(f"File: {len(src):,} -> {len(new_src):,} bytes")

    # Summary by category
    from collections import Counter
    cats = Counter(e[4] for e in keep)
    print("\nBy category:")
    for c, n in cats.most_common():
        print(f"  +{n:3d}  {c}")


if __name__ == "__main__":
    main()
