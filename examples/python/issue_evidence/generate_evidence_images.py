"""Render terminal-style evidence PNGs from live CLI transcripts."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
FONT_CANDIDATES = (
    "/System/Library/Fonts/Menlo.ttc",
    "/Library/Fonts/Menlo.ttc",
    "Menlo.ttc",
    "DejaVuSansMono.ttf",
)


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def _font(size: int = 13) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _line_color(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("$"):
        return "#33dd66"
    if "BUG:" in line or "Internal server error" in line:
        return "#ff6b6b"
    if stripped.startswith("[exit code"):
        return "#ffd166"
    if "RuntimeError" in line or "Response body:" in line:
        return "#f4a261"
    return "#e6e6e6"


def text_to_png(text: str, out_path: Path, padding: int = 18, line_height: int = 19) -> Path:
    font = _font(13)
    lines = strip_ansi(text).rstrip().splitlines() or ["(empty output)"]

    max_width = 0
    for line in lines:
        max_width = max(max_width, font.getbbox(line)[2])

    width = min(max(max_width + padding * 2, 720), 1400)
    height = padding * 2 + line_height * len(lines)

    img = Image.new("RGB", (width, height), "#1c1c1c")
    draw = ImageDraw.Draw(img)

    y = padding
    for line in lines:
        draw.text((padding, y), line, fill=_line_color(line), font=font)
        y += line_height

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, optimize=True)
    return out_path
