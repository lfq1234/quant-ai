# -*- coding: utf-8 -*-
"""截面 IC / Rank IC 曲线"""

import matplotlib.pyplot as plt

import config


def plot_ic_curve(ic_dict, save_path, model_name='Random Forest'):
    """绘制单模型的 IC 和 Rank IC 时序曲线"""
    if model_name not in ic_dict:
        print(f'  [Skip] No IC data for {model_name}')
        return

    ic_df = ic_dict[model_name]
    x = range(len(ic_df))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, ic_df['ic'], width=0.4, color=config.COLOR_BLUE, alpha=0.6, label='IC')
    ax.plot(x, ic_df['rank_ic'], color=config.COLOR_RED, linewidth=2,
            marker='o', markersize=4, label='Rank IC')

    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.axhline(y=ic_df['rank_ic'].mean(), color=config.COLOR_RED,
               linewidth=1, linestyle='--', alpha=0.5,
               label=f'Mean Rank IC = {ic_df["rank_ic"].mean():.4f}')

    ax.set_xticks(list(x))
    ax.set_xticklabels(ic_df['quarter_str'], rotation=45, fontsize=8)
    ax.set_ylabel('IC / Rank IC', fontsize=11)
    ax.set_title(f'{model_name}: IC & Rank IC per Quarter',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [Fig] Saved: {save_path}')
