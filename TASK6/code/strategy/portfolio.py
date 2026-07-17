# -*- coding: utf-8 -*-
"""组合构建：Top-N 等权选股"""


def select_top_n(pred_df, quarter, n=30):
    """
    在某个季度的截面预测中，选出预测收益最高的 N 只股票。

    Returns:
        selected: DataFrame, 含 ts_code, pred, actual（等权组合成员）
    """
    q_data = pred_df[pred_df['quarter_str'] == quarter].copy()
    selected = q_data.nlargest(n, 'pred')
    return selected
