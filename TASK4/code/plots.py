# -*- coding: utf-8 -*-
"""
绘图模块：海龟策略可视化——股价、唐奇安通道、买卖信号、净值曲线、回撤等。
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict

from config import TurtleConfig, IMAGE_DIR

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def plot_strategy(df: pd.DataFrame, config: TurtleConfig,
                  buy_dates: List[datetime], buy_prices: List[float],
                  sell_dates: List[datetime], sell_prices: List[float],
                  save_path: str):
    """绘制策略信号图：股价 + 唐奇安通道 + 买卖信号"""
    fig, ax = plt.subplots(figsize=(15, 7))

    ax.plot(df['trade_date'], df['close'], color='#2c3e50', linewidth=1.5, label='收盘价', zorder=3)
    ax.plot(df['trade_date'], df['channel_high'], color='#e74c3c', linewidth=1.2,
            linestyle='--', label=f'通道上轨（{config.entry_window}日最高价）', alpha=0.8)
    ax.plot(df['trade_date'], df['channel_low'], color='#3498db', linewidth=1.2,
            linestyle='--', label=f'通道下轨（{config.entry_window}日最低价）', alpha=0.8)
    ax.fill_between(df['trade_date'], df['channel_high'], df['channel_low'],
                    color='#f1c40f', alpha=0.1, label='唐奇安通道')

    if buy_dates:
        ax.scatter(buy_dates, buy_prices, marker='^', color='#e74c3c', s=180, zorder=5,
                   label='买入信号（突破上轨）', edgecolors='darkred', linewidths=1)
    if sell_dates:
        ax.scatter(sell_dates, sell_prices, marker='v', color='#27ae60', s=180, zorder=5,
                   label='卖出信号（跌破下轨）', edgecolors='darkgreen', linewidths=1)

    ax.set_title(f'{config.stock_name}（{config.ts_code}）海龟策略交易信号图\n'
                 f'唐奇安通道：入场周期={config.entry_window}日，出场周期={config.exit_window}日',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('交易日期', fontsize=11)
    ax.set_ylabel('价格（元）', fontsize=11)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    fig.autofmt_xdate()
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  信号图已保存: {save_path}')


def plot_backtest(df_bt: pd.DataFrame, results: Dict, save_path: str):
    """绘制回测净值曲线：策略 vs 买入持有"""
    fig, ax = plt.subplots(figsize=(14, 6))
    initial = results['initial_capital']

    ax.plot(df_bt['trade_date'], df_bt['portfolio_value'], color='#e74c3c', linewidth=1.5,
            label=f'海龟策略（总收益 {results["total_return"]}%，年化 {results["annual_return"]}%）')

    first_price = df_bt['close'].iloc[0]
    shares_bh = int(initial / first_price)
    bh_value = shares_bh * df_bt['close']
    ax.plot(df_bt['trade_date'], bh_value, color='#3498db', linewidth=1.5,
            label=f'买入持有（总收益 {results["buy_hold_return"]}%）', alpha=0.8)

    ax.axhline(y=initial, color='gray', linestyle='--', linewidth=0.8, label='初始资金')

    ax.set_title(f'{results["stock_name"]} 海龟策略回测净值曲线',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('交易日期', fontsize=11)
    ax.set_ylabel('组合价值（元）', fontsize=11)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    fig.autofmt_xdate()
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  净值曲线已保存: {save_path}')


def plot_drawdown(df_bt: pd.DataFrame, results: Dict, save_path: str):
    """绘制最大回撤图"""
    cummax = df_bt['portfolio_value'].cummax()
    drawdown = (df_bt['portfolio_value'] - cummax) / cummax * 100

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(df_bt['trade_date'], drawdown, 0, color='#e74c3c', alpha=0.4)
    ax.plot(df_bt['trade_date'], drawdown, color='#c0392b', linewidth=1)

    mdd_val = results['max_drawdown']
    mdd_idx = drawdown.values.argmin()
    mdd_date = df_bt['trade_date'].iloc[mdd_idx]
    ax.annotate(f'最大回撤: {mdd_val:.2f}%', xy=(mdd_date, mdd_val),
                xytext=(mdd_date, mdd_val + 2),
                fontsize=10, color='#c0392b', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#c0392b'))

    ax.set_title(f'{results["stock_name"]} 海龟策略最大回撤（MDD）分析', fontsize=14, fontweight='bold')
    ax.set_xlabel('交易日期', fontsize=11)
    ax.set_ylabel('回撤幅度（%）', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    fig.autofmt_xdate()
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  回撤图已保存: {save_path}')


def plot_metrics_radar(results: Dict, save_path: str):
    """绘制绩效指标雷达图"""
    labels = ['总收益', '年化收益', '夏普', '胜率', '盈亏比', 'Calmar']
    values = [
        np.clip(results['total_return'] / 50, -1, 1),
        np.clip(results['annual_return'] / 50, -1, 1),
        np.clip(results['sharpe_ratio'] / 3, -1, 1),
        results['win_rate'] / 100 * 2 - 1,
        np.clip(results['profit_loss_ratio'] / 3, -1, 1) if results['profit_loss_ratio'] > 0 else 0,
        np.clip(results['calmar_ratio'] / 2, -1, 1) if results['calmar_ratio'] != 0 else 0
    ]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values, 'o-', linewidth=2, color='#e74c3c')
    ax.fill(angles, values, alpha=0.25, color='#e74c3c')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(-1, 1)
    ax.set_title(f'{results["stock_name"]} 海龟策略绩效雷达图（归一化）',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True)
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  雷达图已保存: {save_path}')


def plot_exit_reasons(results: Dict, save_path: str):
    """绘制出场原因分布饼图"""
    reasons = results.get('exit_reasons', {})
    if not reasons:
        return

    labels_map = {
        'stop_loss': '止损出场', 'exit_signal': '反向突破出场', 'final': '期末清仓'
    }
    labels = [labels_map.get(k, k) for k in reasons.keys()]
    sizes = list(reasons.values())
    colors = ['#e74c3c', '#3498db', '#9b59b6']

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)]
    )
    ax.set_title(f'{results["stock_name"]} 海龟策略出场原因分布', fontsize=14, fontweight='bold')
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  出场饼图已保存: {save_path}')


def plot_period_comparison(all_results: List[Dict], save_path: str):
    """绘制不同通道周期对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    labels = [f'{r["entry_window"]}/{r["exit_window"]}' for r in all_results]
    x = np.arange(len(labels))
    width = 0.35

    total_returns = [r['total_return'] for r in all_results]
    bh_returns = [r['buy_hold_return'] for r in all_results]
    # 中国股市习惯：正收益红色，负收益绿色
    strat_colors = ['#e74c3c' if v >= 0 else '#27ae60' for v in total_returns]
    bh_colors = ['#f1948a' if v >= 0 else '#82e0aa' for v in bh_returns]
    axes[0, 0].bar(x - width/2, total_returns, width, color=strat_colors, label='策略总收益')
    axes[0, 0].bar(x + width/2, bh_returns, width, color=bh_colors, label='买入持有')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=30, ha='right')
    axes[0, 0].set_ylabel('收益率（%）')
    axes[0, 0].set_title('总收益率 vs 买入持有（红涨绿跌）')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    sharpes = [r['sharpe_ratio'] for r in all_results]
    mdds = [r['max_drawdown'] for r in all_results]
    axes[0, 1].bar(x, mdds, color='#c0392b', alpha=0.7, label='最大回撤')
    ax2 = axes[0, 1].twinx()
    ax2.plot(x, sharpes, 'o-', color='#2ecc71', linewidth=2, markersize=8, label='夏普比率')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=30, ha='right')
    axes[0, 1].set_ylabel('最大回撤（%）', color='#c0392b')
    ax2.set_ylabel('夏普比率', color='#2ecc71')
    axes[0, 1].set_title('夏普比率与最大回撤')
    axes[0, 1].legend(loc='upper left')
    ax2.legend(loc='upper right')
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    win_rates = [r['win_rate'] for r in all_results]
    pl_ratios = [r['profit_loss_ratio'] for r in all_results]
    axes[1, 0].bar(x, win_rates, color='#3498db', alpha=0.7, label='胜率')
    ax3 = axes[1, 0].twinx()
    ax3.plot(x, pl_ratios, 's-', color='#f39c12', linewidth=2, markersize=8, label='盈亏比')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=30, ha='right')
    axes[1, 0].set_ylabel('胜率（%）', color='#3498db')
    ax3.set_ylabel('盈亏比', color='#f39c12')
    axes[1, 0].set_title('胜率与盈亏比')
    axes[1, 0].legend(loc='upper left')
    ax3.legend(loc='upper right')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    n_trades = [r['n_trades'] for r in all_results]
    axes[1, 1].bar(x, n_trades, color='#9b59b6', alpha=0.7)
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=30, ha='right')
    axes[1, 1].set_ylabel('交易次数')
    axes[1, 1].set_title('交易次数对比')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    fig.suptitle('海龟策略不同通道周期综合对比（入场/出场周期）', fontsize=14, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  周期对比图已保存: {save_path}')


def plot_stock_comparison(stock_results: List[Dict], save_path: str):
    """绘制不同股票对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    stock_names = [r['stock_name'] for r in stock_results]
    x = np.arange(len(stock_names))
    width = 0.35

    total_returns = [r['total_return'] for r in stock_results]
    bh_returns = [r['buy_hold_return'] for r in stock_results]
    # 中国股市习惯：正收益红色，负收益绿色
    strat_colors = ['#e74c3c' if v >= 0 else '#27ae60' for v in total_returns]
    bh_colors = ['#f1948a' if v >= 0 else '#82e0aa' for v in bh_returns]
    axes[0, 0].bar(x - width/2, total_returns, width, color=strat_colors, label='策略总收益')
    axes[0, 0].bar(x + width/2, bh_returns, width, color=bh_colors, label='买入持有')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(stock_names)
    axes[0, 0].set_ylabel('收益率（%）')
    axes[0, 0].set_title('总收益率 vs 买入持有（红涨绿跌）')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    sharpes = [r['sharpe_ratio'] for r in stock_results]
    mdds = [r['max_drawdown'] for r in stock_results]
    axes[0, 1].bar(x, mdds, color='#c0392b', alpha=0.7, label='最大回撤')
    ax2 = axes[0, 1].twinx()
    ax2.plot(x, sharpes, 'o-', color='#2ecc71', linewidth=2, markersize=8, label='夏普比率')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(stock_names)
    axes[0, 1].set_ylabel('最大回撤（%）', color='#c0392b')
    ax2.set_ylabel('夏普比率', color='#2ecc71')
    axes[0, 1].set_title('夏普比率与最大回撤')
    axes[0, 1].legend(loc='upper left')
    ax2.legend(loc='upper right')
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    win_rates = [r['win_rate'] for r in stock_results]
    pl_ratios = [r['profit_loss_ratio'] for r in stock_results]
    axes[1, 0].bar(x, win_rates, color='#3498db', alpha=0.7, label='胜率')
    ax3 = axes[1, 0].twinx()
    ax3.plot(x, pl_ratios, 's-', color='#f39c12', linewidth=2, markersize=8, label='盈亏比')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(stock_names)
    axes[1, 0].set_ylabel('胜率（%）', color='#3498db')
    ax3.set_ylabel('盈亏比', color='#f39c12')
    axes[1, 0].set_title('胜率与盈亏比')
    axes[1, 0].legend(loc='upper left')
    ax3.legend(loc='upper right')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    annual_returns = [r['annual_return'] for r in stock_results]
    vols = [r['volatility'] for r in stock_results]
    axes[1, 1].bar(x, annual_returns, color='#9b59b6', alpha=0.7, label='年化收益')
    ax4 = axes[1, 1].twinx()
    ax4.plot(x, vols, 'd-', color='#e67e22', linewidth=2, markersize=8, label='年化波动率')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(stock_names)
    axes[1, 1].set_ylabel('年化收益（%）', color='#9b59b6')
    ax4.set_ylabel('波动率（%）', color='#e67e22')
    axes[1, 1].set_title('年化收益与波动率')
    axes[1, 1].legend(loc='upper left')
    ax4.legend(loc='upper right')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    fig.suptitle('不同股票海龟策略综合对比', fontsize=14, fontweight='bold')
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  多股对比图已保存: {save_path}')


def plot_multi_param_heatmap(all_results: List[Dict], save_path: str):
    """绘制多股票x多参数超额收益热力图"""
    import matplotlib.colors as mcolors

    stock_names = sorted(set(r['stock_name'] for r in all_results))
    param_labels = ['5/3', '5/5', '10/5', '10/10', '15/7', '20/10', '30/15', '55/20']

    # 构建矩阵：行=股票，列=参数
    matrix = np.full((len(stock_names), len(param_labels)), np.nan)
    for r in all_results:
        si = stock_names.index(r['stock_name'])
        pl = f'{r["entry_window"]}/{r["exit_window"]}'
        if pl in param_labels:
            pi = param_labels.index(pl)
            matrix[si, pi] = r['excess_return']

    fig, ax = plt.subplots(figsize=(12, 5))

    # 红绿发散色：正收益红色（跑赢），负收益绿色（跑输），符合中国股市习惯
    cmap = plt.cm.RdYlGn_r
    vmax = max(abs(np.nanmin(matrix)), abs(np.nanmax(matrix)))
    vmin = -vmax
    im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)

    ax.set_xticks(np.arange(len(param_labels)))
    ax.set_xticklabels(param_labels, fontsize=11)
    ax.set_yticks(np.arange(len(stock_names)))
    ax.set_yticklabels(stock_names, fontsize=12)
    ax.set_xlabel('参数组合（入场/出场周期）', fontsize=12)
    ax.set_ylabel('股票', fontsize=12)

    # 在每个格子里写数值
    for i in range(len(stock_names)):
        for j in range(len(param_labels)):
            val = matrix[i, j]
            if not np.isnan(val):
                color = 'white' if abs(val) > vmax * 0.6 else 'black'
                ax.text(j, i, f'{val:+.1f}%', ha='center', va='center',
                        fontsize=10, fontweight='bold', color=color)

    ax.set_title('海龟策略多股票 × 多参数超额收益热力图（%）\n'
                 '红色=跑赢买入持有，绿色=跑输买入持有',
                 fontsize=13, fontweight='bold')

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('超额收益（%）', fontsize=11)

    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  多参数热力图已保存: {save_path}')
