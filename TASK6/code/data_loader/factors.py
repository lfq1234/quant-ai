# -*- coding: utf-8 -*-
"""Alpha 因子计算：12 个技术面因子"""

import numpy as np
import pandas as pd

import config


def _calc_rsi(close, period=14):
    """计算 RSI 指标"""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calc_factors(df):
    """
    对单只股票日线数据计算 12 个因子。

    输入 df 需包含: trade_date, adj_close, vol, amount, close
    返回: DataFrame, 含 trade_date + 12 个因子列
    """
    d = df.copy().sort_values('trade_date').reset_index(drop=True)
    close = d['adj_close']
    vol = d['vol']
    ret = close.pct_change()

    f = pd.DataFrame(index=d.index)
    f['trade_date'] = d['trade_date']

    # --- 动量类 ---
    f['mom_1m'] = close / close.shift(21) - 1
    f['mom_3m'] = close / close.shift(63) - 1
    f['mom_12m_1m'] = close.shift(21) / close.shift(252) - 1
    f['reversal_5d'] = -ret.rolling(5).sum()

    # --- 换手率 / 流动性 ---
    f['turn_20d'] = vol.rolling(20).mean()
    f['vol_ratio'] = vol.rolling(5).mean() / vol.rolling(20).mean()

    # --- 波动率 ---
    f['vol_20d'] = ret.rolling(20).std()
    f['vol_5d'] = ret.rolling(5).std()
    f['vol_change'] = f['vol_5d'] - f['vol_20d']

    # --- 技术指标 ---
    ma20 = close.rolling(20).mean()
    f['ma_bias_20'] = close / ma20 - 1
    f['rsi_14'] = _calc_rsi(close, 14)
    std20 = close.rolling(20).std()
    f['bb_pos'] = (close - ma20) / (2 * std20)

    # --- 规模 ---
    f['ln_market_cap'] = np.log(close * vol * 100 + 1)  # 近似市值

    return f


def get_quarter_end_dates(df):
    """从日线数据中提取所有季度末交易日"""
    d = df.copy()
    d['year'] = d['trade_date'].dt.year
    d['quarter'] = d['trade_date'].dt.quarter
    # 每个季度最后一个交易日
    qe = d.groupby(['year', 'quarter'])['trade_date'].max().reset_index()
    qe['quarter_str'] = qe['year'].astype(str) + 'Q' + qe['quarter'].astype(str)
    return qe[['trade_date', 'quarter_str']]
