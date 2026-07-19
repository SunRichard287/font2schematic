"""颜色映射和默认配置常量"""

from typing import Dict, Tuple, Optional

# 16 种混凝土颜色 → (Minecraft 方块 ID, RGB 色值)
CONCRETE_COLORS: Dict[str, Tuple[str, Tuple[int, int, int]]] = {
    "白色混凝土":     ("white_concrete",       (249, 255, 254)),
    "淡灰色混凝土":   ("light_gray_concrete",  (125, 125, 115)),
    "灰色混凝土":     ("gray_concrete",        (68,  68,  67)),
    "黑色混凝土":     ("black_concrete",       (25,  26,  25)),
    "红色混凝土":     ("red_concrete",         (161, 39,  34)),
    "橙色混凝土":     ("orange_concrete",      (216, 92,  18)),
    "黄色混凝土":     ("yellow_concrete",      (241, 175, 21)),
    "黄绿色混凝土":   ("lime_concrete",        (107, 196, 32)),
    "绿色混凝土":     ("green_concrete",       (72,  106, 36)),
    "青色混凝土":     ("cyan_concrete",        (21,  119, 136)),
    "浅蓝色混凝土":   ("light_blue_concrete",  (36,  137, 199)),
    "蓝色混凝土":     ("blue_concrete",        (45,  46,  144)),
    "紫色混凝土":     ("purple_concrete",      (100, 32,  157)),
    "品红色混凝土":   ("magenta_concrete",     (190, 72,  186)),
    "粉色混凝土":     ("pink_concrete",        (213, 129, 150)),
    "棕色混凝土":     ("brown_concrete",       (95,  59,  32)),
}

# 空气
AIR_NAME = "空气"
AIR_BLOCK = "air"

# 默认配置
DEFAULT_FONT_SIZE = 72
DEFAULT_SCALE = 1
DEFAULT_PROJECT_NAME = "font2schematic"
DEFAULT_AUTHOR = "font2schematic"
DEFAULT_FOREGROUND = "黑色混凝土"
DEFAULT_BACKGROUND = "白色混凝土"

# 视角模式
MODE_XY = "XY平面"  
MODE_XZ = "XZ平面"  
MODE_YZ = "YZ平面"  
VIEW_MODES = [MODE_XY, MODE_XZ, MODE_YZ]

# 二值化 alpha 阈值
ALPHA_THRESHOLD = 128

# 支持的字体格式
FONT_EXTENSIONS = [("字体文件", "*.ttf *.otf"), ("所有文件", "*.*")]

# 保存的文件格式
LITEMATIC_EXTENSIONS = [("Litematica 投影", "*.litematic")]


def get_all_color_names() -> list[str]:
    """获取所有可选颜色名（含空气）。"""
    return [AIR_NAME] + list(CONCRETE_COLORS.keys())


def get_block_id(color_name: str) -> str:
    """根据颜色名获取 Minecraft 方块 ID。"""
    if color_name == AIR_NAME:
        return AIR_BLOCK
    return CONCRETE_COLORS[color_name][0]


def get_rgb(color_name: str) -> Optional[Tuple[int, int, int]]:
    """根据颜色名获取 RGB 色值（空气返回 None）。"""
    if color_name == AIR_NAME:
        return None
    return CONCRETE_COLORS[color_name][1]
