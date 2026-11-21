[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/zero-two-1836/world-news-21-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/zero-two-1836/world-news-21-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261121)

# The World in One Picture — Saturday, 21 November 2026

A single-image summary of one day's world news, built for the make.fun
`news-image-20261121` competition. The whole day is compressed into one
1024×1024 newspaper-style infographic: one hero story across the top and
nine panels underneath, each with a short label a reader can take in at a
glance.

## The day's stories

**Hero:** Russian ballistic missile hits Kryvyi Rih.

**Panels:**

- AI sell-off rocks markets
- Mexico captures cartel boss "El Chapo Isidro"
- ICJ rules on the Myanmar genocide case
- COP31 deadlocked in Antalya
- Peru hit by a 6.9 earthquake
- Wolbachia mosquitoes cut dengue in Brazil
- BepiColombo reaches Mercury orbit
- 700,000 displaced in southern Ethiopia
- Verstappen takes Las Vegas GP pole

## How it is built

Three files do the work:

- **`build_image.py`** — the generator. It draws the infographic with
  Pillow: fixed panel geometry, hand-set headlines and captions, simple
  drawn icons, on a warm newsprint palette. The canvas is rendered at
  2× supersample (2048×2048) and downscaled to 1024×1024 with LANCZOS,
  which keeps the text crisp. The render is fully deterministic — fixed
  geometry, fixed text, no randomness and no timestamps — so every run
  produces byte-identical output.
- **`entry.png`** — the rendered image, committed to the repo so the
  entry does not depend on fonts or Pillow being available at run time.
- **`main.py`** — the entrypoint. It uses only the Python standard
  library (the grading sandbox installs nothing), and simply copies the
  committed `entry.png` into the output directory
  (`$MAKEFUN_OUTPUT_DIR`, or `/output` by default).

## Running it

Regenerate the image (requires Pillow):

```sh
python3 build_image.py
```

Produce the competition output (standard library only):

```sh
python3 main.py
```

## License

MIT — see `LICENSE`.
