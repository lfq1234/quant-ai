# -*- coding: utf-8 -*-
"""可视化公共配置：matplotlib 中文设置、额外颜色常量"""

import matplotlib
import matplotlib.pyplot as plt

import config

# 额外颜色常量
COLOR_GREEN_LINE = '#27AE60'

# 全局中文设置
matplotlib.rcParams['font.sans-serif'] = config.FONT_SANS_SERIF
matplotlib.rcParams['axes.unicode_minus'] = False
