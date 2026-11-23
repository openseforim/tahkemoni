# Judah al-Ḥarizi, *Taḥkemoni*: Hebrew and English, line by line

Site: <https://openseforim.org/tahkemoni/>

Judah al-Ḥarizi (about 1165 – 1225) wrote the *Taḥkemoni*, fifty gates (maqamat) of Hebrew rhymed prose with
poems set into it. It was the model for Immanuel of Rome's *Maḥberot*
([openseforim/immanuel](https://github.com/openseforim/immanuel)). This repository holds a line-aligned Hebrew and
English text and the scripts that build the side-by-side pages.

## Status

| Gate | Status |
|---|---|
| 40 (the pen and the sword) | Pilot, 23-Nov-2026. 206 lines. Allusions not verified. 5 uncertain renderings. |
| Introduction, 1–39, 41–50 | Not started |

## Sources

- **Hebrew text:** [Project Ben-Yehuda](https://benyehuda.org/author/86), the introduction and all fifty gates,
  vocalized, from the project's [public-domain dump](https://github.com/projectbenyehuda/public_domain_dump)
  (folder `txt/p86/`; gate 40 is `m33035.txt`). Most gates name the edition published by Maḥbarot le-Sifrut with
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

Add a new gate to `GATES` in `scripts/build_page.py`. The build stops if the Hebrew and English do not align.

## Credits

The English is by Claude (Anthropic), directed and reviewed by Ezra Brand.

## Licence

The English translation, the notes, the aligned text files and the build scripts:
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see `LICENSE`), © 2026 Ezra Brand. The Hebrew text
is as published by Project Ben-Yehuda, in its public-domain collection.
