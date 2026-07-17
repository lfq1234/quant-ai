# -*- coding: utf-8 -*-
"""多模型业绩对比柱状图"""

import numpy as np
import matplotlib.pyplot as plt

import config


def plot_model_comparison(summary, save_path):
    """绘制多模型年化收益、Sharpe、信息比率对比柱状图"""
    metrics = ['annual_return', 'sharpe', 'info_rate']
    titles = ['Annual Return', 'Sharpe Ratio', 'Information Ratio']
    available = [m for m in metrics if m in summary.columns]
    n = len(available)

    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]

    models = summary['model'].tolist()
    x = np.arange(len(models))

    for ax, metric, title in zip(axes, available, titles):
        vals = summary[metric].values
        colors = [config.MODEL_COLORS.get(m, '#999999') for m in models]
        bars = ax.bar(x, vals, color=colors, width=0.5, edgecolor='white')
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f'{v:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=30, fontsize=9)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axhline(y=0, color='black', linewidth=0.8)
        ax.grid(axis='y', alpha=0.3)

    fig.suptitle('Model Performance Comparison', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [Fig] Saved: {save_path}')
