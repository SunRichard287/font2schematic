"""核心渲染和 .litematic 投影生成逻辑"""

from __future__ import annotations

import unicodedata
from PIL import Image, ImageDraw, ImageFont
from litemapy import Schematic, Region
from litemapy.minecraft import BlockState

from constants import (
    ALPHA_THRESHOLD,
    AIR_BLOCK,
    AIR_NAME,
    DEFAULT_AUTHOR,
    DEFAULT_PROJECT_NAME,
    MODE_XY,
    MODE_XZ,
    MODE_YZ,
    get_block_id,
)


def estimate_size(
    text: str,
    font_path: str,
    font_size: int,
    scale: int,
    mode: str,
) -> tuple[int, int, int]:
    """预估投影尺寸 (宽, 高, 厚/层数)。

    返回: (width, height, depth) 单位：方块数
    """
    if not text.strip() or not font_path:
        return (0, 0, 0)

 
    text = text.replace("\t", "    ")

    text = "".join(
        ch if ch in ("\n", "\r") or unicodedata.category(ch) not in ("Cc", "Cf")
        else " " for ch in text
    )

    font = ImageFont.truetype(font_path, font_size)
    lines = text.splitlines()

    max_width = 0
    total_height = 0
    for line in lines:
        if line:
            bbox = font.getbbox(line)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
        else:
            lw = 0
            lh = font_size 
        max_width = max(max_width, lw)
        total_height += lh


    w = max(1, max_width) * scale
    h = max(1, total_height) * scale

    if mode == MODE_XZ:
        return (w, 1, h)  
    elif mode == MODE_YZ:
        return (1, w, h)  
    else:  # XY平面
        return (w, h, 1)  


def generate_litematic(
    text: str,
    font_path: str,
    font_size: int,
    scale: int,
    mode: str,
    foreground: str,
    background: str,
    project_name: str = DEFAULT_PROJECT_NAME,
    save_path: str = "",
) -> str:
    """生成 .litematic 文件。

    返回保存路径。
    """

    text = text.replace("\t", "    ")

    text = "".join(
        ch if ch in ("\n", "\r") or unicodedata.category(ch) not in ("Cc", "Cf")
        else " " for ch in text
    )

    font = ImageFont.truetype(font_path, font_size)
    lines = text.splitlines()

    line_heights = []
    line_widths = []
    for line in lines:
        if line:
            bbox = font.getbbox(line)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
        else:
            lw = 0
            lh = font_size
        line_heights.append(lh)
        line_widths.append(lw)

    canvas_w = max(line_widths) if max(line_widths) > 0 else 1
    canvas_h = sum(line_heights)

    spacing = 0  

    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    y_offset = 0
    for i, line in enumerate(lines):
        if line:
            draw.text((0, y_offset), line, font=font, fill=(255, 255, 255, 255))
        y_offset += line_heights[i]

    if scale > 1:
        img = img.resize(
            (canvas_w * scale, canvas_h * scale),
            Image.Resampling.NEAREST,
        )
    elif scale == 0:
        scale = 1

    pixels = img.load()
    fw, fh = img.size

    fg_block_id = get_block_id(foreground)
    bg_block_id = get_block_id(background)

    if mode == MODE_XZ:
        reg = Region(0, 0, 0, fw, 1, fh)
        for x in range(fw):
            for z in range(fh):
                _, _, _, a = pixels[x, z]
                if a > ALPHA_THRESHOLD:
                    reg[x, 0, z] = BlockState(f"minecraft:{fg_block_id}")
                elif bg_block_id != AIR_BLOCK:
                    reg[x, 0, z] = BlockState(f"minecraft:{bg_block_id}")

        schem = Schematic(
            name=project_name or DEFAULT_PROJECT_NAME,
            author=DEFAULT_AUTHOR,
            description=f"font2schematic {MODE_XZ}: {project_name}",
            regions={"main": reg},
        )
    elif mode == MODE_YZ:
        reg = Region(0, 0, 0, 1, fw, fh)
        for y in range(fw):
            for z in range(fh):
                _, _, _, a = pixels[y, z]
                if a > ALPHA_THRESHOLD:
                    reg[0, y, z] = BlockState(f"minecraft:{fg_block_id}")
                elif bg_block_id != AIR_BLOCK:
                    reg[0, y, z] = BlockState(f"minecraft:{bg_block_id}")

        schem = Schematic(
            name=project_name or DEFAULT_PROJECT_NAME,
            author=DEFAULT_AUTHOR,
            description=f"font2schematic {MODE_YZ}: {project_name}",
            regions={"main": reg},
        )
    else:  
        reg = Region(0, 0, 0, fw, fh, 1)
        for x in range(fw):
            for y in range(fh):
                _, _, _, a = pixels[x, y]
                if a > ALPHA_THRESHOLD:
                    reg[x, y, 0] = BlockState(f"minecraft:{fg_block_id}")
                elif bg_block_id != AIR_BLOCK:
                    reg[x, y, 0] = BlockState(f"minecraft:{bg_block_id}")

        schem = Schematic(
            name=project_name or DEFAULT_PROJECT_NAME,
            author=DEFAULT_AUTHOR,
            description=f"font2schematic {MODE_XY}: {project_name}",
            regions={"main": reg},
        )

    schem.save(save_path)
    return save_path
