# -*- coding: utf-8 -*-
"""路径配置：项目根目录、数据目录、图片目录等"""

from pathlib import Path

# __file__ = code/config/paths.py -> 上溯 3 层到 TASK6/
TASK6_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = TASK6_DIR / 'data'
IMAGES_DIR = TASK6_DIR / 'images'
REPORT_DIR = TASK6_DIR
CODE_DIR = TASK6_DIR / 'code'
RAW_DIR = DATA_DIR / 'raw_daily'
PANEL_FILE = DATA_DIR / 'panel_with_factors.csv'
RESULTS_FILE = DATA_DIR / 'backtest_results.json'
