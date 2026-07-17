# -*- coding: utf-8 -*-
"""数据划分：按时间顺序划分训练集 / 测试集（严禁随机打乱）"""

import config


def split_panel(panel):
    """
    按年份划分：训练集 year < TRAIN_END_YEAR，测试集 year >= TRAIN_END_YEAR。

    Returns:
        train_df, test_df: 两个 DataFrame
    """
    panel = panel.copy()
    panel['year'] = panel['quarter_str'].str[:4].astype(int)

    train_df = panel[panel['year'] < config.TRAIN_END_YEAR].copy()
    test_df = panel[panel['year'] >= config.TRAIN_END_YEAR].copy()

    print(f'[Panel Split] Time-ordered split (no shuffle)')
    print(f'  Train: {len(train_df)} rows, {train_df["quarter_str"].nunique()} quarters '
          f'({train_df["quarter_str"].min()} ~ {train_df["quarter_str"].max()})')
    print(f'  Test:  {len(test_df)} rows, {test_df["quarter_str"].nunique()} quarters '
          f'({test_df["quarter_str"].min()} ~ {test_df["quarter_str"].max()})')

    return train_df, test_df
