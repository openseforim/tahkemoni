# Judah al-Ḥarizi, *Taḥkemoni*: Hebrew and English, line by line

Site: <https://openseforim.org/tahkemoni/>

Cite as: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24458135.svg)](https://doi.org/10.5281/zenodo.24458135) (Zenodo; this DOI always points to the newest release)

Judah al-Ḥarizi (about 1165 – 1225) wrote the *Taḥkemoni*, fifty gates (maqamat) of Hebrew rhymed prose with
poems set into it. It was the model for Immanuel of Rome's *Maḥberot*
([openseforim/immanuel](https://github.com/openseforim/immanuel)). This repository holds a line-aligned Hebrew and
English text and the scripts that build the side-by-side pages.

## Status

Complete, 25-Nov-2026: the introduction and all 50 gates, 14,867 lines, Hebrew and English line by line, with notes
for the uncertain renderings. Allusions in brackets are the translator's identifications, not yet checked against a
concordance.

- **Completeness.** The end of every gate was compared with Kaminka's edition (Warsaw 1899). The Ben-Yehuda text stops
  early in gates 5 (after the third of twelve months), 21 and 23; the missing passages are added from Kaminka,
  unvocalized, as blocks with a `source` key in `data/gate-NN.he.json`, and marked on the page.
- **Gate 35** (the tomb of Ezra) is not on Project Ben-Yehuda; its Hebrew is transcribed from Kaminka, pp. 289–296.
- **Line splitting.** `scripts/extract_hebrew.py` splits the dump; where it paired verse halves wrongly or broke a
  sentence between blocks, the translators moved whole words or lines by hand (no letters changed).
- **Removed:** two Project Ben-Yehuda footnotes that had come in as text (gates 18 and 22) and their note digits.

## Sources

- **Hebrew text:** [Project Ben-Yehuda](https://benyehuda.org/author/86), the introduction and 49 of the 50 gates (gate 35 is not there),
  vocalized, from the project's [public-domain dump](https://github.com/projectbenyehuda/public_domain_dump)
  (folder `txt/p86/`; the introduction is `m32702.txt`, gate 40 is `m33035.txt`). Most gates name the edition published by Maḥbarot le-Sifrut with
  Mosad ha-Rav Kook, Tel Aviv. No OCR was needed.
- **Scans for checking readings:** [Lagarde, Göttingen 1883](https://archive.org/details/tahkemoni00hari);
  [Kaminka, Warsaw 1899](https://archive.org/details/TachkemoniYehudaAlchariziWarsaw1899) (with commentary).

## Translations that exist

English by V. E. Reichert (1965–73) and by D. S. Segal (2001), both in copyright. German of the first maqamat by
S. I. Kaempf (1845). So the value here is an open text with an open, line-aligned translation.

## Layout

| Path | Contents |
|---|---|
| `data/gate-NN.he.json` | Hebrew, split into prose and verse blocks and lines |
| `data/gate-NN.en.txt` | English, one line for each Hebrew line; a blank line between blocks; verse halves split by ` / ` |
| `data/gate-NN.notes.json` | Notes for the uncertain renderings (⚠) |
| `scripts/extract_hebrew.py` | Splits one gate from the dump into lines |
| `scripts/build_page.py` | Checks the alignment and writes `docs/gate-NN.html` and `docs/index.html` |
| `docs/` | The GitHub Pages site |

## Build

The dump files are not in the repository. Download a gate to `source/`, then:

```
gh api -H "Accept: application/vnd.github.raw" repos/projectbenyehuda/public_domain_dump/contents/txt/p86/m33035.txt > source/m33035.txt
py -3.13 scripts/extract_hebrew.py source/m33035.txt 40
py -3.13 scripts/build_page.py
```

The introduction is gate `0` (`data/gate-00.*`). A long text can be written in part files (`data/parts/`) and joined, with one blank line between parts.

Add a new gate to `GATES` in `scripts/build_page.py`. The build stops if the Hebrew and English do not align.

## Credits

The English is by Claude (Anthropic), directed and reviewed by Ezra Brand.

## Licence

The English translation, the notes, the aligned text files and the build scripts:
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see `LICENSE`), © 2026 Ezra Brand. The Hebrew text
is as published by Project Ben-Yehuda, in its public-domain collection.
