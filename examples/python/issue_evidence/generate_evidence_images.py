"""Render cropped terminal-style evidence PNGs from text output."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int = 14):
    for name in (
        "Menlo.ttc",
        "SFMono-Regular.otf",
        "DejaVuSansMono.ttf",
        "Courier New.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_to_png(text: str, out_path: Path, padding: int = 16, line_height: int = 18) -> Path:
    font = _font(13)
    lines = text.rstrip().splitlines() or ["(empty output)"]
    max_width = max((font.getbbox(line)[2] for line in lines), default=200)
    width = max_width + padding * 2
    height = padding * 2 + line_height * len(lines)

    img = Image.new("RGB", (width, height), "#1e1e1e")
    draw = ImageDraw.Draw(img)
    y = padding
    for line in lines:
        draw.text((padding, y), line, fill="#d4d4d4", font=font)
        y += line_height

    # Crop to content (already tight); save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, optimize=True)
    return out_path
