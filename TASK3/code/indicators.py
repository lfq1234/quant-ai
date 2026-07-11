# -*- coding: utf-8 -*-
"""
技术指标模块：RSI、ATR、均线、波动率等指标计算。
"""

import numpy as np
import pandas as pd

from config import BacktestConfig


def calc_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI 指标"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算 ATR（真实波动幅度）"""
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=period).mean()
    return atr


def calc_indicators(df: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
    """计算全部技术指标：均线、RSI、成交量均线、ATR、波动率"""
    df = df.copy()
    sp, lp = config.entry.short_period, config.entry.long_period

    df[f'MA{sp}'] = df['close'].rolling(window=sp, min_periods=sp).mean()
    df[f'MA{lp}'] = df['close'].rolling(window=lp, min_periods=lp).mean()

    if config.entry.use_rsi_filter:
        df['RSI'] = calc_rsi(df['close'], config.entry.rsi_period)

    if config.entry.use_volume_filter:
        df['vol_ma'] = df['vol'].rolling(
            window=config.entry.volume_period,
            min_periods=config.entry.volume_period
        ).mean()

    df['ATR'] = calc_atr(df, config.risk_parity_atr_period)
    df['daily_return'] = df['close'].pct_change()
    df['volatility_20'] = df['daily_return'].rolling(
        window=20, min_periods=20
    ).std() * np.sqrt(252)

    return df
