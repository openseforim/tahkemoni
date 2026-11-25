"""Check one gate's English against its Hebrew before a build, and print the Hebrew as a numbered list.

  py -3.13 -I scripts/check_gate.py 24          alignment check of data/gate-24.en.txt and its notes
  py -3.13 -I scripts/check_gate.py 24 --show   the Hebrew (without vowels), numbered by block and line

The rules are those of build_page.py: as many English blocks (separated by one blank line) as Hebrew blocks, as many
lines in each block, " / " in a line exactly when the Hebrew line is a verse line with two halves, and a note for
every mark ⚠n (and no note without a mark)."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
NIQQUD = re.compile(r"[֑-ׇ]")

num = int(sys.argv[1])
stem = f"gate-{num:02d}"
he = json.loads((ROOT / "data" / f"{stem}.he.json").read_text(encoding="utf-8"))
if "--show" in sys.argv:
    print(NIQQUD.sub("", he["title"]), "|", NIQQUD.sub("", he.get("subtitle", "")))
    k = 0
    for i, b in enumerate(he["blocks"]):
        print(f"\n-- block {i + 1} ({b['kind']}, {len(b['lines'])} lines)")
        for line in b["lines"]:
            k += 1
            print(f"{k}\t{NIQQUD.sub('', line)}")
    sys.exit(0)

blocks, cur = [], []
for raw in (ROOT / "data" / f"{stem}.en.txt").read_text(encoding="utf-8").split("\n"):
    line = raw.strip()
    if line:
        cur.append(line)
    elif cur:
        blocks.append(cur)
        cur = []
if cur:
    blocks.append(cur)
errors = []
hb = he["blocks"]
if len(hb) != len(blocks):
    errors.append(f"block count: Hebrew {len(hb)}, English {len(blocks)}")
k = 0
for i, (h, x) in enumerate(zip(hb, blocks)):
    if len(h["lines"]) != len(x):
        errors.append(f"block {i + 1}: Hebrew {len(h['lines'])} lines, English {len(x)}: {x[0][:50]}")
    for j, (hl, xl) in enumerate(zip(h["lines"], x)):
        if (" / " in hl) != (" / " in xl):
            errors.append(f"block {i + 1} line {j + 1}: half-line mark differs: {xl[:50]}")
notes = json.loads((ROOT / "data" / f"{stem}.notes.json").read_text(encoding="utf-8"))
text = "\n".join("\n".join(b) for b in blocks)
marks = re.findall(r"⚠(\d+)", text)
if marks != [str(i) for i in range(1, len(marks) + 1)]:
    errors.append(f"marks are not 1..n in order: {marks}")
if set(marks) != set(notes):
    errors.append(f"marks {sorted(set(marks), key=int)} vs notes {sorted(notes, key=int)}")
for k_, v in notes.items():
    if not isinstance(v, dict) or not {"he", "note"} <= set(v):
        errors.append(f"note {k_}: needs 'he' and 'note'")
print("\n".join(errors) if errors else
      f"OK: {len(blocks)} blocks, {sum(map(len, blocks))} lines, {len(notes)} notes")
sys.exit(1 if errors else 0)
