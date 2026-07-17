# -*- coding: utf-8 -*-
"""每季度收益柱状图"""

import numpy as np
import matplotlib.pyplot as plt

import config


def plot_quarterly_return(all_returns, bench_df, save_path, model_name='Random Forest'):
    """绘制策略 vs 基准的每季度收益柱状图"""
    ret_df = all_returns[model_name]
    merged = ret_df.merge(bench_df, on='quarter_str', how='inner')

    quarters = merged['quarter_str'].tolist()
    x = np.arange(len(quarters))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x - width/2, merged['portfolio_return'], width,
           color=config.COLOR_RED, label=f'{model_name} Strategy', edgecolor='white')
    ax.bar(x + width/2, merged['benchmark_return'], width,
           color=config.BENCH_COLOR, label='Benchmark', edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(quarters, rotation=45, fontsize=9)
    ax.set_ylabel('Quarterly Return', fontsize=11)
    ax.set_title(f'Quarterly Return: {model_name} vs Benchmark',
                 fontsize=13, fontweight='bold')
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [Fig] Saved: {save_path}')
