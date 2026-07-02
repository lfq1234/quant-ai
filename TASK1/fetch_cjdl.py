# -*- coding: utf-8 -*-
"""
TASK1 - 任务三：Tushare 获取长江电力过去一年每日交易数据
- 获取 600900.SH 长江电力 过去一年的日线行情
- 绘制每日收盘价曲线图
- 保存为 CSV 文件
"""

import os
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ==================== 配置 ====================
TOKEN = 'eedeac8183a4726f28d85aade5731a3182166105900e5ddfd6c8b402'  # Tushare Pro token
TS_CODE = '600900.SH'  # 长江电力
STOCK_NAME = '长江电力'
OUTPUT_DIR = r'C:\Users\LENOVO\Desktop\lfq1234\TASK1'

# ==================== 1. 获取数据 ====================
ts.set_token(TOKEN)
pro = ts.pro_api()

end_date = datetime.today().strftime('%Y%m%d')
start_date = (datetime.today() - timedelta(days=365)).strftime('%Y%m%d')

print(f'正在获取 {STOCK_NAME} ({TS_CODE}) 从 {start_date} 到 {end_date} 的日线数据...')
df = pro.daily(ts_code=TS_CODE, start_date=start_date, end_date=end_date)
print(f'获取到 {len(df)} 条记录')

# 按日期升序排序
df = df.sort_values('trade_date').reset_index(drop=True)
df['trade_date'] = pd.to_datetime(df['trade_date'])

# ==================== 2. 绘制收盘价曲线图 ====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df['trade_date'], df['close'], color='#C0392B', linewidth=1.5, label='每日收盘价')
ax.fill_between(df['trade_date'], df['close'], alpha=0.15, color='#C0392B')

# 添加标题与标签
ax.set_title(f'{STOCK_NAME}（{TS_CODE}）近一年每日收盘价曲线', fontsize=14, fontweight='bold')
ax.set_xlabel('交易日期', fontsize=11)
ax.set_ylabel('收盘价（元）', fontsize=11)
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
fig.autofmt_xdate()

# 在图上标注关键统计信息
stats_text = (
    f"统计区间：{df['trade_date'].min().strftime('%Y-%m-%d')} 至 {df['trade_date'].max().strftime('%Y-%m-%d')}\n"
    f"交易日数：{len(df)} 天\n"
    f"期初收盘价：{df['close'].iloc[0]:.2f} 元\n"
    f"期末收盘价：{df['close'].iloc[-1]:.2f} 元\n"
    f"区间最高价：{df['high'].max():.2f} 元\n"
    f"区间最低价：{df['low'].min():.2f} 元\n"
    f"区间涨跌幅：{(df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100:.2f}%"
)
ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
        fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.8))

fig.tight_layout()
chart_path = os.path.join(OUTPUT_DIR, 'cjdl_close_price.png')
fig.savefig(chart_path, dpi=150)
print(f'图表已保存至: {chart_path}')

# ==================== 3. 保存为 CSV ====================
csv_path = os.path.join(OUTPUT_DIR, 'cjdl_600900_2025-2026.csv')
df.to_csv(csv_path, index=False, encoding='utf-8-sig')  # utf-8-sig 让 Excel 直接打开不乱码
print(f'CSV 已保存至: {csv_path}')

# 打印前几行和最后几行
print('\n数据预览（前 5 行）：')
print(df.head().to_string(index=False))
print('\n数据预览（后 5 行）：')
print(df.tail().to_string(index=False))

# 简短描述
print('\n' + '=' * 60)
print(f'任务三完成！')
print(f'  - 数据条数：{len(df)} 条')
print(f'  - CSV 路径：{csv_path}')
print(f'  - 图表路径：{chart_path}')
print('=' * 60)
