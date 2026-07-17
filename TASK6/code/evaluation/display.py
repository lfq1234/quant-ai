# -*- coding: utf-8 -*-
"""评估结果展示：打印业绩指标表"""

import pandas as pd


def print_metrics_table(summary):
    """打印多模型业绩对比表"""
    print('\n  ========== Strategy Performance Summary ==========')
    display_cols = ['model', 'annual_return', 'annual_vol', 'sharpe',
                    'max_drawdown', 'quarter_win_rate']
    avail = [c for c in display_cols if c in summary.columns]
    print(summary[avail].to_string(index=False))
    print()
