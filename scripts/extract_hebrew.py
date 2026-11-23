"""Split one gate of the Taḥkemoni (Project Ben-Yehuda dump file) into blocks and lines.

Usage: py -3.13 scripts/extract_hebrew.py source/m33035.txt 40

Output: data/gate-NN.he.json = {"title", "subtitle", "source_id", "blocks": [{"kind": "prose"|"verse", "lines": [...]}]}
- The edition ends each rhyme unit of the rhymed prose with a full stop: one line = one rhyme unit.
- The edition prints each half-line of a poem as a paragraph of its own: one line = one verse line,
  stored as "first half / second half".
- A one-line paragraph that ends with a colon ("and they took up their parable and said:") is prose.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
NIQQUD = re.compile(r"[֑-ׇ]")


def strip(s):
    return NIQQUD.sub("", s)


def units(text):
    """Rhyme units: split after a full stop that is followed by a space."""
    text = re.sub(r"\.(?=[א-ת])", ". ", text)  # a full stop with no space after it ("לִמְאוֹרוֹת.לְמַעַן")
    return [u.strip() for u in re.split(r"(?<=\.)\s+", text) if u.strip()]


def main():
    src, num = Path(sys.argv[1]), int(sys.argv[2])
    t = src.read_text(encoding="utf-8").split("את הטקסט")[0]  # drop the Ben-Yehuda credit line
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", t) if p.strip()]
    if num == 0:  # the introduction has a title and no subtitle line
        title, subtitle, body = paras[0], "", paras[1:]
    else:
        title, subtitle, body = paras[0], paras[1], paras[2:]
    title = re.sub(r"^ספר תחכמוני\s*[-–]\s*", "", title)

    blocks, verse = [], []

    def inner_stop(p):  # a full stop inside the paragraph, not only at its end
        return bool(re.search(r"\.\s+\S", p))

    def scripture(p):  # a refrain line that quotes a verse: "ככתוב: למרבה המשרה (ישעיה ט, ו)."
        return strip(p).startswith("ככתוב")

    def flush_verse():
        nonlocal verse
        if verse and all(inner_stop(p) for p in verse if not scripture(p)) and len(verse) > 2:
            # each paragraph is a whole verse line, its halves split by an inner full stop (gate 1, the poems
            # for the Nasi); a scripture refrain is a line of its own
            lines = []
            for p in verse:
                if scripture(p):
                    lines.append(p)
                else:
                    a, b = re.split(r"(?<=\.)\s+", p, maxsplit=1)
                    lines.append(f"{a} / {b}")
            blocks.append({"kind": "verse", "lines": lines})
            verse = []
            return
        if verse:
            heading = None
            if len(verse) % 2 and len(verse) > 1 and not verse[-1].rstrip().endswith((".", ",", ";")):
                heading = verse.pop()  # a heading line after a poem ("In the name of Him who teaches man knowledge")
            elif len(verse) == 1:
                heading = verse.pop()
            if len(verse) % 2:
                sys.exit(f"odd number of half-lines in a poem: {strip(verse[0])[:40]}")
            if verse:
                blocks.append({"kind": "verse", "lines": [f"{verse[i]} / {verse[i + 1]}" for i in range(0, len(verse), 2)]})
            if heading:
                blocks.append({"kind": "prose", "lines": [heading]})
            verse = []

    prev = ""
    for p in body:
        # a short paragraph is a half-line of verse; one that ends with a colon is a prose lead-in, unless the
        # paragraph before it was already the lead-in (then it opens the poem, as in gate 1)
        single = (len(p) < 60 and (not p.endswith(":") or (prev.endswith(":") and inner_stop(p)))) or scripture(p)
        prev = p
        if single:
            verse.append(p)
            continue
        flush_verse()
        if blocks and blocks[-1]["kind"] == "prose" and p.endswith(":") and len(p) < 60:
            blocks[-1]["lines"].append(p)  # the lead-in to a poem ends the prose block before it
        else:
            blocks.append({"kind": "prose", "lines": units(p)})
    flush_verse()

    out = ROOT / "data" / f"gate-{num:02d}.he.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"title": title, "subtitle": subtitle, "source_id": src.stem.lstrip("m"),
                               "blocks": blocks}, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(b["lines"]) for b in blocks)
    print(f"{strip(title)}: {len(blocks)} blocks, {n} lines -> {out}")
    k = 0
    for i, b in enumerate(blocks):
        print(f"-- block {i} {b['kind']} ({len(b['lines'])})")
        for l in b["lines"]:
            k += 1
            print(k, strip(l))


if __name__ == "__main__":
    main()
