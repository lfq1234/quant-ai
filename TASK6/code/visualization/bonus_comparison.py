# -*- coding: utf-8 -*-
"""附加题：持仓数敏感性对比图"""

import numpy as np
import matplotlib.pyplot as plt

import config
from evaluation.metrics import calc_metrics


def plot_bonus_comparison(bonus_returns, bench_df, save_path):
    """绘制不同 N 值的累计收益曲线 + 业绩对比柱状图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：累计收益曲线
    bench = bench_df.copy()
    bench['cum'] = (1 + bench['benchmark_return']).cumprod()
    x = range(len(bench))
    ax1.plot(x, bench['cum'], color=config.BENCH_COLOR, linewidth=2,
             linestyle='--', label='Benchmark')
    for n_val, ret_df in bonus_returns.items():
        cum = (1 + ret_df['portfolio_return']).cumprod()
        ax1.plot(range(len(cum)), cum, linewidth=2, label=f'RF {n_val}')

    ax1.set_xlabel('Quarter', fontsize=11)
    ax1.set_ylabel('Cumulative Net Value', fontsize=11)
    ax1.set_title('Cumulative Return by N', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 右图：Sharpe + Max DD 对比
    labels = []
    sharpes = []
    mdds = []
    for n_val, ret_df in bonus_returns.items():
        m = calc_metrics(ret_df, bench_df)
        labels.append(n_val)
        sharpes.append(m['sharpe'])
        mdds.append(m['max_drawdown'])

    x2 = np.arange(len(labels))
    w = 0.35
    ax2.bar(x2 - w/2, sharpes, w, color=config.COLOR_RED, label='Sharpe', edgecolor='white')
    ax2.bar(x2 + w/2, [abs(d) for d in mdds], w, color=config.COLOR_GREEN,
            label='Max Drawdown (abs)', edgecolor='white')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(labels, fontsize=10)
    ax2.set_title('Risk-Return by N', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3)

    fig.suptitle('Bonus: Holding Count Sensitivity (N=10/30/50/100)',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [Fig] Saved: {save_path}')
