# -*- coding: utf-8 -*-
"""累计收益曲线"""

import numpy as np
import matplotlib.pyplot as plt

import config


def plot_cumulative_return(all_returns, bench_df, save_path):
    """绘制多模型 + 基准的累计净值曲线"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # 基准
    bench = bench_df.copy()
    bench['cum'] = (1 + bench['benchmark_return']).cumprod()
    quarters = range(len(bench))
    ax.plot(quarters, bench['cum'], color=config.BENCH_COLOR,
            linewidth=2, linestyle='--', label='Benchmark (Equal-Weight)')

    # 各模型
    for name, ret_df in all_returns.items():
        if name.startswith('_'):
            continue
        cum = (1 + ret_df['portfolio_return']).cumprod()
        x = range(len(cum))
        color = config.MODEL_COLORS.get(name, None)
        ax.plot(x, cum, color=color, linewidth=2, label=name)

    ax.set_xlabel('Quarter', fontsize=11)
    ax.set_ylabel('Cumulative Net Value', fontsize=11)
    ax.set_title('Cumulative Return: Strategy vs Benchmark (2021-2024)',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=1.0, color='gray', linewidth=0.8, alpha=0.5)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [Fig] Saved: {save_path}')
