# BesaFlow — Albanian Gheg Language Learning App

## Project Overview
BesaFlow is a single-file HTML/JS/CSS Albanian language learning app focused on the **Gheg dialect** (Malsor/Kosovo variant). Live at besaflow.netlify.app.

## Architecture — CRITICAL
- **Single file app**: Everything lives in `index.html` — HTML, CSS, JS, base64 images + audio
- **No build step, no framework, no bundler** — pure vanilla JS
- **No backend** — all data is hardcoded JS arrays, state via localStorage
- **Netlify static hosting** — entry point MUST be named `index.html`
- Do NOT split into multiple files. Do NOT add a build system.

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
- Always speaks the **phonetic string** (`.p` field), never the Albanian text
- Web Speech API, voice preference: Italian → Greek → Romanian → Croatian → Spanish → English
- `speak(phonetic)` is the main function, rate 0.68

## Achievement System
- Fires at streak 10 / 25 / 50 / 100 consecutive correct answers
- `checkStreakMilestone(streak)` called after every correct answer
- Plays *Vallja e Rugovës* (Shota) — 45s MP3 embedded as base64
- Eagle animates with gold sparks overlay
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
- `index.html` — entire app (HTML + CSS + JS + base64 eagle image + base64 audio)
- `og-image.png` — 1200×630 social share card (must be hosted at same domain)
- `favicon.png` — eagle favicon (also base64 embedded in index.html as fallback)

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
