# -*- coding: utf-8 -*-
"""获取长江电力2年数据，用于更充分的海龟策略回测"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

TOKEN = 'eedeac8183a4726f28d85aade5731a3182166105900e5ddfd6c8b402'
ts.set_token(TOKEN)
pro = ts.pro_api()

end_date = datetime.today().strftime('%Y%m%d')
start_date = (datetime.today() - timedelta(days=730)).strftime('%Y%m%d')

df = pro.daily(ts_code='600900.SH', start_date=start_date, end_date=end_date)
df = df.sort_values('trade_date').reset_index(drop=True)
df['trade_date'] = pd.to_datetime(df['trade_date'])

print(f'600900 data: {df["trade_date"].min().date()} to {df["trade_date"].max().date()}, rows={len(df)}')
print(f'close min={df["close"].min():.2f}, max={df["close"].max():.2f}')

# 检查信号
df['ch'] = df['high'].rolling(20, 20).max()
buy = df['close'] > df['ch']
print(f'buy signals: {buy.sum()}')

# 保存
df.to_csv(r'C:\Users\LENOVO\Desktop\quant-ai\TASK4\data\cjdl_600900_2yr.csv', index=False, encoding='utf-8-sig')
print('saved: cjdl_600900_2yr.csv')
