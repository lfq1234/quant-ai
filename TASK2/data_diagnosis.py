# -*- coding: utf-8 -*-
"""
TASK2 - 任务一：数据诊断分析
对 TASK1 的长江电力(600900.SH)日线数据进行：
1. 缺失值检查
2. 描述性统计量计算
3. 数据质量诊断可视化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import json
import os

# ==================== 配置 ====================
TASK1_CSV = r'C:\Users\LENOVO\Desktop\quant-ai\TASK1\cjdl_600900_2025-2026.csv'
OUTPUT_DIR = r'C:\Users\LENOVO\Desktop\quant-ai\TASK2'

# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ==================== 1. 加载数据 ====================
print('=' * 60)
print('TASK2 - 任务一：数据诊断分析')
print('=' * 60)

df = pd.read_csv(TASK1_CSV, encoding='utf-8-sig')
print(f'\n数据加载成功，共 {len(df)} 条记录，{len(df.columns)} 个字段')
print(f'字段列表：{list(df.columns)}')
print(f'时间范围：{df["trade_date"].min()} 至 {df["trade_date"].max()}')

# ==================== 2. 缺失值检查 ====================
print('\n' + '-' * 40)
print('【缺失值检查】')
print('-' * 40)

missing_count = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    '缺失数量': missing_count,
    '缺失比例(%)': missing_pct
})
print(missing_df.to_string())

if missing_count.sum() == 0:
    print('\n结论：数据无缺失值，数据完整性良好。')
else:
    print(f'\n结论：共发现 {missing_count.sum()} 个缺失值，需进一步处理。')

# ==================== 3. 描述性统计量 ====================
print('\n' + '-' * 40)
print('【描述性统计量】')
print('-' * 40)

# 选取数值型字段
numeric_cols = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
desc_stats = df[numeric_cols].describe().T
desc_stats['方差'] = df[numeric_cols].var()
desc_stats['偏度'] = df[numeric_cols].skew()
desc_stats['峰度'] = df[numeric_cols].kurtosis()

# 重命名列
desc_stats = desc_stats.rename(columns={
    'count': '计数',
    'mean': '均值',
    'std': '标准差',
    'min': '最小值',
    '25%': '下四分位数',
    '50%': '中位数',
    '75%': '上四分位数',
    'max': '最大值'
})

print(desc_stats.round(4).to_string())

# 保存统计结果到 CSV
stats_csv = os.path.join(OUTPUT_DIR, 'descriptive_stats.csv')
desc_stats.round(4).to_csv(stats_csv, encoding='utf-8-sig')
print(f'\n描述性统计量已保存至：{stats_csv}')

# ==================== 4. 数据质量诊断可视化 ====================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 图1：缺失值热力图
ax1 = axes[0, 0]
missing_matrix = df.isnull().astype(int)
if missing_matrix.sum().sum() == 0:
    ax1.text(0.5, 0.5, '数据无缺失值\n完整性良好', ha='center', va='center',
             fontsize=16, transform=ax1.transAxes,
             bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgreen', alpha=0.8))
    ax1.set_title('图1  缺失值检查结果', fontsize=13, fontweight='bold')
    ax1.set_xticks([])
    ax1.set_yticks([])
else:
    ax1.imshow(missing_matrix.T, cmap='Reds', aspect='auto')
    ax1.set_title('图1  缺失值热力图', fontsize=13, fontweight='bold')
    ax1.set_yticks(range(len(df.columns)))
    ax1.set_yticklabels(df.columns)

# 图2：收盘价箱线图
ax2 = axes[0, 1]
box = ax2.boxplot(df['close'], vert=True, patch_artist=True,
                   boxprops=dict(facecolor='#3498DB', alpha=0.6),
                   medianprops=dict(color='#E74C3C', linewidth=2),
                   whiskerprops=dict(color='#2C3E50'),
                   capprops=dict(color='#2C3E50'))
ax2.set_title('图2  收盘价分布箱线图', fontsize=13, fontweight='bold')
ax2.set_ylabel('收盘价（元）', fontsize=11)
ax2.grid(True, alpha=0.3)

# 标注统计信息
stats_text_close = (
    f"均值：{df['close'].mean():.2f}\n"
    f"中位数：{df['close'].median():.2f}\n"
    f"标准差：{df['close'].std():.2f}\n"
    f"偏度：{df['close'].skew():.4f}\n"
    f"峰度：{df['close'].kurtosis():.4f}"
)
ax2.text(1.25, df['close'].median(), stats_text_close, fontsize=9,
         verticalalignment='center',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.8))

# 图3：日涨跌幅分布直方图
ax3 = axes[1, 0]
n, bins, patches = ax3.hist(df['pct_chg'], bins=40, color='#E67E22', alpha=0.7, edgecolor='white')
ax3.axvline(x=0, color='red', linestyle='--', linewidth=1.2, label='零线')
ax3.axvline(x=df['pct_chg'].mean(), color='blue', linestyle='-', linewidth=1.2,
            label=f'均值:{df["pct_chg"].mean():.4f}%')
ax3.set_title('图3  日涨跌幅分布直方图', fontsize=13, fontweight='bold')
ax3.set_xlabel('日涨跌幅（%）', fontsize=11)
ax3.set_ylabel('频数', fontsize=11)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# 图4：成交量分布
ax4 = axes[1, 1]
ax4.hist(df['vol'], bins=40, color='#9B59B6', alpha=0.7, edgecolor='white')
ax4.axvline(x=df['vol'].mean(), color='red', linestyle='-', linewidth=1.2,
            label=f'均值:{df["vol"].mean():.0f}')
ax4.axvline(x=df['vol'].median(), color='blue', linestyle='--', linewidth=1.2,
            label=f'中位数:{df["vol"].median():.0f}')
ax4.set_title('图4  成交量分布直方图', fontsize=13, fontweight='bold')
ax4.set_xlabel('成交量（手）', fontsize=11)
ax4.set_ylabel('频数', fontsize=11)
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

fig.suptitle('长江电力（600900.SH）数据诊断分析', fontsize=15, fontweight='bold', y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.96])
chart_path = os.path.join(OUTPUT_DIR, 'data_diagnosis.png')
fig.savefig(chart_path, dpi=150)
plt.close(fig)
print(f'\n数据诊断图表已保存至：{chart_path}')

# ==================== 5. 输出诊断摘要 ====================
summary = {
    '数据条数': len(df),
    '字段数量': len(df.columns),
    '时间范围': f'{df["trade_date"].min()} 至 {df["trade_date"].max()}',
    '缺失值总数': int(missing_count.sum()),
    '收盘价_均值': round(df['close'].mean(), 2),
    '收盘价_标准差': round(df['close'].std(), 2),
    '收盘价_最小值': round(df['close'].min(), 2),
    '收盘价_最大值': round(df['close'].max(), 2),
    '日涨跌幅_均值': round(df['pct_chg'].mean(), 4),
    '日涨跌幅_标准差': round(df['pct_chg'].std(), 4),
    '日涨跌幅_偏度': round(df['pct_chg'].skew(), 4),
    '日涨跌幅_峰度': round(df['pct_chg'].kurtosis(), 4),
}

print('\n' + '=' * 60)
print('数据诊断摘要：')
for k, v in summary.items():
    print(f'  {k}：{v}')
print('=' * 60)

# 保存摘要为 JSON（供后续生成文档使用）
summary_path = os.path.join(OUTPUT_DIR, 'diagnosis_summary.json')
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f'诊断摘要已保存至：{summary_path}')
