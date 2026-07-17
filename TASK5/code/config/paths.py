# -*- coding: utf-8 -*-
"""路径配置：项目根目录、数据目录、图片目录等"""

import os

# __file__ = code/config/paths.py
# 需要上溯 3 层：config/ → code/ → TASK5/
TASK5_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(TASK5_DIR, 'data')
IMAGE_DIR = os.path.join(TASK5_DIR, 'images')
CODE_DIR = os.path.join(TASK5_DIR, 'code')

# 数据文件
STOCK_CSV = os.path.join(DATA_DIR, 'cjdl_600900_2025-2026.csv')
