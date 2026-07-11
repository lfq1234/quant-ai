import pandas as pd

df = pd.read_csv(r'C:\Users\LENOVO\Desktop\quant-ai\TASK4\data\cjdl_600900_2yr.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)

# 从第100天开始回测
for start in [50, 100, 150, 200, 250, 300]:
    df_sub = df.iloc[start:].reset_index(drop=True)
    ch = df_sub['high'].rolling(20, 20).max()
    buy = df_sub['close'] > ch
    n = buy.sum()
    print(f'start={start}: signals={n}, date={df_sub.iloc[0]["trade_date"].date()}')
    if n > 0:
        # 显示第一个信号
        idx = buy[buy].index[0]
        print(f'  first signal at idx={idx}, date={df_sub.iloc[idx]["trade_date"].date()}, close={df_sub.iloc[idx]["close"]:.2f}, ch={ch.iloc[idx]:.2f}')
