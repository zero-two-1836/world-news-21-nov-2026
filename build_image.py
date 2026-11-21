#!/usr/bin/env python3
"""Build entry.png: the world news of Saturday 21 November 2026 in one image.

Renders a newspaper-style infographic at 2x supersample, then downscales
to 1024x1024 with LANCZOS for crisp text. Fully deterministic: fixed
geometry, fixed text, no randomness, no timestamps in the PNG.
"""
import os

from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample factor
W = 1024 * SS               # canvas is 2048x2048 before downscale

PAPER = (246, 241, 231)     # warm newsprint
PANEL = (255, 253, 248)     # panel card
INK = (20, 24, 29)          # near-black ink
GRAY = (74, 79, 87)         # caption gray
RED = (179, 49, 42)         # headline red

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BOLD = "DejaVuSans-Bold.ttf"
REG = "DejaVuSans.ttf"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def centered(d, cx, y, text, fnt, fill):
    """Draw text horizontally centred on cx at height y."""
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- icons
# Each icon draws inside a box centred on (cx, cy); s is the half-size.

def icon_missile(d, cx, cy, s, col):
    # buildings bottom-right
    d.rectangle([cx + 18, cy + 6, cx + 44, cy + s], fill=col)
    d.rectangle([cx + 50, cy - 14, cx + 74, cy + s], fill=col)
    # missile body, diagonal from tail (top-right) to nose (bottom-left)
    d.line([cx + 34, cy - 34, cx - 30, cy + 30], fill=col, width=30)
    # nose cone
    d.polygon([cx - 30, cy + 30, cx - 58, cy + 58, cx - 14, cy + 46], fill=col)
    # fins near the tail
    d.polygon([cx + 34, cy - 34, cx + 58, cy - 40, cx + 40, cy - 12], fill=col)
    d.polygon([cx + 34, cy - 34, cx + 28, cy - 60, cx + 10, cy - 38], fill=col)
    # exhaust dashes behind the tail
    for i in range(3):
        o = 18 + i * 16
        d.line([cx + 44 + o, cy - 44 - o, cx + 58 + o, cy - 58 - o],
               fill=col, width=8)
    # impact starburst at the nose
    for dx, dy in ((-1, 0), (0, 1), (-1, 1), (1, 1), (-1, -1)):
        d.line([cx - 62, cy + 62, cx - 62 + dx * 22, cy + 62 + dy * 22],
               fill=RED, width=8)


def icon_chart(d, cx, cy, s, col):
    # axes
    d.line([cx - s, cy - s, cx - s, cy + s], fill=INK, width=7)
    d.line([cx - s, cy + s, cx + s, cy + s], fill=INK, width=7)
    # plunging line
    pts = [(cx - 66, cy - 26), (cx - 34, cy - 12), (cx - 4, cy - 34),
           (cx + 28, cy + 4), (cx + 64, cy + 46)]
    d.line(pts, fill=RED, width=10, joint="curve")
    # arrowhead at the end of the plunge
    d.polygon([cx + 64, cy + 46, cx + 40, cy + 42, cx + 58, cy + 22], fill=RED)


def icon_cuffs(d, cx, cy, s, col):
    wdt = 11
    d.ellipse([cx - 62, cy - 26, cx + 6, cy + 42], outline=col, width=wdt)
    d.ellipse([cx - 6, cy - 26, cx + 62, cy + 42], outline=col, width=wdt)
    # chain links across the top
    for i in range(3):
        x = cx - 24 + i * 20
        d.ellipse([x, cy - 52, x + 18, cy - 34], outline=col, width=7)


def icon_scales(d, cx, cy, s, col):
    wdt = 9
    # beam and post
    d.line([cx - s, cy - 38, cx + s, cy - 38], fill=col, width=wdt)
    d.line([cx, cy - 38, cx, cy + 44], fill=col, width=wdt)
    d.ellipse([cx - 9, cy - 56, cx + 9, cy - 38], outline=col, width=7)
    # base
    d.line([cx - 30, cy + 52, cx + 30, cy + 52], fill=col, width=wdt)
    # pans
    for sx in (-s, s):
        d.line([sx + cx, cy - 38, sx + cx - 22, cy + 16], fill=col, width=6)
        d.line([sx + cx, cy - 38, sx + cx + 22, cy + 16], fill=col, width=6)
        d.arc([sx + cx - 30, cy + 2, sx + cx + 30, cy + 44], 0, 180,
              fill=col, width=7)


def icon_thermo(d, cx, cy, s, col):
    # sun behind, top right
    scx, scy, sr = cx + 46, cy - 48, 24
    d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], outline=col, width=8)
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.line([scx + dx * 34, scy + dy * 34, scx + dx * 46, scy + dy * 46],
               fill=col, width=7)
    # thermometer tube and bulb
    d.rounded_rectangle([cx - 42, cy - 62, cx - 10, cy + 22], radius=16,
                        outline=INK, width=8)
    d.ellipse([cx - 56, cy + 8, cx + 4, cy + 68], outline=INK, width=8)
    d.rectangle([cx - 34, cy - 6, cx - 18, cy + 26], fill=RED)
    d.ellipse([cx - 48, cy + 16, cx - 4, cy + 60], fill=RED)


def icon_quake(d, cx, cy, s, col):
    # seismic trace: flat, then a violent zigzag, then flat again
    pts = [(cx - s, cy + 6), (cx - 52, cy + 6), (cx - 40, cy - 34),
           (cx - 26, cy + 40), (cx - 12, cy - 52), (cx + 2, cy + 34),
           (cx + 16, cy - 20), (cx + 30, cy + 6), (cx + s, cy + 6)]
    d.line(pts, fill=col, width=9, joint="curve")
    # cracked ground line beneath
    d.line([cx - s, cy + 56, cx - 14, cy + 56], fill=INK, width=7)
    d.line([cx + 14, cy + 56, cx + s, cy + 56], fill=INK, width=7)
    d.line([cx - 14, cy + 56, cx - 2, cy + 68, cx + 8, cy + 58],
           fill=INK, width=6)


def icon_mosquito(d, cx, cy, s, col):
    # two wings swept up and back over the body
    d.ellipse([cx - 54, cy - 60, cx + 4, cy - 16], outline=col, width=7)
    d.ellipse([cx - 4, cy - 64, cx + 54, cy - 20], outline=col, width=7)
    # slim abdomen trailing down to the right
    d.ellipse([cx + 0, cy + 0, cx + 62, cy + 26], fill=col)
    # thorax and head
    d.ellipse([cx - 28, cy - 12, cx + 8, cy + 22], fill=col)
    d.ellipse([cx - 48, cy - 16, cx - 28, cy + 4], fill=col)
    # proboscis pointing down-left
    d.line([cx - 44, cy + 0, cx - 66, cy + 32], fill=col, width=7)
    # six legs dangling below
    for lx in (-18, 2, 22):
        d.line([cx + lx, cy + 20, cx + lx - 10, cy + 50], fill=col, width=6)
        d.line([cx + lx + 8, cy + 20, cx + lx + 20, cy + 48], fill=col,
               width=6)


def icon_probe(d, cx, cy, s, col):
    # planet Mercury
    px, py, pr = cx - 26, cy + 12, 46
    d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=col, width=9)
    for ox, oy, r in ((-14, -10, 9), (12, 14, 7), (18, -18, 5)):
        d.ellipse([px + ox - r, py + oy - r, px + ox + r, py + oy + r],
                  outline=col, width=5)
    # spacecraft above right: bus, two solar wings, dish
    bx, by = cx + 40, cy - 40
    d.rectangle([bx - 14, by - 12, bx + 14, by + 12], fill=col)
    d.rectangle([bx - 52, by - 9, bx - 18, by + 9], outline=col, width=6)
    d.rectangle([bx + 18, by - 9, bx + 52, by + 9], outline=col, width=6)
    d.arc([bx - 12, by - 34, bx + 20, by - 6], 200, 320, fill=col, width=6)
    d.line([bx + 4, by - 12, bx + 4, by - 22], fill=col, width=6)


def icon_tent(d, cx, cy, s, col):
    # tent
    d.line([cx - 6, cy - 52, cx - 62, cy + 52], fill=col, width=9)
    d.line([cx - 6, cy - 52, cx + 66, cy + 52], fill=col, width=9)
    d.line([cx - 62, cy + 52, cx + 66, cy + 52], fill=col, width=9)
    d.polygon([cx - 6, cy - 6, cx - 26, cy + 52, cx + 16, cy + 52], fill=col)
    # displaced person beside the tent: head, body, legs
    hx, hy = cx - 92, cy - 6
    d.ellipse([hx - 11, hy - 30, hx + 11, hy - 8], outline=INK, width=6)
    d.line([hx, hy - 6, hx, hy + 26], fill=INK, width=7)
    d.line([hx, hy + 26, hx - 12, hy + 54], fill=INK, width=6)
    d.line([hx, hy + 26, hx + 12, hy + 54], fill=INK, width=6)


def icon_flag(d, cx, cy, s, col):
    # pole
    d.line([cx - 52, cy - s, cx - 52, cy + s], fill=INK, width=9)
    # chequered flag, 4x3 squares
    fx, fy, sq = cx - 52, cy - s, 27
    for r in range(3):
        for c in range(4):
            if (r + c) % 2 == 0:
                d.rectangle([fx + c * sq, fy + r * sq,
                             fx + (c + 1) * sq, fy + (r + 1) * sq],
                            fill=INK)
            else:
                d.rectangle([fx + c * sq, fy + r * sq,
                             fx + (c + 1) * sq, fy + (r + 1) * sq],
                            fill=PANEL, outline=INK, width=2)
    d.rectangle([fx, fy, fx + 4 * sq, fy + 3 * sq], outline=INK, width=4)


# ---------------------------------------------------------------- data

HERO_STORY = {
    "icon": icon_missile,
    "accent": (179, 49, 42),
    "kicker": "UKRAINE · WAR",
    "lines": ["MISSILE HITS", "ZELENSKY'S HOMETOWN"],
    "sub_lines": ["Russian strike on Kryvyi Rih: 2 killed, 60 wounded."],
}

STORIES = [
    {"icon": icon_chart, "accent": (179, 49, 42),
     "lines": ["AI SELL-OFF", "ROCKS MARKETS"],
     "sub": "S&P 500 -3.7% · Nikkei -5.1%"},
    {"icon": icon_cuffs, "accent": (30, 125, 70),
     "lines": ["MEXICO CAPTURES", "CARTEL BOSS"],
     "sub": "'El Chapo Isidro' held in Sinaloa"},
    {"icon": icon_scales, "accent": (107, 63, 160),
     "lines": ["UN COURT RULES:", "MYANMAR GENOCIDE"],
     "sub": "ICJ verdict on the Rohingya case"},
    {"icon": icon_thermo, "accent": (14, 125, 134),
     "lines": ["COP31 CLIMATE", "TALKS DEADLOCK"],
     "sub": "Antalya summit overruns deadline"},
    {"icon": icon_quake, "accent": (201, 106, 18),
     "lines": ["6.9 QUAKE", "SHAKES PERU"],
     "sub": "Andes region near Junin"},
    {"icon": icon_mosquito, "accent": (63, 143, 47),
     "lines": ["MOSQUITOES CUT", "DENGUE BY 69%"],
     "sub": "Bacterium trial in Brazil"},
    {"icon": icon_probe, "accent": (68, 88, 110),
     "lines": ["PROBE REACHES", "MERCURY ORBIT"],
     "sub": "BepiColombo after 8-year flight"},
    {"icon": icon_tent, "accent": (138, 90, 43),
     "lines": ["700,000 DISPLACED", "IN ETHIOPIA"],
     "sub": "Fighting in the south"},
    {"icon": icon_flag, "accent": (20, 24, 29),
     "lines": ["VERSTAPPEN TAKES", "VEGAS POLE"],
     "sub": "Las Vegas Grand Prix qualifying"},
]


# ------------------------------------------------------------- rendering

def accent_strip(d, x, y, w, col):
    d.rectangle([x + 5, y + 5, x + w - 5, y + 19], fill=col)


def hero(d, x, y, w, h, story):
    d.rounded_rectangle([x, y, x + w, y + h], radius=20, fill=PANEL,
                        outline=INK, width=4)
    accent_strip(d, x, y, w, story["accent"])
    story["icon"](d, x + 250, y + h // 2 + 16, 118, story["accent"])
    tx = x + 520
    d.text((tx, y + 52), story["kicker"], font=font(BOLD, 40), fill=RED)
    ly = y + 118
    for ln in story["lines"]:
        d.text((tx, ly), ln, font=font(BOLD, 78), fill=INK)
        ly += 94
    sy = ly + 18
    for ln in story["sub_lines"]:
        d.text((tx, sy), ln, font=font(REG, 42), fill=GRAY)
        sy += 54


def panel(d, x, y, w, h, story):
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=PANEL,
                        outline=INK, width=3)
    accent_strip(d, x, y, w, story["accent"])
    story["icon"](d, x + w // 2, y + 116, 60, story["accent"])
    ly = y + 196
    for ln in story["lines"]:
        centered(d, x + w // 2, ly, ln, font(BOLD, 47), INK)
        ly += 57
    centered(d, x + w // 2, y + h - 56, story["sub"], font(REG, 32), GRAY)


def build():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    centered(d, W // 2, 44, "THE WORLD IN ONE PICTURE", font(BOLD, 44), INK)
    d.rectangle([56, 116, W - 56, 124], fill=RED)
    centered(d, W // 2, 140, "SATURDAY, 21 NOVEMBER 2026", font(BOLD, 96), INK)
    d.rectangle([56, 272, W - 56, 278], fill=INK)

    # hero story
    hero(d, 56, 316, W - 112, 400, HERO_STORY)

    # 3x3 grid of panels
    gx, gy, gw, gh, gap = 56, 748, 620, 380, 28
    for i, story in enumerate(STORIES):
        px = gx + (i % 3) * (gw + gap)
        py = gy + (i // 3) * (gh + gap)
        panel(d, px, py, gw, gh, story)

    # footer
    centered(d, W // 2, 1972,
             "All events reported on 21 November 2026 · Compiled from wire "
             "and world reports", font(REG, 30), GRAY)

    img = img.resize((1024, 1024), Image.LANCZOS)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    print(build())
