from pathlib import Path
from math import cos, sin, pi
import random

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets"
OUT_FILE = ROOT / "小学生手卫生.pptx"

IMG_W, IMG_H = 1600, 900
SLIDE_W, SLIDE_H = 13.333333, 7.5

PALETTE = {
    "blue": (119, 205, 255),
    "deep_blue": (48, 130, 220),
    "mint": (143, 224, 188),
    "green": (92, 184, 92),
    "yellow": (255, 220, 97),
    "orange": (255, 166, 77),
    "pink": (255, 150, 186),
    "purple": (168, 144, 255),
    "cream": (255, 248, 220),
    "white": (255, 255, 255),
    "ink": (53, 75, 95),
    "skin": (255, 204, 164),
    "skin_shadow": (238, 174, 132),
    "soap": (126, 214, 223),
    "water": (68, 188, 255),
}


def blend(c1, c2, t):
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


def gradient_background(top, bottom):
    img = Image.new("RGB", (IMG_W, IMG_H), top)
    draw = ImageDraw.Draw(img)
    for y in range(IMG_H):
        color = blend(top, bottom, y / (IMG_H - 1))
        draw.line([(0, y), (IMG_W, y)], fill=color)
    return img, draw


def add_confetti(draw, seed, density=70):
    random.seed(seed)
    colors = [
        PALETTE["yellow"],
        PALETTE["pink"],
        PALETTE["mint"],
        PALETTE["purple"],
        PALETTE["orange"],
        PALETTE["blue"],
    ]
    for _ in range(density):
        x = random.randint(10, IMG_W - 10)
        y = random.randint(10, IMG_H - 10)
        r = random.randint(4, 12)
        color = random.choice(colors)
        if random.random() < 0.45:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=(255, 255, 255), width=2)
        else:
            draw.rounded_rectangle((x - r, y - r, x + r, y + r), radius=4, fill=color)


def star_points(cx, cy, outer, inner, points=5):
    pts = []
    for i in range(points * 2):
        angle = -pi / 2 + i * pi / points
        radius = outer if i % 2 == 0 else inner
        pts.append((cx + cos(angle) * radius, cy + sin(angle) * radius))
    return pts


def draw_star(draw, cx, cy, size, fill=PALETTE["yellow"]):
    draw.polygon(star_points(cx, cy, size, size * 0.45), fill=fill, outline=(255, 255, 255))


def draw_bubble(draw, cx, cy, r, fill=(255, 255, 255), outline=(120, 210, 255), width=4):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=width)
    draw.ellipse((cx - r * 0.35, cy - r * 0.35, cx - r * 0.08, cy - r * 0.08), fill=(255, 255, 255))


def draw_drop(draw, cx, cy, s, fill=None, outline=None):
    fill = fill or PALETTE["water"]
    outline = outline or (255, 255, 255)
    pts = [
        (cx, cy - 1.25 * s),
        (cx - 0.72 * s, cy - 0.18 * s),
        (cx - 0.55 * s, cy + 0.62 * s),
        (cx, cy + 0.92 * s),
        (cx + 0.55 * s, cy + 0.62 * s),
        (cx + 0.72 * s, cy - 0.18 * s),
    ]
    draw.polygon(pts, fill=fill, outline=outline)
    draw.ellipse((cx - 0.2 * s, cy - 0.48 * s, cx + 0.08 * s, cy - 0.2 * s), fill=(210, 245, 255))


def draw_germ(draw, cx, cy, r, color=(130, 220, 110), mood="smile"):
    outline = (77, 128, 85)
    for i in range(10):
        angle = i * 2 * pi / 10
        x1 = cx + cos(angle) * r * 0.8
        y1 = cy + sin(angle) * r * 0.8
        x2 = cx + cos(angle) * r * 1.28
        y2 = cy + sin(angle) * r * 1.28
        draw.line((x1, y1, x2, y2), fill=outline, width=max(3, int(r * 0.08)))
        draw.ellipse((x2 - r * 0.14, y2 - r * 0.14, x2 + r * 0.14, y2 + r * 0.14), fill=color, outline=outline, width=2)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color, outline=outline, width=max(4, int(r * 0.08)))
    eye_y = cy - r * 0.18
    for ex in (cx - r * 0.35, cx + r * 0.35):
        draw.ellipse((ex - r * 0.13, eye_y - r * 0.13, ex + r * 0.13, eye_y + r * 0.13), fill=(45, 55, 65))
        draw.ellipse((ex - r * 0.05, eye_y - r * 0.07, ex, eye_y - r * 0.02), fill=(255, 255, 255))
    if mood == "wow":
        draw.ellipse((cx - r * 0.18, cy + r * 0.18, cx + r * 0.18, cy + r * 0.52), fill=(45, 55, 65))
    elif mood == "sad":
        draw.arc((cx - r * 0.42, cy + r * 0.28, cx + r * 0.42, cy + r * 0.85), 200, 340, fill=(45, 55, 65), width=4)
    else:
        draw.arc((cx - r * 0.42, cy - r * 0.05, cx + r * 0.42, cy + r * 0.58), 20, 160, fill=(45, 55, 65), width=4)


def draw_hand(draw, cx, cy, scale=1.0, angle=0, outline=(196, 130, 100)):
    # A friendly cartoon hand built from rounded shapes.
    s = scale
    palm = (cx - 72 * s, cy - 15 * s, cx + 72 * s, cy + 125 * s)
    draw.rounded_rectangle(palm, radius=int(38 * s), fill=PALETTE["skin"], outline=outline, width=int(5 * s))
    finger_w = 34 * s
    starts = [-58, -20, 18, 55]
    heights = [116, 142, 132, 102]
    for dx, h in zip(starts, heights):
        draw.rounded_rectangle(
            (cx + dx * s - finger_w / 2, cy - h * s, cx + dx * s + finger_w / 2, cy + 15 * s),
            radius=int(18 * s),
            fill=PALETTE["skin"],
            outline=outline,
            width=int(5 * s),
        )
    draw.rounded_rectangle(
        (cx - 115 * s, cy + 18 * s, cx - 52 * s, cy + 64 * s),
        radius=int(24 * s),
        fill=PALETTE["skin"],
        outline=outline,
        width=int(5 * s),
    )
    for dx in starts:
        draw.arc((cx + dx * s - 12 * s, cy - 16 * s, cx + dx * s + 12 * s, cy + 18 * s), 0, 180, fill=PALETTE["skin_shadow"], width=max(2, int(3 * s)))
    return palm


def draw_soap(draw, cx, cy, scale=1.0, color=None):
    s = scale
    color = color or PALETTE["soap"]
    draw.rounded_rectangle((cx - 95 * s, cy - 52 * s, cx + 95 * s, cy + 52 * s), radius=int(35 * s), fill=color, outline=(56, 151, 173), width=int(5 * s))
    draw.arc((cx - 53 * s, cy - 18 * s, cx + 53 * s, cy + 28 * s), 10, 170, fill=(230, 255, 255), width=max(3, int(6 * s)))
    for dx, dy, r in [(-80, -58, 18), (84, -60, 24), (20, -76, 14), (-18, 68, 13)]:
        draw_bubble(draw, cx + dx * s, cy + dy * s, r * s, fill=(239, 255, 255), width=max(2, int(3 * s)))


def draw_faucet(draw, x, y, scale=1.0):
    s = scale
    metal = (145, 185, 210)
    dark = (77, 125, 157)
    draw.rounded_rectangle((x, y, x + 240 * s, y + 52 * s), radius=int(25 * s), fill=metal, outline=dark, width=int(5 * s))
    draw.rounded_rectangle((x + 172 * s, y + 34 * s, x + 222 * s, y + 126 * s), radius=int(18 * s), fill=metal, outline=dark, width=int(5 * s))
    draw.rounded_rectangle((x + 40 * s, y - 52 * s, x + 92 * s, y + 16 * s), radius=int(16 * s), fill=metal, outline=dark, width=int(5 * s))
    draw.ellipse((x + 28 * s, y - 78 * s, x + 104 * s, y - 32 * s), fill=(255, 126, 126), outline=dark, width=int(4 * s))
    for i in range(4):
        xx = x + (185 + i * 12) * s
        draw.line((xx, y + 126 * s, xx - 18 * s, y + 320 * s), fill=PALETTE["water"], width=max(5, int(9 * s)))
        draw_drop(draw, xx - 20 * s, y + (170 + i * 42) * s, 12 * s)


def draw_child(draw, cx, cy, scale=1.0, shirt=None, pose="wave"):
    s = scale
    shirt = shirt or PALETTE["yellow"]
    ink = PALETTE["ink"]
    # legs and shoes
    draw.rounded_rectangle((cx - 48 * s, cy + 120 * s, cx - 18 * s, cy + 226 * s), radius=int(12 * s), fill=(80, 140, 224), outline=ink, width=int(4 * s))
    draw.rounded_rectangle((cx + 18 * s, cy + 120 * s, cx + 48 * s, cy + 226 * s), radius=int(12 * s), fill=(80, 140, 224), outline=ink, width=int(4 * s))
    draw.ellipse((cx - 74 * s, cy + 214 * s, cx - 8 * s, cy + 242 * s), fill=(255, 255, 255), outline=ink, width=int(4 * s))
    draw.ellipse((cx + 8 * s, cy + 214 * s, cx + 74 * s, cy + 242 * s), fill=(255, 255, 255), outline=ink, width=int(4 * s))
    # body
    draw.rounded_rectangle((cx - 82 * s, cy + 20 * s, cx + 82 * s, cy + 148 * s), radius=int(38 * s), fill=shirt, outline=ink, width=int(5 * s))
    # arms
    if pose == "wash":
        draw.line((cx - 75 * s, cy + 58 * s, cx - 150 * s, cy + 106 * s), fill=PALETTE["skin"], width=int(25 * s))
        draw.line((cx + 75 * s, cy + 58 * s, cx + 150 * s, cy + 106 * s), fill=PALETTE["skin"], width=int(25 * s))
    else:
        draw.line((cx - 74 * s, cy + 62 * s, cx - 150 * s, cy + 10 * s), fill=PALETTE["skin"], width=int(25 * s))
        draw.line((cx + 74 * s, cy + 62 * s, cx + 138 * s, cy + 120 * s), fill=PALETTE["skin"], width=int(25 * s))
    draw.ellipse((cx - 166 * s, cy - 6 * s, cx - 126 * s, cy + 34 * s), fill=PALETTE["skin"], outline=ink, width=int(3 * s))
    draw.ellipse((cx + 120 * s, cy + 102 * s, cx + 160 * s, cy + 142 * s), fill=PALETTE["skin"], outline=ink, width=int(3 * s))
    # head and hair
    draw.ellipse((cx - 78 * s, cy - 126 * s, cx + 78 * s, cy + 30 * s), fill=PALETTE["skin"], outline=ink, width=int(5 * s))
    draw.pieslice((cx - 80 * s, cy - 138 * s, cx + 80 * s, cy - 24 * s), 185, 355, fill=(83, 56, 44), outline=(83, 56, 44))
    for ex in (cx - 30 * s, cx + 30 * s):
        draw.ellipse((ex - 8 * s, cy - 52 * s, ex + 8 * s, cy - 36 * s), fill=ink)
    draw.arc((cx - 34 * s, cy - 38 * s, cx + 34 * s, cy + 4 * s), 18, 162, fill=(204, 78, 88), width=int(4 * s))
    draw.ellipse((cx - 52 * s, cy - 28 * s, cx - 34 * s, cy - 10 * s), fill=(255, 150, 150))
    draw.ellipse((cx + 34 * s, cy - 28 * s, cx + 52 * s, cy - 10 * s), fill=(255, 150, 150))


def draw_clipboard(draw, x, y, scale=1.0):
    s = scale
    draw.rounded_rectangle((x, y, x + 260 * s, y + 350 * s), radius=int(28 * s), fill=(255, 251, 226), outline=PALETTE["ink"], width=int(6 * s))
    draw.rounded_rectangle((x + 70 * s, y - 28 * s, x + 190 * s, y + 36 * s), radius=int(18 * s), fill=PALETTE["orange"], outline=PALETTE["ink"], width=int(5 * s))
    for i in range(5):
        yy = y + (82 + i * 48) * s
        draw.rounded_rectangle((x + 38 * s, yy - 13 * s, x + 64 * s, yy + 13 * s), radius=int(7 * s), fill=PALETTE["mint"], outline=PALETTE["ink"], width=int(3 * s))
        draw.line((x + 86 * s, yy, x + 220 * s, yy), fill=(120, 140, 160), width=int(4 * s))


def save_img(img, name):
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    path = ASSET_DIR / name
    img.save(path)
    return path


def slide01():
    img, d = gradient_background((196, 239, 255), (255, 245, 199))
    add_confetti(d, 1, 90)
    # rainbow
    for i, col in enumerate([(255, 121, 121), (255, 184, 77), (255, 228, 89), (116, 209, 110), (82, 185, 255), (157, 139, 255)]):
        d.arc((135, 150 + i * 18, 730, 705 + i * 18), 190, 345, fill=col, width=18)
    d.rounded_rectangle((420, 520, 1180, 780), radius=95, fill=(245, 253, 255), outline=(117, 191, 225), width=10)
    draw_faucet(d, 680, 310, 0.95)
    draw_child(d, 410, 480, 1.05, PALETTE["pink"], pose="wash")
    draw_child(d, 1190, 480, 1.05, PALETTE["mint"], pose="wash")
    draw_hand(d, 705, 585, 0.75)
    draw_hand(d, 885, 595, 0.75)
    draw_soap(d, 1010, 720, 0.65, PALETTE["purple"])
    for x, y, r in [(690, 520, 35), (815, 500, 52), (910, 520, 32), (1010, 590, 38), (585, 610, 34), (1115, 350, 44), (255, 245, 34)]:
        draw_bubble(d, x, y, r, fill=(245, 255, 255))
    for x, y in [(1280, 130), (1430, 230), (230, 680), (1330, 720)]:
        draw_star(d, x, y, 28)
    return save_img(img, "slide01_cover.png")


def slide02():
    img, d = gradient_background((255, 247, 219), (215, 243, 255))
    add_confetti(d, 2, 55)
    cards = [
        (100, 130, PALETTE["pink"]),
        (475, 130, PALETTE["yellow"]),
        (850, 130, PALETTE["mint"]),
        (1225, 130, PALETTE["purple"]),
        (290, 515, PALETTE["orange"]),
        (675, 515, PALETTE["blue"]),
        (1060, 515, PALETTE["green"]),
    ]
    for idx, (x, y, c) in enumerate(cards):
        d.rounded_rectangle((x, y, x + 260, y + 240), radius=42, fill=(255, 255, 255), outline=c, width=9)
        if idx == 0:
            # book and pencil
            d.rectangle((x + 62, y + 65, x + 200, y + 165), fill=(120, 180, 255), outline=PALETTE["ink"], width=5)
            d.line((x + 131, y + 65, x + 131, y + 165), fill=(255, 255, 255), width=4)
            d.polygon([(x + 72, y + 185), (x + 205, y + 135), (x + 218, y + 164), (x + 85, y + 214)], fill=PALETTE["yellow"], outline=PALETTE["ink"])
        elif idx == 1:
            # blocks
            for j, col in enumerate([PALETTE["pink"], PALETTE["mint"], PALETTE["orange"]]):
                xx = x + 55 + j * 58
                yy = y + 135 - j * 35
                d.rounded_rectangle((xx, yy, xx + 72, yy + 72), radius=12, fill=col, outline=PALETTE["ink"], width=4)
        elif idx == 2:
            # ball
            d.ellipse((x + 62, y + 58, x + 198, y + 194), fill=PALETTE["orange"], outline=PALETTE["ink"], width=5)
            d.arc((x + 72, y + 68, x + 188, y + 184), 60, 240, fill=(255, 255, 255), width=6)
            d.line((x + 130, y + 58, x + 130, y + 194), fill=(255, 255, 255), width=6)
        elif idx == 3:
            # door handle
            d.rounded_rectangle((x + 86, y + 50, x + 180, y + 198), radius=16, fill=(203, 158, 105), outline=PALETTE["ink"], width=5)
            d.ellipse((x + 118, y + 105, x + 202, y + 152), fill=PALETTE["yellow"], outline=PALETTE["ink"], width=5)
        elif idx == 4:
            # apple
            d.ellipse((x + 78, y + 88, x + 152, y + 180), fill=(232, 70, 85), outline=PALETTE["ink"], width=4)
            d.ellipse((x + 122, y + 88, x + 196, y + 180), fill=(232, 70, 85), outline=PALETTE["ink"], width=4)
            d.line((x + 135, y + 83, x + 155, y + 47), fill=(104, 76, 54), width=7)
            d.ellipse((x + 155, y + 42, x + 205, y + 76), fill=PALETTE["green"], outline=PALETTE["ink"], width=3)
        elif idx == 5:
            # pet paw
            d.ellipse((x + 76, y + 95, x + 188, y + 205), fill=(255, 255, 255), outline=PALETTE["ink"], width=5)
            for px, py in [(72, 82), (112, 55), (152, 55), (192, 82)]:
                d.ellipse((x + px - 20, y + py - 20, x + px + 20, y + py + 20), fill=(255, 255, 255), outline=PALETTE["ink"], width=4)
        else:
            # water cup
            d.rounded_rectangle((x + 80, y + 52, x + 180, y + 200), radius=22, fill=(160, 220, 255), outline=PALETTE["ink"], width=5)
            d.arc((x + 165, y + 90, x + 230, y + 160), -80, 80, fill=PALETTE["ink"], width=6)
        for gx, gy in [(x + 212, y + 48), (x + 40, y + 206)]:
            draw_germ(d, gx, gy, 23, random.choice([(122, 220, 109), (255, 150, 186), (168, 144, 255)]))
    d.line((230, 440, 1360, 440), fill=(255, 190, 92), width=14)
    for x in [230, 475, 730, 980, 1220, 1360]:
        draw_drop(d, x, 440, 22, fill=PALETTE["orange"])
    return save_img(img, "slide02_busy_hands.png")


def slide03():
    img, d = gradient_background((226, 249, 255), (255, 236, 245))
    add_confetti(d, 3, 60)
    draw_hand(d, 705, 520, 2.0)
    # magnifying glass
    d.ellipse((760, 120, 1340, 700), fill=(235, 252, 255), outline=PALETTE["deep_blue"], width=18)
    d.line((1210, 635, 1460, 825), fill=PALETTE["deep_blue"], width=38)
    d.line((1224, 620, 1474, 810), fill=(255, 255, 255), width=8)
    germ_specs = [
        (950, 300, 54, (126, 224, 110), "smile"),
        (1090, 420, 42, (255, 164, 83), "wow"),
        (875, 515, 38, (255, 146, 186), "smile"),
        (1205, 530, 50, (160, 144, 255), "smile"),
        (1035, 610, 34, (100, 210, 225), "wow"),
    ]
    for spec in germ_specs:
        draw_germ(d, *spec)
    draw_child(d, 305, 560, 1.0, PALETTE["yellow"], pose="wave")
    for x, y, r in [(118, 168, 40), (208, 260, 28), (1406, 155, 44), (1410, 670, 28)]:
        draw_bubble(d, x, y, r)
    return save_img(img, "slide03_tiny_germs.png")


def slide04():
    img, d = gradient_background((235, 252, 239), (221, 238, 255))
    add_confetti(d, 4, 80)
    # shield
    shield = [(800, 130), (1120, 235), (1080, 555), (800, 745), (520, 555), (480, 235)]
    d.polygon(shield, fill=(255, 245, 132), outline=PALETTE["deep_blue"])
    d.line(shield + [shield[0]], fill=PALETTE["deep_blue"], width=15)
    d.polygon(star_points(800, 410, 110, 48), fill=(255, 168, 69), outline=(255, 255, 255))
    draw_hand(d, 800, 470, 1.25)
    for gx, gy, r, c in [
        (245, 230, 55, (122, 220, 109)),
        (322, 620, 44, (255, 145, 185)),
        (1340, 285, 58, (160, 144, 255)),
        (1270, 670, 45, (255, 170, 80)),
    ]:
        draw_germ(d, gx, gy, r, c, "sad")
        d.line((gx, gy, 800, 420), fill=(255, 255, 255), width=5)
    for x, y in [(210, 735), (1430, 130), (500, 110), (1120, 780)]:
        draw_star(d, x, y, 32)
    draw_soap(d, 245, 470, 0.75)
    draw_drop(d, 1360, 480, 48)
    return save_img(img, "slide04_health_shield.png")


def slide05():
    img, d = gradient_background((255, 249, 221), (221, 247, 255))
    add_confetti(d, 5, 70)
    draw_child(d, 800, 475, 1.05, PALETTE["mint"], pose="wave")
    centers = [(320, 200), (620, 170), (980, 170), (1280, 225), (430, 675), (1135, 685)]
    colors = [PALETTE["pink"], PALETTE["yellow"], PALETTE["orange"], PALETTE["blue"], PALETTE["purple"], PALETTE["green"]]
    for i, (cx, cy) in enumerate(centers):
        d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), fill=(255, 255, 255), outline=colors[i], width=10)
    # meal
    d.ellipse((240, 145, 400, 245), fill=(255, 255, 255), outline=PALETTE["ink"], width=5)
    d.ellipse((285, 170, 355, 220), fill=(255, 220, 97), outline=PALETTE["ink"], width=4)
    d.line((415, 135, 415, 265), fill=PALETTE["ink"], width=7)
    d.line((435, 145, 435, 255), fill=PALETTE["ink"], width=7)
    # toilet
    d.rounded_rectangle((570, 118, 670, 200), radius=20, fill=(210, 240, 255), outline=PALETTE["ink"], width=5)
    d.rounded_rectangle((590, 195, 690, 260), radius=28, fill=(230, 250, 255), outline=PALETTE["ink"], width=5)
    # sneeze
    draw_child(d, 980, 180, 0.38, PALETTE["yellow"])
    for x in [1060, 1095, 1130]:
        draw_drop(d, x, 175 + (x - 1060) * 0.15, 12, fill=PALETTE["blue"])
    # playground
    d.arc((1210, 170, 1350, 330), 180, 360, fill=PALETTE["deep_blue"], width=9)
    d.line((1210, 250, 1210, 330), fill=PALETTE["deep_blue"], width=9)
    d.line((1350, 250, 1350, 330), fill=PALETTE["deep_blue"], width=9)
    d.ellipse((1245, 210, 1315, 280), fill=PALETTE["orange"], outline=PALETTE["ink"], width=4)
    # pet
    d.ellipse((360, 650, 500, 760), fill=(255, 255, 255), outline=PALETTE["ink"], width=5)
    for px, py in [(350, 625), (400, 595), (455, 595), (505, 625)]:
        d.ellipse((px - 28, py - 28, px + 28, py + 28), fill=(255, 255, 255), outline=PALETTE["ink"], width=5)
    # home/school
    d.polygon([(1050, 690), (1135, 610), (1220, 690)], fill=PALETTE["orange"], outline=PALETTE["ink"])
    d.rounded_rectangle((1075, 690, 1195, 775), radius=12, fill=(255, 255, 255), outline=PALETTE["ink"], width=5)
    d.rounded_rectangle((1120, 725, 1150, 775), radius=7, fill=PALETTE["mint"], outline=PALETTE["ink"], width=3)
    for x, y in [(160, 420), (1430, 515), (760, 90), (830, 790)]:
        draw_bubble(d, x, y, 28)
    return save_img(img, "slide05_when_to_wash.png")


def slide06():
    img, d = gradient_background((236, 248, 255), (251, 238, 255))
    add_confetti(d, 6, 55)
    centers = [(270, 250), (555, 200), (845, 215), (1130, 285), (1030, 610), (715, 670), (390, 600)]
    for i, (cx, cy) in enumerate(centers, 1):
        d.ellipse((cx - 105, cy - 105, cx + 105, cy + 105), fill=(255, 255, 255), outline=random.choice([PALETTE["pink"], PALETTE["mint"], PALETTE["orange"], PALETTE["purple"], PALETTE["blue"]]), width=8)
        draw_hand(d, cx - 14, cy - 6, 0.45)
        draw_hand(d, cx + 44, cy + 10, 0.45)
        d.ellipse((cx - 100, cy - 100, cx - 42, cy - 42), fill=PALETTE["yellow"], outline=PALETTE["ink"], width=4)
        # Use simple digits inside the illustration; Chinese labels are added in PPT.
        d.text((cx - 82, cy - 94), str(i), fill=PALETTE["ink"])
        for bx, by, r in [(cx + 78, cy - 72, 12), (cx + 92, cy + 8, 18), (cx - 86, cy + 75, 14)]:
            draw_bubble(d, bx, by, r, width=3)
    for i in range(len(centers) - 1):
        x1, y1 = centers[i]
        x2, y2 = centers[i + 1]
        d.line((x1, y1, x2, y2), fill=(122, 196, 255), width=10)
        draw_drop(d, (x1 + x2) / 2, (y1 + y2) / 2, 16)
    draw_soap(d, 1325, 650, 0.65, PALETTE["pink"])
    return save_img(img, "slide06_seven_steps.png")


def slide07():
    img, d = gradient_background((255, 245, 219), (226, 248, 255))
    add_confetti(d, 7, 80)
    # big timer
    d.ellipse((570, 110, 1030, 570), fill=(255, 255, 255), outline=PALETTE["deep_blue"], width=14)
    d.rounded_rectangle((725, 62, 875, 124), radius=26, fill=PALETTE["yellow"], outline=PALETTE["deep_blue"], width=7)
    d.line((800, 340, 800, 190), fill=PALETTE["orange"], width=14)
    d.line((800, 340, 915, 410), fill=PALETTE["orange"], width=14)
    for angle in range(0, 360, 30):
        x1 = 800 + cos(angle * pi / 180) * 185
        y1 = 340 + sin(angle * pi / 180) * 185
        x2 = 800 + cos(angle * pi / 180) * 205
        y2 = 340 + sin(angle * pi / 180) * 205
        d.line((x1, y1, x2, y2), fill=PALETTE["deep_blue"], width=5)
    for mx, my in [(285, 260), (375, 185), (1180, 250), (1270, 170), (1130, 500)]:
        d.ellipse((mx - 18, my - 18, mx + 18, my + 18), fill=PALETTE["purple"], outline=PALETTE["ink"], width=3)
        d.line((mx + 16, my - 8, mx + 16, my - 100), fill=PALETTE["purple"], width=8)
        d.arc((mx + 14, my - 115, mx + 84, my - 55), 180, 355, fill=PALETTE["purple"], width=8)
    draw_hand(d, 425, 645, 0.85)
    draw_soap(d, 610, 695, 0.72)
    draw_faucet(d, 960, 570, 0.75)
    for x, y, r in [(165, 625, 36), (245, 700, 24), (1390, 620, 42), (1215, 725, 30)]:
        draw_bubble(d, x, y, r)
    return save_img(img, "slide07_20_seconds.png")


def slide08():
    img, d = gradient_background((232, 255, 237), (255, 247, 216))
    add_confetti(d, 8, 65)
    # lab table
    d.rounded_rectangle((130, 640, 1470, 820), radius=38, fill=(255, 210, 142), outline=PALETTE["ink"], width=7)
    d.ellipse((420, 240, 910, 640), fill=(225, 246, 255), outline=PALETTE["deep_blue"], width=10)
    d.ellipse((480, 310, 850, 560), fill=(137, 214, 255), outline=(255, 255, 255), width=5)
    random.seed(80)
    for _ in range(80):
        x = random.randint(510, 820)
        y = random.randint(340, 530)
        if ((x - 665) / 185) ** 2 + ((y - 435) / 125) ** 2 < 1:
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(69, 78, 88))
    draw_soap(d, 1090, 500, 0.8, PALETTE["pink"])
    draw_hand(d, 1080, 270, 0.75)
    for angle in range(0, 360, 30):
        x1 = 665 + cos(angle * pi / 180) * 85
        y1 = 435 + sin(angle * pi / 180) * 58
        x2 = 665 + cos(angle * pi / 180) * 165
        y2 = 435 + sin(angle * pi / 180) * 112
        d.line((x1, y1, x2, y2), fill=(255, 255, 255), width=5)
    draw_child(d, 250, 485, 0.85, PALETTE["mint"], pose="wave")
    d.ellipse((1225, 150, 1455, 330), fill=(255, 255, 255), outline=PALETTE["orange"], width=8)
    d.line((1250, 270, 1430, 190), fill=PALETTE["orange"], width=12)
    for x, y in [(1260, 172), (1350, 155), (1425, 188), (1330, 295)]:
        draw_bubble(d, x, y, 18)
    return save_img(img, "slide08_science_experiment.png")


def slide09():
    img, d = gradient_background((255, 237, 237), (231, 248, 255))
    add_confetti(d, 9, 55)
    draw_child(d, 520, 510, 1.15, PALETTE["yellow"], pose="wave")
    # bent elbow/tissue
    d.rounded_rectangle((640, 405, 820, 505), radius=45, fill=PALETTE["skin"], outline=PALETTE["ink"], width=5)
    d.rounded_rectangle((785, 390, 910, 520), radius=25, fill=(255, 255, 255), outline=PALETTE["deep_blue"], width=5)
    for x, y, r, c in [(1030, 245, 43, (122, 220, 109)), (1175, 360, 38, (255, 150, 186)), (1080, 560, 34, (160, 144, 255))]:
        draw_germ(d, x, y, r, c, "wow")
    # stop sign
    d.rounded_rectangle((920, 225, 995, 620), radius=32, fill=(255, 255, 255), outline=PALETTE["orange"], width=9)
    for yy in [285, 405, 525]:
        d.line((935, yy, 980, yy), fill=PALETTE["orange"], width=11)
    # trash bin
    d.rounded_rectangle((1160, 640, 1325, 805), radius=25, fill=(185, 226, 201), outline=PALETTE["ink"], width=6)
    d.rectangle((1145, 612, 1340, 650), fill=(118, 175, 143), outline=PALETTE["ink"], width=5)
    d.rounded_rectangle((1195, 565, 1290, 625), radius=18, fill=(255, 255, 255), outline=PALETTE["ink"], width=4)
    for x, y, r in [(185, 175, 34), (270, 260, 24), (1370, 145, 36), (1425, 700, 28)]:
        draw_bubble(d, x, y, r)
    return save_img(img, "slide09_cough_etiquette.png")


def slide10():
    img, d = gradient_background((244, 241, 255), (222, 250, 241))
    add_confetti(d, 10, 70)
    draw_hand(d, 375, 470, 1.3)
    # nail clipper
    d.rounded_rectangle((585, 275, 860, 350), radius=22, fill=(180, 205, 220), outline=PALETTE["ink"], width=6)
    d.rounded_rectangle((645, 220, 875, 275), radius=18, fill=(220, 236, 245), outline=PALETTE["ink"], width=5)
    d.line((825, 240, 900, 175), fill=PALETTE["ink"], width=8)
    # bandage
    d.rounded_rectangle((750, 520, 1060, 635), radius=45, fill=(255, 207, 164), outline=PALETTE["ink"], width=6)
    d.rounded_rectangle((875, 545, 940, 610), radius=14, fill=(255, 236, 204), outline=(190, 130, 100), width=3)
    for x in [805, 842, 985, 1022]:
        d.ellipse((x - 8, 572, x + 8, 588), fill=(220, 160, 130))
    # personal items
    d.rounded_rectangle((1180, 175, 1325, 480), radius=32, fill=(130, 215, 255), outline=PALETTE["ink"], width=6)
    d.arc((1305, 260, 1410, 385), -90, 90, fill=PALETTE["ink"], width=8)
    d.rounded_rectangle((1180, 545, 1355, 760), radius=45, fill=(255, 255, 255), outline=PALETTE["pink"], width=8)
    for yy in [585, 630, 675, 720]:
        d.line((1210, yy, 1320, yy), fill=(255, 190, 210), width=7)
    for x, y in [(145, 195), (1015, 160), (1450, 485), (695, 745)]:
        draw_star(d, x, y, 26)
    return save_img(img, "slide10_clean_habits.png")


def slide11():
    img, d = gradient_background((235, 250, 255), (255, 244, 226))
    add_confetti(d, 11, 70)
    # school map
    d.rounded_rectangle((100, 115, 900, 760), radius=45, fill=(255, 255, 255), outline=PALETTE["deep_blue"], width=9)
    rooms = [
        (150, 170, 360, 330, PALETTE["yellow"]),
        (405, 170, 615, 330, PALETTE["mint"]),
        (660, 170, 850, 330, PALETTE["pink"]),
        (150, 380, 360, 560, PALETTE["orange"]),
        (405, 380, 615, 560, PALETTE["blue"]),
        (660, 380, 850, 560, PALETTE["purple"]),
    ]
    for x1, y1, x2, y2, col in rooms:
        d.rounded_rectangle((x1, y1, x2, y2), radius=26, fill=col, outline=PALETTE["ink"], width=4)
        draw_drop(d, (x1 + x2) / 2, (y1 + y2) / 2, 22, fill=(255, 255, 255), outline=PALETTE["ink"])
    d.line((250, 625, 780, 625), fill=(255, 194, 89), width=16)
    for x in [250, 410, 580, 780]:
        d.ellipse((x - 20, 605, x + 20, 645), fill=PALETTE["yellow"], outline=PALETTE["ink"], width=3)
    draw_clipboard(d, 1075, 210, 1.0)
    draw_child(d, 1005, 615, 0.75, PALETTE["pink"], pose="wave")
    d.ellipse((930, 130, 1070, 270), fill=(230, 255, 255), outline=PALETTE["deep_blue"], width=8)
    d.line((1040, 250, 1125, 330), fill=PALETTE["deep_blue"], width=18)
    for x, y in [(1300, 110), (1425, 720), (90, 790), (960, 790)]:
        draw_star(d, x, y, 25)
    return save_img(img, "slide11_school_detective.png")


def slide12():
    img, d = gradient_background((220, 245, 255), (255, 246, 214))
    add_confetti(d, 12, 100)
    d.polygon([(250, 640), (1350, 640), (1460, 820), (140, 820)], fill=(255, 255, 255), outline=PALETTE["deep_blue"])
    draw_child(d, 430, 465, 1.05, PALETTE["pink"], pose="wave")
    draw_child(d, 800, 450, 1.18, PALETTE["yellow"], pose="wave")
    draw_child(d, 1180, 465, 1.05, PALETTE["mint"], pose="wave")
    for cx, cy, col in [(430, 210, PALETTE["pink"]), (800, 175, PALETTE["yellow"]), (1180, 210, PALETTE["mint"])]:
        d.polygon(star_points(cx, cy, 78, 35), fill=col, outline=PALETTE["ink"])
        draw_drop(d, cx, cy, 28, fill=PALETTE["water"], outline=PALETTE["ink"])
    draw_soap(d, 230, 550, 0.8, PALETTE["purple"])
    draw_faucet(d, 1280, 510, 0.6)
    for x, y, r in [(170, 170, 42), (285, 260, 30), (1395, 185, 42), (1305, 300, 28), (710, 755, 35), (945, 730, 28)]:
        draw_bubble(d, x, y, r)
    return save_img(img, "slide12_pledge.png")


def add_bg(slide, img_path):
    slide.shapes.add_picture(str(img_path), 0, 0, width=Inches(SLIDE_W), height=Inches(SLIDE_H))


def set_text_style(run, size=24, bold=False, color=(53, 75, 95)):
    run.font.name = "Microsoft YaHei"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)


def add_box(slide, x, y, w, h, fill=(255, 255, 255), outline=(255, 255, 255), transparency=8, radius=True):
    shape_type = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    box = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(*fill)
    box.fill.transparency = transparency
    box.line.color.rgb = RGBColor(*outline)
    box.line.width = Pt(2)
    return box


def add_text(slide, x, y, w, h, text, size=24, bold=False, color=(53, 75, 95), align=PP_ALIGN.LEFT):
    tx = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tx.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = align
    p.text = text
    for run in p.runs:
        set_text_style(run, size, bold, color)
    return tx


def add_title(slide, title, subtitle=None):
    add_box(slide, 0.45, 0.28, 12.45, 0.88, fill=(255, 255, 255), outline=(255, 220, 97), transparency=2)
    add_text(slide, 0.72, 0.35, 11.9, 0.55, title, size=28, bold=True, color=(38, 99, 170), align=PP_ALIGN.CENTER)
    if subtitle:
        add_text(slide, 0.95, 0.88, 11.4, 0.26, subtitle, size=12, bold=False, color=(85, 107, 130), align=PP_ALIGN.CENTER)


def add_footer(slide, page):
    add_box(slide, 11.95, 7.05, 0.85, 0.28, fill=(255, 255, 255), outline=(122, 196, 255), transparency=18)
    add_text(slide, 12.05, 7.08, 0.65, 0.18, str(page), size=10, bold=True, color=(38, 99, 170), align=PP_ALIGN.CENTER)


def add_bullets(slide, x, y, w, h, bullets, size=20, fill=(255, 255, 255), color=(53, 75, 95)):
    add_box(slide, x, y, w, h, fill=fill, outline=(255, 255, 255), transparency=7)
    tx = slide.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.12), Inches(w - 0.36), Inches(h - 0.18))
    tf = tx.text_frame
    tf.clear()
    tf.word_wrap = True
    for idx, text in enumerate(bullets):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = "• " + text
        p.space_after = Pt(6)
        p.line_spacing = 1.15
        for run in p.runs:
            set_text_style(run, size, False, color)


def add_card(slide, x, y, w, h, text, fill, size=18):
    add_box(slide, x, y, w, h, fill=fill, outline=(255, 255, 255), transparency=0)
    add_text(slide, x + 0.08, y + 0.08, w - 0.16, h - 0.16, text, size=size, bold=True, color=(53, 75, 95), align=PP_ALIGN.CENTER)


def build_ppt(image_paths):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    blank = prs.slide_layouts[6]

    slides = []
    for path in image_paths:
        slide = prs.slides.add_slide(blank)
        add_bg(slide, path)
        slides.append(slide)

    # 1
    add_box(slides[0], 2.1, 0.65, 9.15, 1.95, fill=(255, 255, 255), outline=(255, 220, 97), transparency=0)
    add_text(slides[0], 2.35, 0.82, 8.65, 0.78, "小学生手卫生", size=44, bold=True, color=(38, 99, 170), align=PP_ALIGN.CENTER)
    add_text(slides[0], 2.55, 1.65, 8.25, 0.43, "二年级健康科普课：和泡泡一起打败细菌小怪兽", size=18, bold=True, color=(240, 118, 88), align=PP_ALIGN.CENTER)
    add_card(slides[0], 5.05, 6.45, 3.25, 0.58, "准备好了吗？伸出小手！", (255, 242, 151), size=17)
    add_footer(slides[0], 1)

    # 2
    add_title(slides[1], "小手每天很忙")
    add_bullets(slides[1], 0.55, 1.35, 3.8, 2.35, [
        "写字、玩耍、摸门把手，小手到处帮忙。",
        "看不见的小细菌，也可能悄悄搭便车。",
        "别担心！学会洗手，小手就能变清爽。"
    ], size=18)
    add_card(slides[1], 4.65, 6.55, 4.05, 0.55, "想一想：今天你的小手碰过什么？", (255, 242, 151), size=16)
    add_footer(slides[1], 2)

    # 3
    add_title(slides[2], "细菌病毒在哪里？")
    add_bullets(slides[2], 0.55, 1.35, 4.15, 2.7, [
        "它们很小很小，肉眼看不见。",
        "喜欢躲在手指缝、指甲边和手心里。",
        "有些会让我们肚子疼、咳嗽或发烧。"
    ], size=18, fill=(255, 255, 255))
    add_card(slides[2], 0.78, 4.35, 3.55, 0.58, "不是所有细菌都坏，但脏手要洗干净！", (220, 250, 241), size=15)
    add_footer(slides[2], 3)

    # 4
    add_title(slides[3], "洗手像给身体加护盾")
    add_bullets(slides[3], 0.65, 1.45, 3.9, 2.45, [
        "洗掉灰尘、油油和脏东西。",
        "减少细菌从手跑到口、眼、鼻。",
        "保护自己，也保护同学和家人。"
    ], size=18, fill=(255, 255, 255))
    add_card(slides[3], 9.25, 6.35, 3.35, 0.62, "干净小手 = 健康加分", (255, 242, 151), size=18)
    add_footer(slides[3], 4)

    # 5
    add_title(slides[4], "这些时候一定要洗手")
    wash_times = [
        ("吃东西前", 1.02, 1.98, (255, 230, 236)),
        ("上厕所后", 3.55, 1.75, (255, 245, 181)),
        ("咳嗽喷嚏后", 6.6, 1.75, (255, 222, 191)),
        ("户外玩耍后", 9.38, 2.15, (221, 242, 255)),
        ("摸宠物后", 1.98, 6.06, (235, 226, 255)),
        ("回家或进教室后", 8.28, 6.1, (220, 250, 230)),
    ]
    for text, x, y, fill in wash_times:
        add_card(slides[4], x, y, 2.1, 0.48, text, fill, size=14)
    add_footer(slides[4], 5)

    # 6
    add_title(slides[5], "七步洗手法：小手面面俱到")
    steps = [
        "1 掌心相对搓一搓",
        "2 手背交叉搓一搓",
        "3 手指交叉搓一搓",
        "4 弯弯指背搓一搓",
        "5 大拇指转一转",
        "6 指尖掌心画圈圈",
        "7 手腕也要洗干净",
    ]
    add_bullets(slides[5], 9.15, 1.35, 3.55, 4.55, steps, size=15, fill=(255, 255, 255))
    add_card(slides[5], 4.65, 6.9, 4.15, 0.42, "每一步都搓到，细菌没处躲！", (255, 242, 151), size=15)
    add_footer(slides[5], 6)

    # 7
    add_title(slides[6], "洗手小口诀")
    add_card(slides[6], 0.65, 1.45, 2.05, 0.82, "湿一湿", (221, 242, 255), size=22)
    add_card(slides[6], 0.65, 2.55, 2.05, 0.82, "抹香皂", (235, 226, 255), size=22)
    add_card(slides[6], 0.65, 3.65, 2.05, 0.82, "搓20秒", (255, 242, 151), size=22)
    add_card(slides[6], 0.65, 4.75, 2.05, 0.82, "冲干净", (220, 250, 230), size=22)
    add_card(slides[6], 0.65, 5.85, 2.05, 0.82, "擦干手", (255, 230, 236), size=22)
    add_bullets(slides[6], 9.15, 1.55, 3.45, 2.25, [
        "可以唱一遍生日歌。",
        "手心、手背、指缝都要有泡泡。",
        "擦干后，小手不再湿哒哒。"
    ], size=17)
    add_card(slides[6], 8.95, 5.85, 3.85, 0.62, "20秒，让泡泡认真工作！", (255, 242, 151), size=17)
    add_footer(slides[6], 7)

    # 8
    add_title(slides[7], "泡泡科学小实验")
    add_bullets(slides[7], 9.0, 1.25, 3.75, 3.55, [
        "盘里倒清水，撒一点胡椒粉。",
        "手指先碰清水，胡椒还在附近。",
        "手指沾肥皂再碰，胡椒会散开。",
        "在老师或家长陪同下做实验。"
    ], size=16, fill=(255, 255, 255))
    add_card(slides[7], 4.6, 6.62, 4.15, 0.58, "肥皂能帮水带走油油和脏东西", (220, 250, 241), size=16)
    add_footer(slides[7], 8)

    # 9
    add_title(slides[8], "打喷嚏也要讲卫生")
    add_bullets(slides[8], 0.65, 1.45, 3.85, 3.35, [
        "用纸巾或手肘挡住口鼻。",
        "用过的纸巾丢进垃圾桶。",
        "咳嗽、打喷嚏后要洗手。",
        "别用脏手揉眼睛、抠鼻子。"
    ], size=17, fill=(255, 255, 255))
    add_card(slides[8], 8.45, 6.45, 3.85, 0.6, "礼貌一挡，细菌少飞翔", (255, 242, 151), size=17)
    add_footer(slides[8], 9)

    # 10
    add_title(slides[9], "让小手保持干净")
    add_bullets(slides[9], 0.7, 1.35, 3.75, 3.15, [
        "勤剪指甲，别把脏东西藏起来。",
        "不咬手指，不用手乱摸脸。",
        "小伤口贴创可贴，保持干净。",
        "毛巾、水杯等个人物品不混用。"
    ], size=17, fill=(255, 255, 255))
    add_card(slides[9], 8.0, 6.55, 4.05, 0.58, "干净小习惯，每天都能做", (220, 250, 230), size=17)
    add_footer(slides[9], 10)

    # 11
    add_title(slides[10], "校园洗手小侦探")
    add_bullets(slides[10], 9.25, 1.15, 3.25, 1.0, [
        "找一找：学校里哪里可以洗手？",
        "记一记：今天抓住几个洗手机会？"
    ], size=14, fill=(255, 255, 255))
    add_card(slides[10], 9.7, 6.2, 2.85, 0.6, "完成一次，给自己一颗星！", (255, 242, 151), size=15)
    add_card(slides[10], 2.05, 6.95, 4.55, 0.35, "课堂互动：做一名“洗手提醒员”", (221, 242, 255), size=13)
    add_footer(slides[10], 11)

    # 12
    add_title(slides[11], "我是手卫生小英雄")
    add_box(slides[11], 2.25, 1.25, 8.85, 1.55, fill=(255, 255, 255), outline=(255, 220, 97), transparency=2)
    add_text(slides[11], 2.55, 1.42, 8.25, 0.42, "我承诺：", size=24, bold=True, color=(240, 118, 88), align=PP_ALIGN.CENTER)
    add_text(slides[11], 2.65, 1.93, 8.05, 0.48, "吃前便后洗手，搓够20秒，提醒伙伴一起做！", size=20, bold=True, color=(38, 99, 170), align=PP_ALIGN.CENTER)
    add_card(slides[11], 4.15, 6.55, 5.0, 0.62, "小手干净，健康同行！", (255, 242, 151), size=22)
    add_footer(slides[11], 12)

    prs.save(OUT_FILE)


def main():
    image_paths = [
        slide01(),
        slide02(),
        slide03(),
        slide04(),
        slide05(),
        slide06(),
        slide07(),
        slide08(),
        slide09(),
        slide10(),
        slide11(),
        slide12(),
    ]
    build_ppt(image_paths)
    print(f"Generated: {OUT_FILE}")
    print(f"Assets: {ASSET_DIR}")


if __name__ == "__main__":
    main()
