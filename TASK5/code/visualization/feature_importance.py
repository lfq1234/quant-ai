# -*- coding: utf-8 -*-
"""特征重要性图（仅适用于树模型）"""

import numpy as np
import matplotlib.pyplot as plt

import config


def plot_feature_importance(model, feature_names, save_path, top_n=15, model_name='Random Forest'):
    """绘制特征重要性图（仅适用于树模型）"""
    if not hasattr(model, 'feature_importances_'):
        print(f"  [跳过] {model_name} 不支持 feature_importances_")
        return

    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(range(len(indices)), importances[indices][::-1],
            color=config.COLOR_RED, height=0.6, edgecolor='white')
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices][::-1], fontsize=10)
    ax.set_xlabel('特征重要性', fontsize=11)
    ax.set_title(f'{model_name} 特征重要性 Top {len(indices)}', fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [图] 已保存: {save_path}")
