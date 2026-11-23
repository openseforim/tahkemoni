"""Build the side-by-side page for one gate of the Taḥkemoni, and the index page.

Usage: py -3.13 scripts/build_page.py 40 "The Fortieth Gate" "The pen and the sword: which is more needed"

Inputs (in data/):
  gate-NN.he.json     from extract_hebrew.py (blocks with kind and lines)
  gate-NN.en.txt      one English line for each Hebrew line; a blank line between blocks;
                      a verse line has its two halves split by " / "
  gate-NN.notes.json  notes for the marks "⚠n"
Output: docs/gate-NN.html, then docs/index.html (from GATES below).
The script stops if the English and Hebrew block or line counts do not agree.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
e = html.escape

# gates that have a page: number -> (English title, subtitle)
GATES = {
    0: ("Introduction", "The author's preface: praise of God, the soul and the intellect, the Hebrew language as a bride, why the book was written, and the dedication"),
    1: ("The First Gate", "How the book came to be, and in whose name it was composed: a friend's challenge, the defense of Hebrew, and the praise of the Nasi Josiah"),
    40: ("The Fortieth Gate", "The pen and the sword: which is more needed by men and by their wars"),
}
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Hebrew:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="/assets/os.css">
<script src="/assets/os.js" defer></script>
</head>
<body>
"""


def read_english(path):
    blocks, cur = [], []
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if line:
            cur.append(line)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def fmt_en(text):
    text = e(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]", r'<span class="ref">[\1]</span>', text)
    return re.sub(r"\s*⚠(\d+)", r'<a class="warn" href="#n\1" id="r\1" title="uncertain rendering">⚠\1</a>', text)


def halves(text, fmt):
    """A verse line: two halves, shown apart."""
    if " / " not in text:
        return fmt(text)
    a, b = text.split(" / ", 1)
    return f'<span class="h1">{fmt(a)}</span> <span class="h2">{fmt(b)}</span>'


def gate_page(num, title, subtitle):
    stem = f"gate-{num:02d}"
    he = json.loads((ROOT / "data" / f"{stem}.he.json").read_text(encoding="utf-8"))
    en = read_english(ROOT / "data" / f"{stem}.en.txt")
    notes = json.loads((ROOT / "data" / f"{stem}.notes.json").read_text(encoding="utf-8"))
    hb = he["blocks"]
    bad = len(hb) != len(en)
    if bad:
        print(f"block count: Hebrew {len(hb)}, English {len(en)}")
    for i, (h, x) in enumerate(zip(hb, en)):
        if len(h["lines"]) != len(x):
            bad = True
            print(f"block {i}: Hebrew {len(h['lines'])} lines, English {len(x)} lines: {x[0][:50]}")
        for j, (hl, xl) in enumerate(zip(h["lines"], x)):
            if (" / " in hl) != (" / " in xl):
                bad = True
                print(f"block {i} line {j + 1}: half-line marks differ: {xl[:50]}")
    if bad:
        sys.exit("alignment errors; no page written")

    rows, n = [], 0
    for h, x in zip(hb, en):
        rows.append(f'<section class="blk {h["kind"]}">')
        for hl, xl in zip(h["lines"], x):
            n += 1
            rows.append(f'<div class="row" id="l{n}"><a class="ln" href="#l{n}">{n}</a>'
                        f'<p class="en">{halves(xl, fmt_en)}</p>'
                        f'<p class="he" lang="he" dir="rtl">{halves(hl, lambda s: e(s, quote=False))}</p></div>')
        rows.append("</section>")
    note_rows = "\n".join(
        f'<li id="n{k}"><a href="#r{k}">⚠{k}</a> <span lang="he" dir="rtl" class="he-inline">{e(v["he"])}</span>'
        f' — {e(v["note"], quote=False)}</li>' for k, v in notes.items())
    keys = sorted(GATES)
    i = keys.index(num)
    label = lambda k: "Introduction" if k == 0 else f"Gate {k}"
    prev = f'<a href="gate-{keys[i - 1]:02d}.html" rel="prev">← {label(keys[i - 1])}</a>' if i > 0 else ""
    nxt = f'<a href="gate-{keys[i + 1]:02d}.html" rel="next">{label(keys[i + 1])} →</a>' if i + 1 < len(keys) else ""
    pn = f'<span class="pn">{prev}{nxt}</span>' if prev or nxt else ""
    he_sub = e(he["title"]) + (f": {e(he['subtitle'])}" if he["subtitle"] else "")
    page = HEAD.format(title=f"{e(title)} — al-Ḥarizi, Taḥkemoni") + f"""<header class="chapter">
<nav class="crumb" aria-label="Gates"><span><a href="index.html">All gates</a> · {label(num)}</span>{pn}</nav>
<h1>{e(title)}</h1>
<p class="sub">{e(subtitle)}</p>
<p class="sub-he" lang="he" dir="rtl">{he_sub}</p>
<details class="about"><summary>About this text</summary>
<p class="meta">{n} lines. One row is one rhyme unit of the rhymed prose, or one line of verse (its two halves set apart).
References in <span class="ref">[gray brackets]</span> are the translator's identifications of biblical phrases.
<a class="warn" href="#notes">⚠</a> marks an uncertain rendering.
Each line number is a link to that line.
Hebrew text: <a href="https://benyehuda.org/read/{he["source_id"]}">Project Ben-Yehuda</a>.</p>
</details>
</header>
<main>
{chr(10).join(rows)}
</main>
<footer id="notes">
<h2>Uncertain renderings</h2>
<ul class="notes">
{note_rows}
</ul>
<nav class="crumb foot" aria-label="Gates"><span><a href="index.html">All gates</a></span>{pn}</nav>
</footer>
</body>
</html>
"""
    out = ROOT / "docs" / f"{stem}.html"
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out}: {len(hb)} blocks, {n} lines")
    return n


def index_page(counts):
    rows = "\n".join(f'<tr><td><a href="gate-{k:02d}.html">{k or "Introduction"}</a></td><td>{e(v[1])}</td><td>{counts[k]} lines</td></tr>'
                     for k, v in sorted(GATES.items()))
    first = min(GATES)  # 0 = the introduction
    page = HEAD.format(title="Judah al-Ḥarizi, Taḥkemoni: Hebrew and English") + f"""<header>
<h1>Judah al-Ḥarizi, <i>Taḥkemoni</i></h1>
<p class="sub">The Hebrew maqamat, with an English translation line by line · <span lang="he" dir="rtl">ספר תחכמוני</span></p>
<p class="meta">Judah al-Ḥarizi (about 1165 – 1225) wrote the <i>Taḥkemoni</i>, fifty gates of Hebrew rhymed prose with poems set
into it. The narrator, Heman the Ezrahite, meets again and again the wandering poet Ḥever the Kenite. The book was the model for
Immanuel of Rome's <a href="/immanuel/"><i>Maḥberot</i></a>. This site shows the Hebrew and the English side by side, one row for each line.</p>
</header>
<article>
<h2>Gates</h2>
<div class="tablewrap">
<table>
<tr><th>Gate</th><th>Subject</th><th>Status</th></tr>
{rows}
<tr><td>2–39, 41–50</td><td></td><td>Not started</td></tr>
</table>
</div>
<a class="cta" href="gate-{first:02d}.html">Read the {e(GATES[first][0])}, side by side →</a>

<h2>Method</h2>
<ul>
<li><b>Lines.</b> The Hebrew edition ends each rhyme unit of the rhymed prose with a full stop. Each unit is one row. Each line of verse is one row, with its two halves set apart.</li>
<li><b>Prose.</b> The English is cadenced prose. Rhyme is kept only where English gives it without added words.</li>
<li><b>Poems.</b> The English is literal, line for line. It does not keep the meter or the rhyme.</li>
<li><b>Allusions.</b> Al-Ḥarizi builds his sentences from biblical phrases. References in gray brackets identify them. They are the translator's identifications and are not yet checked against a concordance.</li>
<li><b>Uncertain renderings</b> have the mark ⚠ and a note at the end of the page.</li>
<li><b>Translator.</b> The translation is by Claude (Anthropic), directed and reviewed by Ezra Brand.</li>
</ul>

<h2>The Hebrew text</h2>
<div class="tablewrap">
<table>
<tr><th>Source</th><th>Contents</th><th>Notes</th></tr>
<tr><td><a href="https://benyehuda.org/author/86">Project Ben-Yehuda</a></td><td>The introduction and all fifty gates, one text for each gate</td><td>Vocalized. In the project's <a href="https://github.com/projectbenyehuda/public_domain_dump">public-domain dump</a> (folder <code>txt/p86/</code>). Most gates name the edition published by Maḥbarot le-Sifrut with Mosad ha-Rav Kook, Tel Aviv. This is the text used here.</td></tr>
<tr><td><a href="https://archive.org/details/tahkemoni00hari">Lagarde, Göttingen 1883</a></td><td>Scan of P. de Lagarde's edition (400 ppi)</td><td>For a check of readings.</td></tr>
<tr><td><a href="https://archive.org/details/TachkemoniYehudaAlchariziWarsaw1899">Kaminka, Warsaw 1899</a></td><td>Scan of A. Kaminka's edition with commentary</td><td>For a check of readings and allusions.</td></tr>
</table>
</div>

<h2>Translations that exist</h2>
<ul>
<li>English: V. E. Reichert, <i>The Taḥkemoni of Judah al-Ḥarizi</i>, 2 vols. (Jerusalem, 1965–73); D. S. Segal, <i>The Book of Taḥkemoni</i> (Littman Library, 2001). Both are in copyright.</li>
<li>German: S. I. Kaempf, the first maqamat (Berlin, 1845), <a href="https://archive.org/details/dieerstenmakamen00juda">scan</a>.</li>
</ul>
<p>So the value here is an open Hebrew text with an open, line-aligned translation, not a first translation. This list can be incomplete.</p>
</article>
</body>
</html>
"""
    (ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
    print("wrote docs/index.html")


def main():
    (ROOT / "docs").mkdir(exist_ok=True)
    counts = {k: gate_page(k, *v) for k, v in GATES.items()}
    index_page(counts)


if __name__ == "__main__":
    main()
    # Open Seforim post-build: canonical and social tags, early display script, lang, CSS/JS version stamps
    import subprocess
    tool = ROOT.parent / "openseforim-site" / "tools" / "postbuild.py"
    if tool.exists():
        subprocess.run([sys.executable, str(tool), "tahkemoni", str(ROOT / "docs")], check=False)
