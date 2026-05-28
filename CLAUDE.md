# BesaFlow — Albanian Gheg Language Learning App

## Project Overview
BesaFlow is a single-file HTML/JS/CSS Albanian language learning app focused on the **Gheg dialect** (Malsor/Kosovo variant). Live at besaflow.netlify.app.

## Architecture — CRITICAL
- **Code lives in `index.html`** — HTML, CSS, JS all in one file (~125 KB)
- **Audio served as static files** under `audio/` (externalized May 2026; was previously base64 inline at 50 MB)
  - `audio/male/NNNN.mp3` and `audio/female/NNNN.mp3` — ElevenLabs clips per word
  - `audio/milestones/{shotaAudio,gjovalinAudio,lekeAudio,nikolleAudio}.mp3` — streak songs
  - `audio/manifest.json` — text → "NNNN" lookup (also baked into JS as `AUDIO_MANIFEST`)
  - `audio/missing_female.json` — list of 118 texts pending female regen
- **Single eagle PNG** at `assets/eagle.png` (referenced from index.html)
- **No build step, no framework, no bundler** — pure vanilla JS
- **No backend** — data is hardcoded JS arrays, state via localStorage
- **Netlify static hosting** — entry point MUST be named `index.html`
- Do NOT add a build system. Do NOT re-bake audio into base64.

## Data Structure
All word data lives as JS arrays in the `<script>` block:

```js
const WORDS = [
  {e:"🐕", w:"dog", a:"qen", p:"chen", cat:"Nature & Animals", pos:"Noun"},
  // e=emoji, w=english, a=albanian_gheg, p=phonetic, cat=category, pos=part_of_speech
]
const PHRASES = [
  {e:"👋", w:"How are you?", a:"Qysh je?", p:"kysh yeh", cat:"Greetings & Small Talk", pos:"Phrase"},
]
const SENTENCES = [
  {e:"💬", w:"I eat bread", a:"Unë ha bukë", p:"oo-nuh hah boo-kuh", cat:"Sentences", pos:"Sentence"},
]
```

## Gheg Dialect Rules — NEVER use Tosk forms
Always verify words are Gheg (northern Albanian / Kosovo / Malsor), NOT Tosk (standard/southern):
- `nanë` not `nënë` (mother)
- `babë` not `baba/atë` (father)
- `vlla` not `vëllai` (brother)
- `nandë` not `nëntë` (nine)
- `katun` not `fshat` (village)
- `zjarm` not `zjarr` (fire)
- `hanë` not `hënë` (moon)
- `qysh` not `si` (how)
- `qikë` not `vajzë` (girl)
- `krejt` not `të gjitha` (all)
- `nashta` not `ndoshta` (maybe)
- `tash` not `tani` (now)
- Verbs: `me hangër` (to eat), `me pi` (to drink), `me fol` (to speak)
- Reference: Gjergj Fishta's *Lahuta e Malcis* for authentic Malsor Gheg

## Study Modes
1. `flash` — Flashcards: English front, Albanian on flip, auto-speaks phonetic
2. `mc` — Multiple Choice: 4 options, feedback + repeat button
3. `listen` — Listen & ID: hears phonetic, picks Albanian from choices
4. `sent` — Sentences: uses SENTENCES array, flashcard format
5. `phr` — Phrases: uses PHRASES array, 6 sub-categories, flashcard format
6. `mix` — Mixed: randomly picks flash/mc/listen each session

## Pronunciation / Voice
- `speak(albanian, phonetic)` — primary path is the ElevenLabs clip via `AUDIO_MANIFEST[albanian]`
- Voice preference (`_voicePref`) is `'male'` or `'female'`, stored in `localStorage.bf_voice`
- Fallback chain: requested gender → male (if female missing for that text) → Web Speech API on the phonetic string (`u.lang='en-US'`, rate 0.72)
- 118 female clips still missing — listed in `audio/missing_female.json`. Regenerate via ElevenLabs when quota allows.

## Achievement System
- Fires at streak 10 / 25 / 50 / 100 consecutive correct answers
- `checkStreakMilestone(streak)` called after every correct answer
- Songs are external MP3s under `audio/milestones/` — `<audio id="...">` tags reference them by relative path
  - 10: shotaAudio.mp3 (Vallja e Rugovës, 45s)
  - 25: gjovalinAudio.mp3 (skip 35s intro)
  - 50: lekeAudio.mp3 (skip 5s intro)
  - 100: nikolleAudio.mp3 (full)
- Eagle animates with gold sparks overlay (`assets/eagle.png`)
- `_lastMilestoneFired` prevents duplicate triggers; resets on wrong answer

## App State Object
```js
let S = {
  mode: 'flash',       // study mode
  selectedCats: [],    // active category filters
  count: 25,           // questions per session
  queue: [],           // shuffled word queue
  idx: 0,              // current position
  correct: 0,          // correct this session
  streak: 0,           // consecutive correct streak
  fcFlipped: false,    // flashcard flipped?
  listenMode: false,   // listening session?
  sentMode: false,     // sentences/phrases mode?
  practiced: [],       // all words ever practiced (localStorage: bf_practiced)
};
```

## Category Chips
- `buildCatChips(pool)` — rebuilds chips from whichever array is active
- Called automatically when mode changes via `selectMode()`
- `S.selectedCats[]` tracks which are toggled on

## Theming
- Dark mode default: `--bg:#0F1117`, `--red:#C8241E`, `--gold:#D4A843`
- Light mode via `[data-theme="light"]` on `<html>`
- `toggleTheme()` toggles and saves to `localStorage` key `bf_dark`

## Files
- `index.html` — app code (~125 KB; HTML + CSS + JS + small AUDIO_MANIFEST)
- `assets/eagle.png` — eagle logo (referenced from index.html)
- `og-image.png` — 1200×630 social share card
- `favicon.png` — eagle favicon (linked, not inlined)
- `audio/` — externalized voice clips + milestone songs + manifest
- `scripts/` — one-off Python tooling (`externalize_audio.py`, `patch_index.py`, `externalize_assets.py`)
- `source/` (gitignored) — original Gheg CSVs used to seed the data arrays
- `reference-audio/` (gitignored) — Wikitongues native-speaker reference recordings

## Deployment
1. All 3 files go to Netlify together (drag zip or drag folder)
2. File MUST be `index.html` — any other name = 404 at root
3. iMessage OG preview only works when `og-image.png` is live at besaflow.netlify.app/og-image.png

## Adding Words — checklist
1. Spelling must be Gheg, not Tosk/Standard
2. Phonetic uses English sounds, hyphen-separated syllables  
3. Category matches existing 11 cats or add new one consistently
4. Emoji is contextually appropriate
5. Add to `const WORDS = [` array

## Adding Phrases — categories available
- Greetings & Small Talk
- Food & Eating  
- Getting Around
- Family & People
- Everyday Expressions
- Heritage & Honor
