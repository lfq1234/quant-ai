# -*- coding: utf-8 -*-
"""TASK5 配置中心 — 统一导出路径、参数、特征配置和可视化样式"""

from .paths import TASK5_DIR, DATA_DIR, IMAGE_DIR, CODE_DIR, STOCK_CSV
from .params import RANDOM_STATE, MODEL_PARAMS, TEST_SIZE
from .features import MA_PERIODS, RSI_PERIOD, VOLATILITY_WINDOW, MOMENTUM_PERIODS
from .style import (
    COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_ORANGE, COLOR_PURPLE,
    MODEL_COLORS, FONT_SANS_SERIF,
)
