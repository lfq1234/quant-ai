# -*- coding: utf-8 -*-
"""
技术指标模块：唐奇安通道（Donchian Channel）和 ATR 计算。
"""

import pandas as pd
import numpy as np

from config import TurtleConfig


def calc_donchian_channel(df: pd.DataFrame, config: TurtleConfig) -> pd.DataFrame:
    """
    计算唐奇安通道：上轨 = 过去 entry_window 日最高价，下轨 = 过去 entry_window 日最低价。
    """
    df = df.copy()
    ew = config.entry_window
    xw = config.exit_window

    # 入场通道：过去 entry_window 日的最高价/最低价（不含当天，用 shift 排除当日）
    df['channel_high'] = df['high'].shift(1).rolling(window=ew, min_periods=ew).max()
    df['channel_low']  = df['low'].shift(1).rolling(window=ew, min_periods=ew).min()

    # 出场通道：过去 exit_window 日的最低价（不含当天）
    df['exit_low'] = df['low'].shift(1).rolling(window=xw, min_periods=xw).min()

    # 中线（通道中点，用于可视化）
    df['channel_mid'] = (df['channel_high'] + df['channel_low']) / 2.0

    return df


def calc_atr(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """计算 ATR（Average True Range）平均真实波幅"""
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=period).mean()
    return atr


def calc_indicators(df: pd.DataFrame, config: TurtleConfig) -> pd.DataFrame:
    """计算全部技术指标：唐奇安通道 + ATR"""
    df = df.copy()
    df = calc_donchian_channel(df, config)
    df['ATR'] = calc_atr(df, config.atr_period)
    df['daily_return'] = df['close'].pct_change()
    return df
