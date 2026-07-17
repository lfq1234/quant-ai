# -*- coding: utf-8 -*-
"""截面面板构建：季度 × 股票 → 因子 + 下季度收益"""

import os
import pandas as pd
import numpy as np

import config
from .universe import UNIVERSE_CODES
from .tushare_api import load_daily_data
from .factors import calc_factors, get_quarter_end_dates


def _winsorize(s, lower=0.01, upper=0.99):
    """缩尾处理：将极端值截断到 1%/99% 分位"""
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lo, hi)


def _cross_sectional_standardize(panel, feature_cols):
    """按季度截面标准化每个因子"""
    for col in feature_cols:
        panel[col] = panel.groupby('quarter_str')[col].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-8)
        )
    return panel


def build_panel():
    """
    构建截面面板数据。

    流程：
      1. 逐只股票加载日线 → 计算因子
      2. 提取季度末因子快照
      3. 计算下季度收益（应变量）
      4. 合并为面板，缩尾 + 截面标准化

    Returns:
        panel: DataFrame, 列 = [quarter_str, ts_code, *features, next_return]
    """
    all_snapshots = []

    for i, code in enumerate(UNIVERSE_CODES):
        csv_path = os.path.join(config.RAW_DIR, f'{code}.csv')
        if not os.path.exists(csv_path):
            continue
        df = load_daily_data(code)
        if len(df) < 252:
            continue

        # 计算因子
        factors = calc_factors(df)

        # 季度末日期
        qe = get_quarter_end_dates(df)

        # 在季度末日期上提取因子快照
        snapshot = factors[factors['trade_date'].isin(qe['trade_date'])].copy()
        snapshot = snapshot.merge(qe, on='trade_date', how='inner')
        snapshot['ts_code'] = code

        # 计算下季度收益：adj_close 下季度末 / 本季度末 - 1
        adj_close_qe = df[df['trade_date'].isin(qe['trade_date'])][['trade_date', 'adj_close']].copy()
        adj_close_qe = adj_close_qe.sort_values('trade_date').reset_index(drop=True)
        adj_close_qe['next_return'] = adj_close_qe['adj_close'].shift(-1) / adj_close_qe['adj_close'] - 1
        adj_close_qe = adj_close_qe[['trade_date', 'next_return']]

        snapshot = snapshot.merge(adj_close_qe, on='trade_date', how='left')
        all_snapshots.append(snapshot)

        if (i + 1) % 20 == 0:
            print(f'  [{i+1}/{len(UNIVERSE_CODES)}] Processed {code}')

    panel = pd.concat(all_snapshots, ignore_index=True)

    # 只保留 2015-2024 的数据（2014 用于计算 12 月动量）
    panel['year'] = panel['quarter_str'].str[:4].astype(int)
    panel = panel[(panel['year'] >= 2015) & (panel['year'] <= 2024)]

    # 删除无下季度收益的行（最后一个季度）
    panel = panel.dropna(subset=['next_return'])

    # 只保留因子列 + 元信息
    keep_cols = ['quarter_str', 'ts_code', 'trade_date'] + config.FEATURE_COLS + ['next_return']
    panel = panel[[c for c in keep_cols if c in panel.columns]]

    # 因子缺失值填充（截面中位数）
    for col in config.FEATURE_COLS:
        panel[col] = panel.groupby('quarter_str')[col].transform(
            lambda x: x.fillna(x.median())
        )
        panel[col] = panel[col].fillna(0)

    # 缩尾 + 截面标准化
    for col in config.FEATURE_COLS:
        panel[col] = panel.groupby('quarter_str')[col].transform(_winsorize)
    panel = _cross_sectional_standardize(panel, config.FEATURE_COLS)

    # 最终安全网：确保无 NaN
    panel[config.FEATURE_COLS] = panel[config.FEATURE_COLS].fillna(0)
    panel = panel.dropna(subset=['next_return'])

    # 排序
    panel = panel.sort_values(['quarter_str', 'ts_code']).reset_index(drop=True)

    print(f'  Panel built: {len(panel)} rows, {panel["ts_code"].nunique()} stocks, '
          f'{panel["quarter_str"].nunique()} quarters')
    print(f'  Quarters: {panel["quarter_str"].min()} ~ {panel["quarter_str"].max()}')

    return panel
