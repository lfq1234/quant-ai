# -*- coding: utf-8 -*-
"""业绩评估指标：年化收益、Sharpe、回撤、信息比率、IC"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr


def calc_metrics(returns_df, bench_df=None):
    """
    计算策略核心业绩指标。

    Args:
        returns_df: DataFrame[quarter_str, portfolio_return]
        bench_df: DataFrame[quarter_str, benchmark_return]（可选）

    Returns:
        dict: annual_return, annual_vol, sharpe, max_drawdown, ...
    """
    r = returns_df['portfolio_return'].values
    n_quarters = len(r)
    n_years = n_quarters / 4

    # 累计净值
    cum = np.cumprod(1 + r)
    total_return = cum[-1] - 1

    # 年化收益
    annual_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0

    # 年化波动率
    annual_vol = np.std(r, ddof=1) * np.sqrt(4) if n_quarters > 1 else 0

    # Sharpe Ratio（无风险利率假设 0）
    sharpe = annual_return / annual_vol if annual_vol > 0 else 0

    # 最大回撤
    running_max = np.maximum.accumulate(cum)
    drawdown = cum / running_max - 1
    max_drawdown = np.min(drawdown)

    # 季度胜率
    quarter_win_rate = np.mean(r > 0)

    result = {
        'total_return': total_return,
        'annual_return': annual_return,
        'annual_vol': annual_vol,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'quarter_win_rate': quarter_win_rate,
        'n_quarters': n_quarters,
    }

    # 相对基准指标
    if bench_df is not None:
        merged = returns_df.merge(bench_df, on='quarter_str', how='inner')
        excess = merged['portfolio_return'] - merged['benchmark_return']
        result['excess_return'] = excess.mean() * 4  # 年化超额
        result['info_ratio'] = (excess.mean() / excess.std() * np.sqrt(4)
                                if excess.std() > 0 else 0)
        result['win_rate_vs_bench'] = np.mean(excess > 0)
        result['bench_annual_return'] = _calc_annual(merged['benchmark_return'].values)

    return result


def _calc_annual(r):
    """从季度收益序列计算年化收益"""
    if len(r) == 0:
        return 0
    cum = np.cumprod(1 + r)
    n_years = len(r) / 4
    return (cum[-1]) ** (1 / n_years) - 1 if n_years > 0 else 0


def calc_ic(pred_df):
    """
    计算每个季度的 IC（Pearson）和 Rank IC（Spearman）。

    IC = corr(预测收益, 实际收益)
    Rank IC = spearman_corr(预测收益, 实际收益)

    Returns:
        ic_df: DataFrame[quarter_str, ic, rank_ic]
    """
    records = []
    for q in sorted(pred_df['quarter_str'].unique()):
        q_data = pred_df[pred_df['quarter_str'] == q]
        if len(q_data) < 5:
            continue
        ic, _ = pearsonr(q_data['pred'], q_data['actual'])
        ric, _ = spearmanr(q_data['pred'], q_data['actual'])
        records.append({'quarter_str': q, 'ic': ic, 'rank_ic': ric})

    ic_df = pd.DataFrame(records)
    if len(ic_df) == 0:
        ic_df = pd.DataFrame(columns=['quarter_str', 'ic', 'rank_ic'])
    ic_df['ic_mean'] = ic_df['ic'].mean() if 'ic' in ic_df.columns else 0
    ic_df['rank_ic_mean'] = ic_df['rank_ic'].mean() if 'rank_ic' in ic_df.columns else 0
    return ic_df


def evaluate_all_models(all_returns, bench_df, results):
    """
    评估所有模型的回测业绩 + IC。

    Returns:
        summary: DataFrame, 每行一个模型
        ic_dict: {model_name: ic_df}
    """
    rows = []
    ic_dict = {}

    for name, ret_df in all_returns.items():
        if name.startswith('_'):
            continue  # 跳过附加题
        m = calc_metrics(ret_df, bench_df)
        rows.append({'model': name, **m})

        # IC
        if name in results:
            ic_dict[name] = calc_ic(results[name]['pred_df'])

    summary = pd.DataFrame(rows)
    # 保留 4 位小数
    float_cols = ['total_return', 'annual_return', 'annual_vol', 'sharpe',
                  'max_drawdown', 'quarter_win_rate']
    for col in float_cols:
        if col in summary.columns:
            summary[col] = summary[col].round(4)

    return summary, ic_dict
