# -*- coding: utf-8 -*-
"""方案 B：长江电力日线数据加载与技术特征工程"""

import pandas as pd
import config


def _calc_rsi(close, period=14):
    """计算 RSI 指标"""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def load_stock_data(csv_path=None):
    """
    加载长江电力日线数据，构造技术特征，生成二分类标签。

    特征 X:
      - MA 偏离度（MA5/MA10/MA20）
      - RSI(14)
      - 成交量变化率
      - 日内波动率
      - 当日涨跌幅
      - 5日/10日动量
      - 5日波动率
      - 量比（成交量/5日均量）

    标签 y:
      - 1 = 次日上涨（pct_chg > 0）
      - 0 = 次日下跌（pct_chg <= 0）
    """
    if csv_path is None:
        csv_path = config.STOCK_CSV

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)

    close = df['close']
    vol = df['vol']
    high = df['high']
    low = df['low']
    pre_close = df['pre_close']

    # --- 构造特征 ---
    features = pd.DataFrame(index=df.index)

    # 1. MA 偏离度
    for ma_period in config.MA_PERIODS:
        ma = close.rolling(window=ma_period).mean()
        features[f'ma{ma_period}_dev'] = (close - ma) / ma

    # 2. RSI
    features['rsi_14'] = _calc_rsi(close, config.RSI_PERIOD)

    # 3. 成交量变化率
    features['vol_chg'] = vol.pct_change()

    # 4. 日内波动率
    features['intraday_vol'] = (high - low) / pre_close

    # 5. 当日涨跌幅
    features['pct_chg'] = df['pct_chg']

    # 6. 动量（N日收益率）
    for mom_period in config.MOMENTUM_PERIODS:
        features[f'momentum_{mom_period}'] = close.pct_change(mom_period)

    # 7. 5日波动率
    features['volatility_5'] = close.pct_change().rolling(window=config.VOLATILITY_WINDOW).std()

    # 8. 量比
    features['vol_ratio'] = vol / vol.rolling(window=5).mean()

    # --- 构造标签：次日涨跌 ---
    features['target'] = (df['pct_chg'].shift(-1) > 0).astype(int)

    # --- 去除 NaN 行 ---
    features = features.dropna()

    # 分离 X 和 y
    y = features['target']
    X = features.drop(columns=['target'])
    feature_names = list(X.columns)

    # 保留日期信息（仅用于展示，不参与训练）
    dates = df['trade_date'].iloc[X.index].reset_index(drop=True)

    print(f"[股票数据] 长江电力 600900.SH")
    print(f"  原始交易日数: {len(df)}, 有效样本数: {len(X)}")
    print(f"  特征数: {len(feature_names)}")
    print(f"  特征列表: {feature_names}")
    print(f"  标签分布: {dict(y.value_counts())} (1=次日涨, 0=次日跌)")
    print(f"  时间范围: {dates.iloc[0].strftime('%Y-%m-%d')} ~ {dates.iloc[-1].strftime('%Y-%m-%d')}")

    return X, y, feature_names, dates
