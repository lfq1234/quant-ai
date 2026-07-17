# -*- coding: utf-8 -*-
"""季度调仓回测引擎"""

import pandas as pd
import numpy as np

import config
from .portfolio import select_top_n


def backtest_model(pred_df, n=None, cost=None):
    """
    对单个模型的预测结果执行季度调仓回测。

    策略：每季度末选 Top-N 等权持有，持有 1 季度，扣减交易成本。

    Returns:
        returns_df: DataFrame[quarter_str, portfolio_return, n_holdings]
    """
    if n is None:
        n = config.TOP_N
    if cost is None:
        cost = config.COST_PER_TRADE

    quarters = sorted(pred_df['quarter_str'].unique())
    records = []

    for q in quarters:
        selected = select_top_n(pred_df, q, n)
        if len(selected) == 0:
            continue
        port_ret = selected['actual'].mean()
        port_ret -= cost  # 单边交易成本
        records.append({
            'quarter_str': q,
            'portfolio_return': port_ret,
            'n_holdings': len(selected),
        })

    return pd.DataFrame(records)


def backtest_all_models(results, n=None):
    """
    对所有模型执行回测，返回 {model_name: returns_df}。

    同时对每个模型测试不同 N 值（附加题）。
    """
    all_returns = {}
    for name, res in results.items():
        all_returns[name] = backtest_model(res['pred_df'], n=n)
        print(f'  [{name}] backtest done: {len(all_returns[name])} quarters')

    # 附加题：Random Forest 不同持仓数
    if 'Random Forest' in results:
        bonus = {}
        for n_val in [10, 30, 50, 100]:
            bonus[f'N={n_val}'] = backtest_model(results['Random Forest']['pred_df'], n=n_val)
        all_returns['_bonus_N_sensitivity'] = bonus

    return all_returns
