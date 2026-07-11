# -*- coding: utf-8 -*-
"""
入场规则模块：均线金叉 + RSI 过滤 + 成交量过滤 + 趋势强度过滤。
"""

import pandas as pd

from config import BacktestConfig


def generate_signals(df: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
    """生成入场信号：均线金叉 + 多维度过滤"""
    df = df.copy()
    sp, lp = config.entry.short_period, config.entry.long_period
    ma_s, ma_l = f'MA{sp}', f'MA{lp}'

    df['ma_diff'] = df[ma_s] - df[ma_l]
    df['signal'] = 0

    # 基础金叉：今日差值 > 0 且 昨日差值 <= 0
    golden_cross = (df['ma_diff'] > 0) & (df['ma_diff'].shift(1) <= 0)

    # 入场过滤条件
    filters = golden_cross

    if config.entry.use_rsi_filter:
        filters = filters & (df['RSI'].notna()) & (df['RSI'] < config.entry.rsi_upper)

    if config.entry.use_volume_filter:
        filters = filters & (df['vol_ma'].notna()) & \
                  (df['vol'] >= df['vol_ma'] * config.entry.volume_threshold)

    if config.entry.use_trend_filter:
        filters = filters & (df['close'] > df[ma_l])

    df.loc[filters, 'signal'] = 1
    # 死叉：今日差值 < 0 且 昨日差值 >= 0
    df.loc[(df['ma_diff'] < 0) & (df['ma_diff'].shift(1) >= 0), 'signal'] = -1

    return df
