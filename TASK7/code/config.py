# -*- coding: utf-8 -*-
"""TASK7 报告生成：路径配置"""

import os

# code/ 目录
BASE = os.path.dirname(os.path.abspath(__file__))
# TASK7/ 目录
TASK7 = os.path.dirname(BASE)

IMAGES_DIR = os.path.join(TASK7, 'images')          # 平台导出图表放这里
REPORT_DIR = TASK7                                   # docx/pdf 输出目录
RESULTS_FILE = os.path.join(BASE, 'results_template.json')

# 最终提交文件名（任务要求：姓名+TASK7.pdf）
REPORT_DOCX = os.path.join(REPORT_DIR, '林富强+TASK7.docx')
REPORT_PDF = os.path.join(REPORT_DIR, '林富强+TASK7.pdf')
