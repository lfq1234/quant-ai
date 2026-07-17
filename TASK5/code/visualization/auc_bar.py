# -*- coding: utf-8 -*-
"""AUC 柱状图"""

import matplotlib.pyplot as plt

import config
from ._common import COLOR_GREEN_LINE


def plot_auc_bar(summary_df, save_path, dataset_name=''):
    """绘制多模型 AUC 柱状图"""
    fig, ax = plt.subplots(figsize=(7, 4.5))

    models = summary_df['模型'].tolist()
    aucs = summary_df['AUC'].tolist()
    colors = [config.MODEL_COLORS.get(m, '#999999') for m in models]

    bars = ax.bar(models, aucs, color=colors, width=0.5, edgecolor='white', linewidth=1.2)

    # 在柱上标注数值
    for bar, auc in zip(bars, aucs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f'{auc:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # 随机基线
    ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=1, label='随机基线 (0.5)')
    ax.axhline(y=0.7, color='#F39C12', linestyle=':', linewidth=1, label='有效阈值 (0.7)')
    ax.axhline(y=0.8, color=COLOR_GREEN_LINE, linestyle=':', linewidth=1, label='良好阈值 (0.8)')

    ax.set_ylim([0, 1.1])
    ax.set_ylabel('AUC', fontsize=12)
    title = '各模型 AUC 对比'
    if dataset_name:
        title += f' — {dataset_name}'
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [图] 已保存: {save_path}")
