"""
Consolidate 19 categories down to 11 broader, simpler groupings.
User: "feels like way too many or redundant — make the categories more
wide / simpler."

Final 11:
  People & Family          ← Family & People
  Body & Health            ← (kept)
  Food & Drink             ← Food & Drink + Food & Eating
  Home & Things            ← Household & Objects + Clothing & Personal +
                              School, Work & Tech
  Places & Travel          ← Places & Transport + Getting Around
  Nature & Animals         ← (kept)
  Verbs                    ← (kept)
  Describing               ← Adjectives & Colors  (renamed for plainer English)
  Time & Calendar          ← Time & Function Words + Holidays
  Conversation             ← Greetings & Small Talk + Everyday Expressions +
                              Emergency + Heritage & Honor
  Sentences                ← (kept — pairs with the Sentences study mode)
"""
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

MAP = {
    "Family & People":         "People & Family",
    "Body & Health":           "Body & Health",
    "Food & Drink":            "Food & Drink",
    "Food & Eating":           "Food & Drink",
    "Household & Objects":     "Home & Things",
    "Clothing & Personal":     "Home & Things",
    "School, Work & Tech":     "Home & Things",
    "Places & Transport":      "Places & Travel",
    "Getting Around":          "Places & Travel",
    "Nature & Animals":        "Nature & Animals",
    "Verbs":                   "Verbs",
    "Adjectives & Colors":     "Describing",
    "Time & Function Words":   "Time & Calendar",
    "Holidays":                "Time & Calendar",
    "Greetings & Small Talk":  "Conversation",
    "Everyday Expressions":    "Conversation",
    "Emergency":               "Conversation",
    "Heritage & Honor":        "Conversation",
    "Sentences":               "Sentences",
}


def main():
    src = SRC.read_text()
    before = len(src)

    # Count current categories so we can show what changed.
    before_counts = Counter(re.findall(r'cat:"([^"]+)"', src))

    # Apply mapping. Use replace with longest keys first to avoid partial
    # collisions (e.g. "Body & Health" is a prefix of nothing here but be safe).
    new_src = src
    for old in sorted(MAP, key=len, reverse=True):
        new = MAP[old]
        if old == new:
            continue
        # Only replace exact cat:"<old>" occurrences.
        new_src = new_src.replace(f'cat:"{old}"', f'cat:"{new}"')

    after_counts = Counter(re.findall(r'cat:"([^"]+)"', new_src))

    SRC.write_text(new_src)

    print(f"File: {before:,} -> {len(new_src):,} bytes\n")
    print(f"Categories: {len(before_counts)} -> {len(after_counts)}\n")
    print("New category counts (entries):")
    for cat, n in sorted(after_counts.items(), key=lambda x: -x[1]):
        sources = sorted(o for o, t in MAP.items() if t == cat and o != cat)
        delta = ""
        if sources:
            delta = "  (merged: " + ", ".join(sources) + ")"
        print(f"  {n:4d}  {cat}{delta}")


if __name__ == "__main__":
    main()
