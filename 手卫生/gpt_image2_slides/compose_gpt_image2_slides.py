from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "source"
FINAL_DIR = ROOT / "final"
ARTIFACT_DIR = Path("/opt/cursor/artifacts/assets")

CANVAS = (1920, 1080)
FONT_REGULAR = Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
FONT_BOLD = FONT_REGULAR


SLIDES = [
    {
        "base": "hand_hygiene_gpt2_base_01_cover.png",
        "out": "slide01_cover.png",
        "texts": [
            ("title", (285, 100, 1635, 320), "小手洗一洗\n健康伴我行", 84, "#246fb2"),
            ("center", (490, 335, 1430, 405), "二年级手卫生科普课", 40, "#ef7c58"),
            ("center", (590, 890, 1330, 970), "和泡泡一起打败细菌小怪兽！", 38, "#354b5f"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_02_contents.png",
        "out": "slide02_contents.png",
        "texts": [
            ("title", (430, 58, 1490, 170), "今天学什么？", 68, "#246fb2"),
            ("center", (160, 220, 855, 435), "模块一\n为什么要洗手\n认识细菌和脏手风险", 44, "#354b5f"),
            ("center", (1065, 220, 1760, 435), "模块二\n什么时候要洗手\n五大关键时刻", 44, "#354b5f"),
            ("center", (160, 600, 855, 815), "模块三\n怎样正确洗手\n七步洗手法 + 小贴士", 44, "#354b5f"),
            ("center", (1065, 600, 1760, 815), "模块四\n洗手小达人宣誓\n把好习惯带回家", 44, "#354b5f"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_03_germs.png",
        "out": "slide03_germs.png",
        "texts": [
            ("title", (360, 52, 1560, 155), "第一章：为什么要洗手", 62, "#246fb2"),
            ("center", (95, 215, 655, 445), "认识手上的细菌\n小手看起来干净，\n也可能藏着数百万到上亿个\n看不见的小细菌！", 40, "#354b5f"),
            ("left", (115, 520, 725, 835), "它们爱躲在：\n• 手心\n• 指缝\n• 指甲边\n\n脏手碰口、鼻、眼，\n细菌就可能进身体。", 36, "#354b5f"),
            ("center", (1110, 790, 1780, 910), "洗手能把很多“小怪兽”冲走！", 42, "#ef7c58"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_04_consequences.png",
        "out": "slide04_consequences.png",
        "texts": [
            ("title", (390, 52, 1530, 155), "不洗手会怎样？", 66, "#246fb2"),
            ("center", (120, 250, 565, 520), "肚子疼\n细菌跟食物一起\n进肚子", 42, "#354b5f"),
            ("center", (735, 250, 1185, 520), "感冒发烧\n脏手摸口鼻\n病毒来捣乱", 42, "#354b5f"),
            ("center", (1355, 250, 1800, 520), "皮肤感染\n小伤口碰脏东西\n会添麻烦", 42, "#354b5f"),
            ("center", (445, 870, 1475, 960), "记住：洗手是在给身体加护盾", 44, "#ef7c58"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_05_when.png",
        "out": "slide05_when_to_wash.png",
        "texts": [
            ("title", (330, 52, 1590, 155), "第二章：什么时候要洗手", 62, "#246fb2"),
            ("center", (530, 165, 1390, 235), "五大关键时刻", 44, "#ef7c58"),
            ("center", (100, 335, 430, 410), "饭前", 44, "#354b5f"),
            ("center", (1390, 260, 1815, 345), "便后", 44, "#354b5f"),
            ("center", (170, 725, 560, 805), "玩耍后", 44, "#354b5f"),
            ("center", (760, 690, 1160, 795), "咳嗽或\n打喷嚏后", 38, "#354b5f"),
            ("center", (1320, 735, 1840, 820), "接触宠物后", 44, "#354b5f"),
            ("center", (310, 955, 1610, 1030), "口诀：吃前便后、玩后咳后、摸宠物后", 40, "#246fb2"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_06_seven_overview.png",
        "out": "slide06_seven_steps_overview.png",
        "texts": [
            ("title", (300, 50, 1620, 150), "第三章：怎样正确洗手", 62, "#246fb2"),
            ("center", (545, 160, 1375, 235), "七步洗手法总览", 44, "#ef7c58"),
            ("center", (115, 725, 345, 835), "内\n掌心相对", 32, "#354b5f"),
            ("center", (370, 805, 600, 915), "外\n手背也要洗", 32, "#354b5f"),
            ("center", (625, 725, 855, 835), "夹\n指缝交叉", 32, "#354b5f"),
            ("center", (880, 805, 1110, 915), "弓\n指背弯弯", 32, "#354b5f"),
            ("center", (1135, 725, 1365, 835), "大\n拇指转转", 32, "#354b5f"),
            ("center", (1390, 805, 1620, 915), "立\n指尖画圈", 32, "#354b5f"),
            ("center", (1645, 725, 1875, 835), "腕\n手腕别忘", 32, "#354b5f"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_07_steps_1_4.png",
        "out": "slide07_steps_1_4.png",
        "texts": [
            ("title", (320, 52, 1600, 155), "七步洗手法图解（1-4）", 60, "#246fb2"),
            ("center", (145, 250, 725, 365), "1 内：掌心相对搓一搓", 38, "#354b5f"),
            ("center", (1195, 250, 1775, 365), "2 外：手背交叉搓一搓", 38, "#354b5f"),
            ("center", (145, 720, 725, 835), "3 夹：手指交叉搓一搓", 38, "#354b5f"),
            ("center", (1195, 720, 1775, 835), "4 弓：弯弯指背搓一搓", 38, "#354b5f"),
            ("center", (555, 940, 1365, 1015), "每一步都搓出泡泡，细菌没处躲！", 38, "#ef7c58"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_08_steps_5_7.png",
        "out": "slide08_steps_5_7.png",
        "texts": [
            ("title", (320, 52, 1600, 155), "七步洗手法图解（5-7）", 60, "#246fb2"),
            ("center", (95, 645, 600, 760), "5 大：大拇指转一转", 38, "#354b5f"),
            ("center", (710, 645, 1215, 760), "6 立：指尖掌心画圈圈", 36, "#354b5f"),
            ("center", (1320, 645, 1825, 760), "7 腕：手腕也要洗干净", 36, "#354b5f"),
            ("center", (485, 880, 1435, 975), "合起来搓洗不少于 20 秒", 46, "#ef7c58"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_09_tips.png",
        "out": "slide09_tips.png",
        "texts": [
            ("title", (385, 52, 1535, 155), "洗手小贴士", 66, "#246fb2"),
            ("center", (110, 255, 560, 430), "流动水\n先湿手，冲干净", 40, "#354b5f"),
            ("center", (735, 255, 1185, 430), "肥皂/洗手液\n泡泡带走脏东西", 38, "#354b5f"),
            ("center", (1360, 255, 1810, 430), "20秒\n可以唱一遍生日歌", 38, "#354b5f"),
            ("center", (735, 735, 1185, 910), "擦干\n用干净毛巾或纸巾", 40, "#354b5f"),
            ("center", (305, 960, 1615, 1030), "洗完擦干手，小手不再湿哒哒！", 40, "#ef7c58"),
        ],
    },
    {
        "base": "hand_hygiene_gpt2_base_10_pledge.png",
        "out": "slide10_pledge.png",
        "texts": [
            ("title", (350, 52, 1570, 155), "洗手小达人宣誓", 66, "#246fb2"),
            ("center", (345, 240, 1575, 335), "我承诺：", 52, "#ef7c58"),
            ("left", (420, 350, 1500, 695), "• 饭前便后主动洗手；\n• 玩耍、咳嗽、摸宠物后记得洗手；\n• 认真完成七步洗手法，搓够20秒；\n• 提醒伙伴一起保护健康！", 42, "#354b5f"),
            ("center", (430, 815, 1490, 920), "小手干净，健康同行！", 56, "#246fb2"),
        ],
    },
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size=size)


def normalize_base(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    return ImageOps.fit(image, CANVAS, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            candidate = current + char
            width = draw.textbbox((0, 0), candidate, font=fnt, stroke_width=1)[2]
            if width <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = char
        lines.append(current)
    return "\n".join(lines)


def draw_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], outline: str = "#8cd4ff") -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 8, y1 + 8, x2 + 8, y2 + 8), radius=32, fill=(64, 96, 128, 56))
    draw.rounded_rectangle(box, radius=32, fill=(255, 255, 255, 224), outline=outline, width=5)


def draw_text_box(
    draw: ImageDraw.ImageDraw,
    mode: str,
    box: tuple[int, int, int, int],
    text: str,
    size: int,
    color: str,
) -> None:
    draw_panel(draw, box, outline="#ffdc61" if mode == "title" else "#8cd4ff")
    x1, y1, x2, y2 = box
    margin = 28 if mode != "title" else 22
    fnt = font(size)
    wrapped = wrap_text(draw, text, fnt, x2 - x1 - margin * 2)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=fnt, spacing=10, stroke_width=1)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    if mode == "left":
        x = x1 + margin
        align = "left"
    else:
        x = x1 + (x2 - x1 - text_w) / 2
        align = "center"
    y = y1 + (y2 - y1 - text_h) / 2 - 4
    draw.multiline_text(
        (x, y),
        wrapped,
        font=fnt,
        fill=color,
        spacing=10,
        align=align,
        stroke_width=1,
        stroke_fill=(255, 255, 255, 180),
    )


def compose_slide(slide: dict[str, object]) -> Path:
    source = SOURCE_DIR / str(slide["base"])
    image = normalize_base(source)
    draw = ImageDraw.Draw(image, "RGBA")
    for item in slide["texts"]:
        mode, box, text, size, color = item
        draw_text_box(draw, mode, box, text, size, color)
    out = FINAL_DIR / str(slide["out"])
    image.convert("RGB").save(out, quality=95, optimize=True)
    return out


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    for slide in SLIDES:
        base_name = str(slide["base"])
        src = ARTIFACT_DIR / base_name
        dst = SOURCE_DIR / base_name
        if src.exists():
            shutil.copy2(src, dst)
        if not dst.exists():
            raise FileNotFoundError(f"Missing GPT Image 2 base image: {dst}")

    outputs = [compose_slide(slide) for slide in SLIDES]
    print("Generated final slides:")
    for output in outputs:
        print(f"- {output}")


if __name__ == "__main__":
    main()
