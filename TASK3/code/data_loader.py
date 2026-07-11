# -*- coding: utf-8 -*-
"""
数据加载模块：从 CSV 或 Tushare API 获取股价数据。
"""

import os
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta

from config import DATA_DIR, TOKEN


def load_data(csv_path: str) -> pd.DataFrame:
    """加载 CSV 股价数据"""
    df = pd.read_csv(csv_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    return df


def load_stock_data(filename: str) -> pd.DataFrame:
    """从 data 目录按文件名加载 CSV"""
    return load_data(os.path.join(DATA_DIR, filename))


def fetch_stock_data(ts_code: str, token: str = TOKEN) -> pd.DataFrame:
    """通过 Tushare 获取股票近一年日线数据"""
    ts.set_token(token)
    pro = ts.pro_api()
    end_date = datetime.today().strftime('%Y%m%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y%m%d')
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df = df.sort_values('trade_date').reset_index(drop=True)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    return df


def save_stock_data(df: pd.DataFrame, ts_code: str) -> str:
    """保存数据到 data 目录，返回保存路径"""
    filename = f'{ts_code.split(".")[0]}_data.csv'
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return path
