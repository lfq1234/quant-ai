# -*- coding: utf-8 -*-
"""因子重要性图（树模型专用）"""

import numpy as np
import matplotlib.pyplot as plt

import config


def plot_feature_importance(model, save_path, model_name='Random Forest'):
    """绘制因子重要性横向柱状图"""
    if not hasattr(model, 'feature_importances_'):
        print(f'  [Skip] {model_name} has no feature_importances_')
        return

    importances = model.feature_importances_
    names = config.FEATURE_COLS
    order = np.argsort(importances)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(range(len(order)), importances[order],
            color=config.COLOR_RED, height=0.6, edgecolor='white')
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([names[i] for i in order], fontsize=10)
    ax.set_xlabel('Importance', fontsize=11)
    ax.set_title(f'{model_name} Factor Importance', fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [Fig] Saved: {save_path}')
