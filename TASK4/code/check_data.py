import pandas as pd

df = pd.read_csv(r'C:\Users\LENOVO\Desktop\quant-ai\TASK4\data\cjdl_600900_2yr.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)
print('Total:', len(df))
print('Date:', df['trade_date'].min(), 'to', df['trade_date'].max())
print('High max:', df['high'].max())
print('Close max:', df['close'].max())

ch = df['high'].rolling(20, 20).max()
print('First valid ch:', ch.iloc[19])
print('Max ch:', ch.max())
print('Min ch:', ch.min())

buy = df['close'] > ch
print('Buy signals:', buy.sum())

print(df.head(20)[['trade_date', 'close', 'high']])
print(df.tail(20)[['trade_date', 'close', 'high']])
