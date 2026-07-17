# -*- coding: utf-8 -*-
"""Tushare API 封装：批量下载日线 + 复权因子，缓存到 CSV"""

import os
import time
import pandas as pd
import tushare as ts

import config

from .universe import UNIVERSE, UNIVERSE_CODES

# Tushare Pro token（沿用 TASK1）
TOKEN = 'eedeac8183a4726f28d85aade5731a3182166105900e5ddfd6c8b402'

# 数据时间范围
START_DATE = '20140101'  # 多取一年用于计算 12 月动量
END_DATE = '20241231'


def _get_pro():
    """初始化 Tushare Pro API"""
    ts.set_token(TOKEN)
    return ts.pro_api()


def _download_one(pro, ts_code):
    """下载单只股票的日线行情（不复权，用 pct_chg 计算收益）"""
    daily = pro.daily(ts_code=ts_code, start_date=START_DATE, end_date=END_DATE)
    time.sleep(0.16)
    if daily is None or len(daily) == 0:
        return None

    daily = daily.sort_values('trade_date').reset_index(drop=True)
    # 用 pct_chg 累积构建后复权收盘价，避免调用 adj_factor API（限流严重）
    daily['pct_chg'] = daily['pct_chg'].fillna(0.0)
    daily['ret_factor'] = (1.0 + daily['pct_chg'] / 100.0).cumprod()
    last_close = daily['close'].iloc[-1]
    daily['adj_close'] = last_close / daily['ret_factor'].iloc[-1] * daily['ret_factor']
    daily['trade_date'] = pd.to_datetime(daily['trade_date'], format='%Y%m%d')
    return daily


def download_all():
    """批量下载全部 100 只股票日线数据，保存到 data/raw_daily/"""
    os.makedirs(config.RAW_DIR, exist_ok=True)
    pro = _get_pro()
    codes = UNIVERSE_CODES

    success, fail = 0, 0
    for i, code in enumerate(codes):
        csv_path = os.path.join(config.RAW_DIR, f'{code}.csv')
        if os.path.exists(csv_path):
            success += 1
            continue
        print(f'  [{i+1}/{len(codes)}] Downloading {code} ({UNIVERSE.get(code, "")})...', end=' ')
        try:
            df = _download_one(pro, code)
            if df is not None:
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f'{len(df)} rows')
                success += 1
            else:
                print('EMPTY')
                fail += 1
        except Exception as e:
            print(f'ERROR: {e}')
            fail += 1
    print(f'  Download complete: {success} ok, {fail} failed')
    return success, fail


def load_daily_data(ts_code):
    """从 CSV 加载单只股票日线数据"""
    csv_path = os.path.join(config.RAW_DIR, f'{ts_code}.csv')
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    return df
