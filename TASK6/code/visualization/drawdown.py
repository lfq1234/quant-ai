# -*- coding: utf-8 -*-
"""回撤曲线"""

import numpy as np
import matplotlib.pyplot as plt

import config


def plot_drawdown(all_returns, save_path):
    """绘制多模型回撤曲线"""
    fig, ax = plt.subplots(figsize=(10, 5))

    for name, ret_df in all_returns.items():
        if name.startswith('_'):
            continue
        cum = (1 + ret_df['portfolio_return']).cumprod()
        running_max = np.maximum.accumulate(cum)
        dd = cum / running_max - 1
        x = range(len(dd))
        color = config.MODEL_COLORS.get(name, None)
        ax.fill_between(x, dd, 0, color=color, alpha=0.15)
        ax.plot(x, dd, color=color, linewidth=1.5, label=name)

    ax.set_xlabel('Quarter', fontsize=11)
    ax.set_ylabel('Drawdown', fontsize=11)
    ax.set_title('Drawdown Curves (2021-2024)', fontsize=13, fontweight='bold')
    ax.legend(loc='lower left', fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [Fig] Saved: {save_path}')
