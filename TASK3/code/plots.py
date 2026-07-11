# -*- coding: utf-8 -*-
"""
绘图模块：策略信号图、回测净值曲线、回撤图、雷达图、出场饼图、对比图。
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict

from config import BacktestConfig, IMAGE_DIR

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def _get_period_subdir(short_period: int, long_period: int) -> str:
    """根据均线周期获取图片子目录，如 '5_20'"""
    return os.path.join(IMAGE_DIR, f'{short_period}_{long_period}')


def _ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def plot_strategy(df: pd.DataFrame, config: BacktestConfig,
                  buy_dates: List[datetime], buy_prices: List[float],
                  sell_dates: List[datetime], sell_prices: List[float],
                  save_path: str):
    """绘制策略信号图：股价 + 均线 + 买卖信号"""
    sp, lp = config.entry.short_period, config.entry.long_period
    ma_s, ma_l = f'MA{sp}', f'MA{lp}'

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df['trade_date'], df['close'], color='#2c3e50', linewidth=1, label='收盘价', alpha=0.8)
    ax.plot(df['trade_date'], df[ma_s], color='#e74c3c', linewidth=1.5, label=f'MA{sp}（短均线）')
    ax.plot(df['trade_date'], df[ma_l], color='#3498db', linewidth=1.5, label=f'MA{lp}（长均线）')

    if buy_dates:
        ax.scatter(buy_dates, buy_prices, marker='^', color='#e74c3c', s=150, zorder=5,
                   label='买入信号（金叉+过滤）', edgecolors='darkred', linewidths=0.5)
    if sell_dates:
        ax.scatter(sell_dates, sell_prices, marker='v', color='#27ae60', s=150, zorder=5,
                   label='卖出信号', edgecolors='darkgreen', linewidths=0.5)

    ax.set_title(f'双均线策略交易信号图（MA{sp}/MA{lp}）', fontsize=14, fontweight='bold')
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


def plot_backtest(df_bt: pd.DataFrame, results: Dict, save_path: str):
    """绘制回测结果图：策略净值 vs 买入持有"""
    fig, ax = plt.subplots(figsize=(14, 6))
    initial = results['initial_capital']

    ax.plot(df_bt['trade_date'], df_bt['portfolio_value'], color='#e74c3c', linewidth=1.5,
            label=f'双均线策略（总收益 {results["total_return"]}%，年化 {results["annual_return"]}%）')

    first_price = df_bt['close'].iloc[0]
    shares_bh = int(initial / first_price)
    bh_value = shares_bh * df_bt['close']
    ax.plot(df_bt['trade_date'], bh_value, color='#3498db', linewidth=1.5,
            label=f'买入持有（总收益 {results["buy_hold_return"]}%）', alpha=0.8)

    ax.axhline(y=initial, color='gray', linestyle='--', linewidth=0.8, label='初始资金')

    ax.set_title(f'策略回测净值曲线（MA{results["short_period"]}/MA{results["long_period"]}）',
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

    ax.set_title('策略最大回撤（MDD）分析', fontsize=14, fontweight='bold')
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
    ax.set_title('策略绩效雷达图（归一化）', fontsize=14, fontweight='bold', pad=20)
    ax.grid(True)
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_exit_reasons(results: Dict, save_path: str):
    """绘制出场原因分布饼图"""
    reasons = results.get('exit_reasons', {})
    if not reasons:
        return

    labels_map = {
        'signal': '信号出场', 'take_profit': '止盈出场',
        'stop_loss': '止损出场', 'time_exit': '时间出场', 'final': '期末清仓'
    }
    labels = [labels_map.get(k, k) for k in reasons.keys()]
    sizes = list(reasons.values())
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)]
    )
    ax.set_title('出场原因分布', fontsize=14, fontweight='bold')
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_position_comparison(position_results: List[Dict], save_path: str):
    """绘制不同仓位管理模式对比"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    labels = [r['position_mode'] for r in position_results]
    x = np.arange(len(labels))

    total_returns = [r['total_return'] for r in position_results]
    bh_returns = [r['buy_hold_return'] for r in position_results]
    axes[0, 0].bar(x - 0.2, total_returns, 0.4, color='#e74c3c', label='策略总收益')
    axes[0, 0].bar(x + 0.2, bh_returns, 0.4, color='#3498db', label='买入持有')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=15, ha='right')
    axes[0, 0].set_ylabel('收益率（%）')
    axes[0, 0].set_title('总收益率 vs 买入持有')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    mdds = [r['max_drawdown'] for r in position_results]
    sharpes = [r['sharpe_ratio'] for r in position_results]
    axes[0, 1].bar(x, mdds, color='#c0392b', alpha=0.7, label='最大回撤')
    ax2 = axes[0, 1].twinx()
    ax2.plot(x, sharpes, 'o-', color='#2ecc71', linewidth=2, markersize=8, label='夏普比率')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=15, ha='right')
    axes[0, 1].set_ylabel('最大回撤（%）', color='#c0392b')
    ax2.set_ylabel('夏普比率', color='#2ecc71')
    axes[0, 1].set_title('最大回撤与夏普比率')
    axes[0, 1].legend(loc='upper left')
    ax2.legend(loc='upper right')

    win_rates = [r['win_rate'] for r in position_results]
    pl_ratios = [r['profit_loss_ratio'] for r in position_results]
    axes[1, 0].bar(x, win_rates, color='#3498db', alpha=0.7, label='胜率')
    ax3 = axes[1, 0].twinx()
    ax3.plot(x, pl_ratios, 's-', color='#f39c12', linewidth=2, markersize=8, label='盈亏比')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=15, ha='right')
    axes[1, 0].set_ylabel('胜率（%）', color='#3498db')
    ax3.set_ylabel('盈亏比', color='#f39c12')
    axes[1, 0].set_title('胜率与盈亏比')
    axes[1, 0].legend(loc='upper left')
    ax3.legend(loc='upper right')

    n_trades = [r['n_trades'] for r in position_results]
    axes[1, 1].bar(x, n_trades, color='#9b59b6', alpha=0.7)
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=15, ha='right')
    axes[1, 1].set_ylabel('交易次数')
    axes[1, 1].set_title('交易次数对比')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    fig.suptitle('长江电力（600900.SH）不同仓位管理模式综合对比', fontsize=14, fontweight='bold')
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_period_comparison(all_results: List[Dict], save_path: str):
    """绘制不同均线周期对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    periods_label = [f'MA{r["short_period"]}/{r["long_period"]}' for r in all_results]
    x = np.arange(len(periods_label))
    width = 0.35

    total_returns = [r['total_return'] for r in all_results]
    bh_returns = [r['buy_hold_return'] for r in all_results]
    axes[0, 0].bar(x - width/2, total_returns, width, color='#e74c3c', label='策略总收益')
    axes[0, 0].bar(x + width/2, bh_returns, width, color='#3498db', label='买入持有')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(periods_label)
    axes[0, 0].set_ylabel('收益率（%）')
    axes[0, 0].set_title('总收益率 vs 买入持有')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    sharpes = [r['sharpe_ratio'] for r in all_results]
    mdds = [r['max_drawdown'] for r in all_results]
    axes[0, 1].bar(x, mdds, color='#c0392b', alpha=0.7, label='最大回撤')
    ax2 = axes[0, 1].twinx()
    ax2.plot(x, sharpes, 'o-', color='#2ecc71', linewidth=2, markersize=8, label='夏普比率')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(periods_label)
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
    axes[1, 0].set_xticklabels(periods_label)
    axes[1, 0].set_ylabel('胜率（%）', color='#3498db')
    ax3.set_ylabel('盈亏比', color='#f39c12')
    axes[1, 0].set_title('胜率与盈亏比')
    axes[1, 0].legend(loc='upper left')
    ax3.legend(loc='upper right')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    annual_returns = [r['annual_return'] for r in all_results]
    vols = [r['volatility'] for r in all_results]
    axes[1, 1].bar(x, annual_returns, color='#9b59b6', alpha=0.7, label='年化收益')
    ax4 = axes[1, 1].twinx()
    ax4.plot(x, vols, 'd-', color='#e67e22', linewidth=2, markersize=8, label='年化波动率')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(periods_label)
    axes[1, 1].set_ylabel('年化收益（%）', color='#9b59b6')
    ax4.set_ylabel('波动率（%）', color='#e67e22')
    axes[1, 1].set_title('年化收益与波动率')
    axes[1, 1].legend(loc='upper left')
    ax4.legend(loc='upper right')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    fig.suptitle('长江电力（600900.SH）不同均线周期综合对比', fontsize=14, fontweight='bold')
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_stock_comparison(stock_results: List[Dict], save_path: str):
    """绘制不同股票对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    stock_names = [r['name'] for r in stock_results]
    x = np.arange(len(stock_names))
    width = 0.35

    total_returns = [r['total_return'] for r in stock_results]
    bh_returns = [r['buy_hold_return'] for r in stock_results]
    axes[0, 0].bar(x - width/2, total_returns, width, color='#e74c3c', label='策略总收益')
    axes[0, 0].bar(x + width/2, bh_returns, width, color='#3498db', label='买入持有')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(stock_names)
    axes[0, 0].set_ylabel('收益率（%）')
    axes[0, 0].set_title('总收益率 vs 买入持有')
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

    fig.suptitle('不同股票双均线策略（MA5/MA20）综合对比', fontsize=14, fontweight='bold')
    fig.tight_layout()
    _ensure_dir(os.path.dirname(save_path))
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
