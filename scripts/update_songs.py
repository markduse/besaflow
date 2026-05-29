"""
Replace SONGS data with the 4 user-curated tracks (Lumi Une, Vajzë Me Zemër Guri,
Jem Ilira, Lum Kush Rrin Me Burra T'mir). All Gheg lyrics are user-verified;
English translations and word-by-word breakdowns are Claude's best attempt and
should be flagged via the in-app Report button if anything is off.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# Format for snippet:
#   gheg     — user-verified Albanian lines (1-2 lines per snippet)
#   english  — natural English translation
#   phonetic — readable English-sound approximation
#   notes    — cultural / contextual line (italic on the back)
#   breakdown — list of (gheg_chunk, english_chunk) pairs shown word-by-word
#   startAt / duration — 0/0 means play the whole song from the beginning;
#     time offsets can be added later once Mark scrubs through each track.

SONGS = [
    # ─────────────────────────────────────────────────────────────
    {
        "id": "lumi-une",
        "title": "Lumi Une",
        "artist": "Irkenc Hyka",
        "region": "Northern Albania / Kosovë (wedding)",
        "cover": "💒",
        "audio": "audio/songs/lumi-une.mp3",
        "about": "Wedding song. The bride's family sings 'O e lumja unë' (oh, blessed am I — feminine), and the groom's side answers 'O i lumi unë' (masculine). Celebrates the new bride being raised by her mother and welcomed into the new family.",
        "snippets": [
            {
                "gheg": "O e lumja unë / Ç'paska rritur nona",
                "english": "Oh, blessed am I (a daughter) / What [a daughter] mother has raised",
                "phonetic": "oh eh loom-yah oo-nuh / chpah-skah rree-toor noh-nah",
                "notes": "Bride's refrain — 'e lumja' is feminine; the masculine form is sung later",
                "breakdown": [
                    ("O", "oh"),
                    ("e lumja", "the blessed (feminine)"),
                    ("unë", "me / I"),
                    ("Ç'paska rritur", "what [a daughter] has raised"),
                    ("nona", "mother (Gheg = nana)"),
                ],
            },
            {
                "gheg": "Shtatin si selvie / Kangën po ja knojna",
                "english": "Stature like a cypress / We are singing her song",
                "phonetic": "shtah-teen see sel-vee-eh / kahn-guhn poh yah knoy-nah",
                "notes": "Selvie = cypress tree — a classic Albanian compliment for a tall, elegant woman",
                "breakdown": [
                    ("Shtatin", "the stature / posture"),
                    ("si selvie", "like a cypress"),
                    ("Kangën", "the song"),
                    ("po ja knojna", "we are singing it to her (Gheg knojna = këndojmë)"),
                ],
            },
            {
                "gheg": "Po vjen nusja gjithë lezet / Për mu paska ken kismet",
                "english": "Here comes the bride, full of grace / She was meant for me by fate",
                "phonetic": "poh vyen noo-syah gyee-thuh leh-zet / puhr moo pah-skah ken kee-smet",
                "notes": "Kismet = fate / destiny (from Turkish); deeply rooted in Balkan vocabulary",
                "breakdown": [
                    ("Po vjen", "is coming"),
                    ("nusja", "the bride"),
                    ("gjithë lezet", "full of grace / charm"),
                    ("Për mu", "for me"),
                    ("paska ken", "she has been (turns out to be)"),
                    ("kismet", "fate / destiny"),
                ],
            },
            {
                "gheg": "E bukur si zanë e malit / Kom me majt unë me kimet",
                "english": "Beautiful as a mountain fairy / I will hold her in high regard",
                "phonetic": "eh boo-koor see zah-nuh eh mah-leet / kohm meh mahyt oo-nuh meh kee-met",
                "notes": "Zana = mountain fairy from Albanian mythology, protector of the heights",
                "breakdown": [
                    ("E bukur", "beautiful"),
                    ("si zanë e malit", "like a fairy of the mountain"),
                    ("Kom me majt", "I will keep / hold (Gheg future)"),
                    ("unë", "I"),
                    ("me kimet", "with esteem / value"),
                ],
            },
            {
                "gheg": "Kom me dasht si syt e ballit",
                "english": "I will love her like the eyes of my forehead",
                "phonetic": "kohm meh dahsht see suet eh bah-leet",
                "notes": "Idiom: loving someone like 'the eyes of your forehead' is the deepest devotion in Albanian",
                "breakdown": [
                    ("Kom me dasht", "I will love"),
                    ("si syt", "like the eyes"),
                    ("e ballit", "of the forehead"),
                ],
            },
            {
                "gheg": "O i lumi unë / Ç'paska rritur nona",
                "english": "Oh, blessed am I (a son) / What [a son] mother has raised",
                "phonetic": "oh ee loo-mee oo-nuh / chpah-skah rree-toor noh-nah",
                "notes": "Groom's refrain — masculine 'i lumi' answering the bride's 'e lumja'",
                "breakdown": [
                    ("O", "oh"),
                    ("i lumi", "the blessed (masculine)"),
                    ("unë", "me / I"),
                    ("Ç'paska rritur", "what [a son] has raised"),
                    ("nona", "mother"),
                ],
            },
            {
                "gheg": "Hedhim valle me tupan / Le t'na nijn krejt anë e mbanë",
                "english": "We throw the valle with the drum / Let everyone hear us from every side",
                "phonetic": "heh-theem vahl-leh meh too-pahn / leh tnah neeyn krayt ah-nuh eh mbah-nuh",
                "notes": "Tupan = the big drum that anchors Albanian wedding music",
                "breakdown": [
                    ("Hedhim", "we throw / dance"),
                    ("valle", "the round dance"),
                    ("me tupan", "with the drum"),
                    ("Le t'na nijn", "let them hear us (Gheg)"),
                    ("krejt", "all / completely"),
                    ("anë e mbanë", "from every side"),
                ],
            },
            {
                "gheg": "Kena dasëm, dasëm t'madhe / Për me gzu sot babë e nanë",
                "english": "We have a wedding, a great wedding / To make father and mother joyful today",
                "phonetic": "keh-nah dah-suhm dah-suhm tmah-theh / puhr meh gzoo soht bah-buh eh nah-nuh",
                "notes": "Gzu = gëzu (to make happy) — the wedding's true purpose is the parents' joy",
                "breakdown": [
                    ("Kena", "we have (Gheg = kemi)"),
                    ("dasëm", "wedding"),
                    ("t'madhe", "great / big"),
                    ("Për me gzu", "to make joyful"),
                    ("sot", "today"),
                    ("babë e nanë", "father and mother (Gheg)"),
                ],
            },
            {
                "gheg": "Po vjen nusja, po vjen dhandri / Çohet krejt shoqnia n'kam",
                "english": "Here comes the bride, here comes the groom / The whole company rises to their feet",
                "phonetic": "poh vyen noo-syah poh vyen than-dree / choh-het krayt shohch-nyah nkahm",
                "notes": "The procession arrives — everyone stands as a sign of respect",
                "breakdown": [
                    ("Po vjen", "is coming"),
                    ("nusja", "the bride"),
                    ("dhandri", "the groom (Gheg)"),
                    ("Çohet", "rises / stands up"),
                    ("krejt shoqnia", "the whole company"),
                    ("n'kam", "to their feet (Gheg n'këmbë)"),
                ],
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "vajze-me-zemer-guri",
        "title": "Vajzë Me Zemër Guri",
        "artist": "Lekë Dedvukaj",
        "region": "Malsia e Madhe",
        "cover": "💔",
        "audio": "audio/songs/vajze-me-zemer-guri.mp3",
        "about": "Heartbreak ballad. The narrator pines for a girl who doesn't think of him — calling her 'a girl with a heart of stone.'",
        "snippets": [
            {
                "gheg": "Sa e gjat o eshte kjo dit / Kur larg meje je moj cik",
                "english": "How long this day is / When you are far from me, girl",
                "phonetic": "sah eh gyaht oh esh-teh kyoh deet / koor lahrg meh-yeh yeh moy tseek",
                "notes": "Moj cik = vocative 'oh girl' — moj is a feminine address particle, cik = girl",
                "breakdown": [
                    ("Sa e gjat", "how long"),
                    ("eshte", "is"),
                    ("kjo dit", "this day"),
                    ("Kur", "when"),
                    ("larg meje", "far from me"),
                    ("je", "you are"),
                    ("moj cik", "oh girl (vocative)"),
                ],
            },
            {
                "gheg": "E un rri vetem e t'pres / Pa ty dua, dua te vdes",
                "english": "And I sit alone and wait for you / Without you I want — I want to die",
                "phonetic": "eh oon rree veh-tem eh tpres / pah tue doo-ah doo-ah teh vdes",
                "notes": "Classic Albanian melodrama — life and death framing for unrequited love",
                "breakdown": [
                    ("E un rri", "and I sit / stay"),
                    ("vetem", "alone"),
                    ("e t'pres", "and wait for you"),
                    ("Pa ty", "without you"),
                    ("dua", "I want"),
                    ("te vdes", "to die"),
                ],
            },
            {
                "gheg": "Ti je vajz me zemer guri / Per mu nuk mendon",
                "english": "You are a girl with a heart of stone / You don't think of me",
                "phonetic": "tee yeh vahyz meh zeh-mer goo-ree / per moo nook men-dohn",
                "notes": "Chorus — 'zemer guri' (heart of stone) is the song's emotional core",
                "breakdown": [
                    ("Ti je", "you are"),
                    ("vajz", "girl"),
                    ("me zemer", "with a heart"),
                    ("guri", "of stone"),
                    ("Per mu", "for me"),
                    ("nuk mendon", "you don't think"),
                ],
            },
            {
                "gheg": "A e shkreta imja zemer / Vetem ty te don",
                "english": "And my poor heart / Wants only you",
                "phonetic": "ah eh shkreh-tah eem-yah zeh-mer / veh-tem tue teh dohn",
                "notes": "E shkreta = the poor/wretched one — feminine; here referring to 'imja zemer' (my heart)",
                "breakdown": [
                    ("A", "and / oh"),
                    ("e shkreta", "the poor one (feminine)"),
                    ("imja zemer", "my heart"),
                    ("Vetem ty", "only you"),
                    ("te don", "wants"),
                ],
            },
            {
                "gheg": "Ditet kalojn nji nga nji / Ti ka kthehesh ma nuk je",
                "english": "The days pass one by one / You don't come back anymore",
                "phonetic": "dee-tet kah-lohyn nyee ngah nyee / tee kah kteh-hesh mah nook yeh",
                "notes": "Nji = Gheg for 'one' (Tosk = një)",
                "breakdown": [
                    ("Ditet", "the days"),
                    ("kalojn", "pass"),
                    ("nji nga nji", "one by one (Gheg nji = një)"),
                    ("Ti", "you"),
                    ("ka kthehesh", "do you return"),
                    ("ma nuk je", "you are no longer (here)"),
                ],
            },
            {
                "gheg": "Kalojn dit e koha shkon / Ndoshta ti as s'me kujton",
                "english": "Days pass and time goes by / Maybe you don't even remember me",
                "phonetic": "kah-lohyn deet eh koh-hah shkohn / ndoh-shtah tee ahs smeh kooy-tohn",
                "notes": "S'me kujton = doesn't remember me — Gheg contracts s' for nuk (not)",
                "breakdown": [
                    ("Kalojn dit", "days pass"),
                    ("e koha shkon", "and time goes"),
                    ("Ndoshta", "maybe / perhaps"),
                    ("ti as", "you don't even"),
                    ("s'me kujton", "remember me (Gheg s' = nuk)"),
                ],
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "jem-ilira",
        "title": "Jem Ilira, Jem Teuta",
        "artist": "Nikollë Nikprelaj",
        "region": "Malësi e Madhe",
        "cover": "🦅",
        "audio": "audio/songs/jem-ilira.mp3",
        "about": "Patriotic Malsor anthem. 'We are Illyrians, we are Teutas' — invoking Queen Teuta of Illyria as the spiritual mother of all Albanians, scattered but one.",
        "snippets": [
            {
                "gheg": "Tan kto male sikur thërrasin / Bjeshkët tona diç po flasin",
                "english": "All these mountains as if calling / Our highlands are saying something",
                "phonetic": "tahn ktoh mah-leh see-koor thuhr-rah-seen / byesh-kuht toh-nah deech poh flah-seen",
                "notes": "Bjeshkët = summer highland pastures, central to Malsor identity",
                "breakdown": [
                    ("Tan kto male", "all these mountains (Gheg)"),
                    ("sikur thërrasin", "as if they are calling"),
                    ("Bjeshkët tona", "our highlands"),
                    ("diç po flasin", "are saying something"),
                ],
            },
            {
                "gheg": "Mos harroni n'kangë t'i a thoni",
                "english": "Don't forget — sing it in song",
                "phonetic": "mohs hah-roh-nee nkahn-guh tee ah thoh-nee",
                "notes": "The song's mission: pass the story down through music",
                "breakdown": [
                    ("Mos harroni", "don't forget"),
                    ("n'kangë", "in song"),
                    ("t'i a thoni", "tell it / sing it"),
                ],
            },
            {
                "gheg": "Jem Ilira, jem Teuta / Jem të rritur nëpër luftna",
                "english": "We are Illyrians, we are Teutas / We grew up through wars",
                "phonetic": "yem ee-lee-rah yem teh-oo-tah / yem tuh rree-toor nuh-puhr loof-tnah",
                "notes": "Teuta was the legendary queen of Illyria (3rd century BC); the song claims her as ancestral mother",
                "breakdown": [
                    ("Jem", "we are (Gheg = jemi)"),
                    ("Ilira", "Illyrians"),
                    ("Teuta", "(Queen) Teuta of Illyria"),
                    ("të rritur", "raised / grown"),
                    ("nëpër luftna", "through wars"),
                ],
            },
            {
                "gheg": "T'gjithë Shqiptarët kudo jan / Nuk kanë tjetër veç nji nanë",
                "english": "All Albanians wherever they are / Have no other than one mother",
                "phonetic": "tgyee-thuh shchee-ptah-ruht koo-doh yahn / nook kah-nuh tyeh-tuhr vech nyee nah-nuh",
                "notes": "Nji nanë = one mother — the diaspora theme, united by origin",
                "breakdown": [
                    ("T'gjithë", "all"),
                    ("Shqiptarët", "the Albanians"),
                    ("kudo jan", "wherever they are"),
                    ("Nuk kanë tjetër", "have no other"),
                    ("veç", "except"),
                    ("nji nanë", "one mother (Gheg)"),
                ],
            },
            {
                "gheg": "Tanë kto male sikur thonë / Të gjithëve gjaku o na bashkon",
                "english": "All these mountains as if saying / Blood unites us all",
                "phonetic": "tah-nuh ktoh mah-leh see-koor thoh-nuh / tuh gyee-thuh-veh gyah-koo oh nah bahsh-kohn",
                "notes": "The blood-bond is the second pillar after the mountains themselves",
                "breakdown": [
                    ("Tanë kto male", "all these mountains"),
                    ("sikur thonë", "as if they say"),
                    ("Të gjithëve", "all of us"),
                    ("gjaku", "the blood"),
                    ("na bashkon", "unites us"),
                ],
            },
        ],
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "lum-kush-rrin",
        "title": "Lum Kush Rrin Me Burra T'mir",
        "artist": "Gjovalin Shani",
        "region": "Malësi (Highland)",
        "cover": "⚔️",
        "audio": "audio/songs/lum-kush-rrin.mp3",
        "about": "The defining Malsor honor song. Defines what a man (burrë) actually is — not killing, not vice, but mastery of his own works, brotherhood, council, and love of homeland.",
        "snippets": [
            {
                "gheg": "Heeeej / N'Malesite tona mot mbas moti / Pa djemni kurr s'i la Zoti",
                "english": "Heeeej / In our highlands, year after year / God never left them without sons",
                "phonetic": "heyy / nmah-leh-see-teh toh-nah moht mbahs moh-tee / pah djem-nee koor see lah zoh-tee",
                "notes": "Opening invocation. The long 'Heeeej' is a Malsor singing tradition",
                "breakdown": [
                    ("N'Malesite tona", "in our highlands"),
                    ("mot mbas moti", "year after year"),
                    ("Pa djemni", "without youth / sons"),
                    ("kurr s'i la", "never left them"),
                    ("Zoti", "God"),
                ],
            },
            {
                "gheg": "Kurre pa za s'e la kengetarin / Nuk e la pa nder bujarin",
                "english": "He never left the singer without voice / Didn't leave the noble without honor",
                "phonetic": "koor-reh pah zah seh lah ken-geh-tah-reen / nook eh lah pah nder boo-yah-reen",
                "notes": "The cultural inventory: voice (singer), honor (noble), wisdom (council), manliness (mountains) — each preserved by God",
                "breakdown": [
                    ("Kurre pa za", "never without voice"),
                    ("s'e la", "didn't leave"),
                    ("kengetarin", "the singer"),
                    ("pa nder", "without honor"),
                    ("bujarin", "the noble / generous one"),
                ],
            },
            {
                "gheg": "Pa urti s'e la kuvendin / Eeej pa burrni malet as vendin",
                "english": "Didn't leave the council without wisdom / Eeej without manhood, neither the mountains nor the land",
                "phonetic": "pah oor-tee seh lah koo-ven-deen / ay pah boor-nee mah-let ahs ven-deen",
                "notes": "Burrni = manliness / honor / the moral substance of a man — central Gheg virtue",
                "breakdown": [
                    ("Pa urti", "without wisdom"),
                    ("kuvendin", "the council / gathering"),
                    ("pa burrni", "without manhood / honor"),
                    ("malet", "the mountains"),
                    ("as vendin", "nor the land"),
                ],
            },
            {
                "gheg": "Nuk je trim pse vret filanin / S'bahesh burr pse e meson duhanin",
                "english": "You are not brave because you killed so-and-so / You don't become a man because you learn tobacco",
                "phonetic": "nook yeh treem psay vret fee-lah-neen / sbah-hesh boor psay eh meh-sohn doo-hah-neen",
                "notes": "The song's moral core — rejecting the easy markers of false manhood",
                "breakdown": [
                    ("Nuk je trim", "you are not brave"),
                    ("pse vret", "because you kill"),
                    ("filanin", "so-and-so / a stranger"),
                    ("S'bahesh burr", "you don't become a man"),
                    ("pse e meson", "because you learn"),
                    ("duhanin", "tobacco / smoking"),
                ],
            },
            {
                "gheg": "Trim i thojne per sa t'jet jeta / Eeej kush o i Zoti o i puneve t'veta",
                "english": "They call him brave for as long as life lasts / Eeej whoever is master of his own works",
                "phonetic": "treem ee thohy-neh per sah tyet yeh-tah / ay koosh oh ee zoh-tee oh ee poo-neh-veh tveh-tah",
                "notes": "True manhood = being the owner / master of one's own deeds",
                "breakdown": [
                    ("Trim i thojne", "they call him brave"),
                    ("per sa t'jet jeta", "for as long as life lasts"),
                    ("kush o i Zoti", "whoever is master"),
                    ("o i puneve t'veta", "of his own works"),
                ],
            },
            {
                "gheg": "Gja me t'madhe n'jet nuk ka / Kur e don shokun si vlla",
                "english": "There is nothing greater in life / Than loving your friend like a brother",
                "phonetic": "gyah meh tmah-theh nyet nook kah / koor eh dohn shoh-koon see vllah",
                "notes": "Shok si vlla — friend as brother — the highest male bond in Malsor culture",
                "breakdown": [
                    ("Gja me t'madhe", "anything greater"),
                    ("n'jet", "in life"),
                    ("nuk ka", "there is not"),
                    ("Kur e don", "when you love"),
                    ("shokun", "the friend"),
                    ("si vlla", "like a brother (Gheg = vëlla)"),
                ],
            },
            {
                "gheg": "Kur me burra rrin n'kuvend / Eee fiton nder eee fiton mend",
                "english": "When you sit in council with men / Eee you win honor, you win mind",
                "phonetic": "koor meh boo-rah rreen nkoo-vend / ay fee-tohn nder ay fee-tohn mend",
                "notes": "Kuvend = the traditional male gathering where decisions, disputes, and stories are shared",
                "breakdown": [
                    ("Kur", "when"),
                    ("me burra", "with men"),
                    ("rrin n'kuvend", "you sit in council"),
                    ("fiton nder", "you win honor"),
                    ("fiton mend", "you win mind / wisdom"),
                ],
            },
            {
                "gheg": "N'kohe te mire e n'kohe te veshtire / Eeej lum kush rrin me burra t'mire",
                "english": "In good times and in difficult times / Eeej blessed is whoever sits with good men",
                "phonetic": "nkoh-heh teh mee-reh eh nkoh-heh teh vesh-tee-reh / ay loom koosh rreen meh boo-rah tmee-reh",
                "notes": "The song's chorus and title-line. The blessing that sums up Malsor brotherhood",
                "breakdown": [
                    ("N'kohe te mire", "in good times"),
                    ("e n'kohe te veshtire", "and in difficult times"),
                    ("lum kush rrin", "blessed is whoever sits"),
                    ("me burra t'mire", "with good men"),
                ],
            },
        ],
    },
]


def make_js_object(d, indent=2, level=0):
    """Convert a Python dict/list into JS object/array literal text (no JSON quoting)."""
    pad = " " * (indent * level)
    inner = " " * (indent * (level + 1))
    if isinstance(d, dict):
        parts = []
        for k, v in d.items():
            parts.append(inner + json.dumps(k) + ": " + make_js_object(v, indent, level + 1))
        return "{\n" + ",\n".join(parts) + "\n" + pad + "}"
    if isinstance(d, list):
        if not d:
            return "[]"
        parts = [inner + make_js_object(x, indent, level + 1) for x in d]
        return "[\n" + ",\n".join(parts) + "\n" + pad + "]"
    if isinstance(d, tuple):
        return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in d) + "]"
    return json.dumps(d, ensure_ascii=False)


def main():
    src = SRC.read_text()
    songs_js = "const SONGS = " + make_js_object(SONGS, indent=2, level=0) + ";\n"

    # Find the existing SONGS block and replace it
    pattern = re.compile(r"const SONGS = \[.*?\n\];\n", re.DOTALL)
    if not pattern.search(src):
        raise SystemExit("Could not find SONGS block to replace")
    new = pattern.sub(songs_js, src, count=1)
    SRC.write_text(new)
    print(f"Replaced SONGS block. File: {len(src):,} -> {len(new):,} bytes.")
    total_snippets = sum(len(s["snippets"]) for s in SONGS)
    print(f"4 songs, {total_snippets} snippets total.")


if __name__ == "__main__":
    main()
