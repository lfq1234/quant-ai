import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

ts.set_token('eedeac8183a4726f28d85aade5731a3182166105900e5ddfd6c8b402')
pro = ts.pro_api()

end_date = datetime.today().strftime('%Y%m%d')
start_date = (datetime.today() - timedelta(days=730)).strftime('%Y%m%d')

codes = [
    '002415.SZ', '002594.SZ', '300750.SZ', '000858.SZ', 
    '601012.SH', '600276.SH', '000333.SZ', '002230.SZ',
]
for code in codes:
    try:
        df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date').reset_index(drop=True)
        df['ch'] = df['high'].rolling(20, 20).max()
        buy = df['close'] > df['ch']
        n = buy.sum()
        print(f'{code}: {n} signals, close range {df["close"].min():.2f}-{df["close"].max():.2f}')
    except Exception as e:
        print(f'{code}: error {e}')
