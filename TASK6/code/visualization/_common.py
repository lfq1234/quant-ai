# -*- coding: utf-8 -*-
"""可视化公共配置：matplotlib 中文设置"""

import matplotlib
import matplotlib.pyplot as plt

import config

matplotlib.rcParams['font.sans-serif'] = config.FONT_SANS_SERIF
matplotlib.rcParams['axes.unicode_minus'] = False
