import pandas as pd

df = pd.read_csv(r'C:\Users\LENOVO\Desktop\quant-ai\TASK4\data\cjdl_600900_2yr.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)

for w in [5, 10, 15]:
    ch = df['high'].rolling(w, w).max()
    buy = df['close'] > ch
    print(f'w={w}: signals={buy.sum()}')

df25 = df[df['trade_date'] >= '2025-01-01'].reset_index(drop=True)
ch25 = df25['high'].rolling(20, 20).max()
buy25 = df25['close'] > ch25
print(f'2025+ 20d signals: {buy25.sum()}')
print(f'2025+ close range: {df25["close"].min():.2f} - {df25["close"].max():.2f}')
print(f'2025+ high range: {df25["high"].min():.2f} - {df25["high"].max():.2f}')
