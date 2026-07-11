# -*- coding: utf-8 -*-
"""
买卖信号模块：基于唐奇安通道的突破信号生成。
"""

import pandas as pd
from config import TurtleConfig


def generate_signals(df: pd.DataFrame, config: TurtleConfig) -> pd.DataFrame:
    """
    生成买入/卖出信号：
    - 买入：价格突破 entry_window 日最高价（通道上轨），且突破前一日的最高价
    - 卖出：价格跌破 exit_window 日最低价（反向突破）
    """
    df = df.copy()
    df['signal'] = 0

    # 买入：价格突破通道上轨（昨日最高价/前日通道上轨），今日close > channel_high
    # 注意：channel_high 是前 entry_window 天的最高价（不含当天），所以直接用 close > channel_high 即可
    buy_signal = df['close'] > df['channel_high']

    # 卖出：价格跌破 exit_window 日最低价
    sell_signal = df['close'] < df['exit_low']

    df.loc[buy_signal, 'signal'] = 1
    df.loc[sell_signal, 'signal'] = -1

    return df
