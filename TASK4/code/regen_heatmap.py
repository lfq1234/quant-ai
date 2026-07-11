# -*- coding: utf-8 -*-
"""重新生成多参数热力图"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plots import plot_multi_param_heatmap
from config import DATA_DIR, IMAGE_DIR

multi_param_path = os.path.join(DATA_DIR, 'multi_param_results.json')
with open(multi_param_path, 'r', encoding='utf-8') as f:
    all_results = json.load(f)

save_path = os.path.join(IMAGE_DIR, 'heatmap_multi_param.png')
plot_multi_param_heatmap(all_results, save_path)
print(f'热力图已保存: {save_path}')
