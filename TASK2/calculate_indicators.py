# -*- coding: utf-8 -*-
"""
TASK2 - 任务三 & 任务四：技术指标计算与可视化
1. 加载 TASK1 的股价数据
2. 计算 RSI、MACD、布林带(Bollinger Bands)
3. 计算 KDJ（任务四扩展指标）
4. 绘制可视化图表
5. 生成 HTML 报告
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

# ==================== 配置 ====================
TASK1_CSV = r'C:\Users\LENOVO\Desktop\quant-ai\TASK1\cjdl_600900_2025-2026.csv'
OUTPUT_DIR = r'C:\Users\LENOVO\Desktop\quant-ai\TASK2'

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 中国股市配色：涨红跌绿
UP_COLOR = '#E74C3C'   # 红色
DOWN_COLOR = '#27AE60'  # 绿色

# ==================== 1. 加载数据 ====================
print('=' * 60)
print('TASK2 - 任务三：技术指标计算与可视化')
print('=' * 60)

df = pd.read_csv(TASK1_CSV, encoding='utf-8-sig')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)
print(f'加载 {len(df)} 条数据，时间范围 {df["trade_date"].min().date()} 至 {df["trade_date"].max().date()}')


# ==================== 2. 计算 RSI（相对强弱指数）====================
def calc_rsi(close, period=14):
    """计算 RSI 指标
    RSI = 100 - 100/(1+RS)
    RS = N日内平均涨幅 / N日内平均跌幅
    """
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # 使用指数移动平均平滑（Wilder's smoothing）
    avg_gain = avg_gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = avg_loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calc_rsi(df['close'], 14)
print(f'RSI 计算完成，最新值：{df["RSI"].iloc[-1]:.2f}')


# ==================== 3. 计算 MACD ====================
def calc_macd(close, fast=12, slow=26, signal=9):
    """计算 MACD 指标
    DIF = EMA(12) - EMA(26)
    DEA = EMA(DIF, 9)
    MACD柱 = (DIF - DEA) * 2
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd_hist = (dif - dea) * 2
    return dif, dea, macd_hist

df['DIF'], df['DEA'], df['MACD_HIST'] = calc_macd(df['close'])
print(f'MACD 计算完成，最新 DIF：{df["DIF"].iloc[-1]:.4f}，DEA：{df["DEA"].iloc[-1]:.4f}')


# ==================== 4. 计算布林带(Bollinger Bands) ====================
def calc_bollinger(close, period=20, num_std=2):
    """计算布林带
    中轨 = SMA(20)
    上轨 = 中轨 + 2 * std(20)
    下轨 = 中轨 - 2 * std(20)
    """
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower

df['BOLL_UPPER'], df['BOLL_MID'], df['BOLL_LOWER'] = calc_bollinger(df['close'])
print(f'布林带计算完成，最新上轨：{df["BOLL_UPPER"].iloc[-1]:.2f}，下轨：{df["BOLL_LOWER"].iloc[-1]:.2f}')


# ==================== 5. 计算 KDJ（任务四扩展指标）====================
def calc_kdj(high, low, close, n=9, m1=3, m2=3):
    """计算 KDJ 指标
    RSV = (Close - Low_n) / (High_n - Low_n) * 100
    K = 2/3 * prev_K + 1/3 * RSV
    D = 2/3 * prev_D + 1/3 * K
    J = 3*K - 2*D
    """
    low_n = low.rolling(window=n).min()
    high_n = high.rolling(window=n).max()
    rsv = (close - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)

    k = pd.Series(np.nan, index=close.index)
    d = pd.Series(np.nan, index=close.index)

    k.iloc[0] = 50
    d.iloc[0] = 50
    for i in range(1, len(close)):
        k.iloc[i] = (2/3) * k.iloc[i-1] + (1/3) * rsv.iloc[i]
        d.iloc[i] = (2/3) * d.iloc[i-1] + (1/3) * k.iloc[i]

    j = 3 * k - 2 * d
    return k, d, j

df['K'], df['D'], df['J'] = calc_kdj(df['high'], df['low'], df['close'])
print(f'KDJ 计算完成，最新 K：{df["K"].iloc[-1]:.2f}，D：{df["D"].iloc[-1]:.2f}，J：{df["J"].iloc[-1]:.2f}')


# ==================== 6. 绘制可视化图表 ====================
dates = df['trade_date']

# ---------- 图5：RSI 可视化 ----------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [2, 1]})

ax1.plot(dates, df['close'], color='#2C3E50', linewidth=1.2, label='收盘价')
ax1.set_title('长江电力（600900.SH）收盘价走势', fontsize=13, fontweight='bold')
ax1.set_ylabel('收盘价（元）', fontsize=11)
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

ax2.plot(dates, df['RSI'], color='#8E44AD', linewidth=1.5, label='RSI(14)')
ax2.axhline(y=70, color=DOWN_COLOR, linestyle='--', linewidth=1, alpha=0.7, label='超买线(70)')
ax2.axhline(y=30, color=UP_COLOR, linestyle='--', linewidth=1, alpha=0.7, label='超卖线(30)')
ax2.axhline(y=50, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
ax2.fill_between(dates, 70, 100, alpha=0.08, color=DOWN_COLOR)
ax2.fill_between(dates, 0, 30, alpha=0.08, color=UP_COLOR)
ax2.set_title('图5  RSI 相对强弱指数', fontsize=13, fontweight='bold')
ax2.set_ylabel('RSI', fontsize=11)
ax2.set_xlabel('交易日期', fontsize=11)
ax2.set_ylim(0, 100)
ax2.legend(loc='best', fontsize=9)
ax2.grid(True, alpha=0.3)

fig.autofmt_xdate()
fig.tight_layout()
rsi_path = os.path.join(OUTPUT_DIR, 'chart_rsi.png')
fig.savefig(rsi_path, dpi=150)
plt.close(fig)
print(f'RSI 图表已保存：{rsi_path}')

# ---------- 图6：MACD 可视化 ----------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [2, 1]})

ax1.plot(dates, df['close'], color='#2C3E50', linewidth=1.2, label='收盘价')
ax1.set_title('长江电力（600900.SH）收盘价走势', fontsize=13, fontweight='bold')
ax1.set_ylabel('收盘价（元）', fontsize=11)
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

# MACD 柱状图（涨红跌绿）
colors = [UP_COLOR if v >= 0 else DOWN_COLOR for v in df['MACD_HIST']]
ax2.bar(dates, df['MACD_HIST'], color=colors, alpha=0.6, width=1.0, label='MACD柱')
ax2.plot(dates, df['DIF'], color='#E67E22', linewidth=1.2, label='DIF')
ax2.plot(dates, df['DEA'], color='#3498DB', linewidth=1.2, label='DEA')
ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.8)
ax2.set_title('图6  MACD 指标', fontsize=13, fontweight='bold')
ax2.set_ylabel('MACD', fontsize=11)
ax2.set_xlabel('交易日期', fontsize=11)
ax2.legend(loc='best', fontsize=9)
ax2.grid(True, alpha=0.3)

fig.autofmt_xdate()
fig.tight_layout()
macd_path = os.path.join(OUTPUT_DIR, 'chart_macd.png')
fig.savefig(macd_path, dpi=150)
plt.close(fig)
print(f'MACD 图表已保存：{macd_path}')

# ---------- 图7：布林带可视化 ----------
fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(dates, df['close'], color='#2C3E50', linewidth=1.2, label='收盘价', zorder=3)
ax.plot(dates, df['BOLL_UPPER'], color=UP_COLOR, linewidth=1, label='上轨(2σ)', alpha=0.8)
ax.plot(dates, df['BOLL_MID'], color='#F39C12', linewidth=1, label='中轨(SMA20)', alpha=0.8, linestyle='--')
ax.plot(dates, df['BOLL_LOWER'], color=DOWN_COLOR, linewidth=1, label='下轨(2σ)', alpha=0.8)
ax.fill_between(dates, df['BOLL_UPPER'], df['BOLL_LOWER'], alpha=0.1, color='#3498DB', label='布林带区域')

ax.set_title('图7  布林带(Bollinger Bands)指标', fontsize=13, fontweight='bold')
ax.set_ylabel('价格（元）', fontsize=11)
ax.set_xlabel('交易日期', fontsize=11)
ax.legend(loc='best', fontsize=9)
ax.grid(True, alpha=0.3)
fig.autofmt_xdate()
fig.tight_layout()
boll_path = os.path.join(OUTPUT_DIR, 'chart_boll.png')
fig.savefig(boll_path, dpi=150)
plt.close(fig)
print(f'布林带图表已保存：{boll_path}')

# ---------- 图8：KDJ 可视化（任务四）----------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [2, 1]})

ax1.plot(dates, df['close'], color='#2C3E50', linewidth=1.2, label='收盘价')
ax1.set_title('长江电力（600900.SH）收盘价走势', fontsize=13, fontweight='bold')
ax1.set_ylabel('收盘价（元）', fontsize=11)
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

ax2.plot(dates, df['K'], color='#E67E22', linewidth=1.2, label='K线')
ax2.plot(dates, df['D'], color='#3498DB', linewidth=1.2, label='D线')
ax2.plot(dates, df['J'], color='#E74C3C', linewidth=1.0, label='J线', alpha=0.8)
ax2.axhline(y=80, color=UP_COLOR, linestyle='--', linewidth=0.8, alpha=0.5, label='超买线(80)')
ax2.axhline(y=20, color=DOWN_COLOR, linestyle='--', linewidth=0.8, alpha=0.5, label='超卖线(20)')
ax2.axhline(y=50, color='gray', linestyle=':', linewidth=0.6, alpha=0.4)
ax2.set_title('图8  KDJ 随机指标（任务四扩展指标）', fontsize=13, fontweight='bold')
ax2.set_ylabel('KDJ', fontsize=11)
ax2.set_xlabel('交易日期', fontsize=11)
ax2.legend(loc='best', fontsize=9)
ax2.grid(True, alpha=0.3)

fig.autofmt_xdate()
fig.tight_layout()
kdj_path = os.path.join(OUTPUT_DIR, 'chart_kdj.png')
fig.savefig(kdj_path, dpi=150)
plt.close(fig)
print(f'KDJ 图表已保存：{kdj_path}')

# ==================== 7. 保存含指标的数据 ====================
output_csv = os.path.join(OUTPUT_DIR, 'data_with_indicators.csv')
df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f'含指标数据已保存：{output_csv}')


# ==================== 8. 生成 HTML 报告 ====================
def fig_to_base64(path):
    import base64
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

figs = {
    'diagnosis': os.path.join(OUTPUT_DIR, 'data_diagnosis.png'),
    'rsi': rsi_path,
    'macd': macd_path,
    'boll': boll_path,
    'kdj': kdj_path,
}

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TASK2 - 数据炼金术：数据诊断与构造交易指标</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Microsoft YaHei", "SimHei", sans-serif; background: #f5f5f5; color: #333; line-height: 1.8; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ text-align: center; font-size: 24px; margin: 30px 0 10px; color: #2c3e50; }}
        h2 {{ font-size: 20px; margin: 25px 0 15px; color: #34495e; border-left: 4px solid #3498db; padding-left: 12px; }}
        h3 {{ font-size: 16px; margin: 20px 0 10px; color: #555; }}
        .info-box {{ background: #fff; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .chart-box {{ background: #fff; border-radius: 8px; padding: 15px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .chart-box img {{ width: 100%; border-radius: 4px; }}
        .chart-caption {{ text-align: center; font-size: 14px; color: #666; margin-top: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: center; }}
        th {{ background: #3498db; color: #fff; font-weight: bold; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }}
        .stat-card {{ background: #fff; border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }}
        .stat-card .value {{ font-size: 22px; font-weight: bold; color: #e74c3c; }}
        .stat-card .label {{ font-size: 13px; color: #888; margin-top: 5px; }}
        .formula {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 12px 20px; margin: 10px 0; font-family: "Consolas", monospace; font-size: 14px; }}
        .interpretation {{ background: #fffde7; border-left: 4px solid #f1c40f; padding: 12px 18px; margin: 12px 0; border-radius: 0 4px 4px 0; }}
        .summary {{ background: #e8f5e9; border-left: 4px solid #27ae60; padding: 12px 18px; margin: 15px 0; border-radius: 0 4px 4px 0; }}
    </style>
</head>
<body>
<div class="container">

<h1>数据炼金术：数据诊断与构造交易指标</h1>
<p style="text-align:center; color:#888; margin-bottom:30px;">长江电力（600900.SH） | 2025-07-02 至 2026-07-02 | 共 243 个交易日</p>

<!-- 任务一 -->
<h2>任务一：数据诊断分析</h2>

<div class="info-box">
    <h3>缺失值检查结果</h3>
    <div class="summary">
        <p>对全部 11 个字段进行缺失值检测，结果：<strong>所有字段缺失值数量均为 0</strong>，数据完整性良好，无需进行缺失值填补处理。</p>
    </div>
    <table>
        <tr><th>字段</th><th>缺失数量</th><th>缺失比例(%)</th></tr>
        <tr><td>ts_code</td><td>0</td><td>0.0</td></tr>
        <tr><td>trade_date</td><td>0</td><td>0.0</td></tr>
        <tr><td>open</td><td>0</td><td>0.0</td></tr>
        <tr><td>high</td><td>0</td><td>0.0</td></tr>
        <tr><td>low</td><td>0</td><td>0.0</td></tr>
        <tr><td>close</td><td>0</td><td>0.0</td></tr>
        <tr><td>pre_close</td><td>0</td><td>0.0</td></tr>
        <tr><td>change</td><td>0</td><td>0.0</td></tr>
        <tr><td>pct_chg</td><td>0</td><td>0.0</td></tr>
        <tr><td>vol</td><td>0</td><td>0.0</td></tr>
        <tr><td>amount</td><td>0</td><td>0.0</td></tr>
    </table>
</div>

<div class="info-box">
    <h3>描述性统计量（核心字段）</h3>
    <div class="stat-grid">
        <div class="stat-card"><div class="value">{df["close"].mean():.2f}</div><div class="label">收盘价均值</div></div>
        <div class="stat-card"><div class="value">{df["close"].std():.2f}</div><div class="label">收盘价标准差</div></div>
        <div class="stat-card"><div class="value">{df["close"].min():.2f} ~ {df["close"].max():.2f}</div><div class="label">收盘价范围</div></div>
        <div class="stat-card"><div class="value">{df["pct_chg"].mean():.4f}%</div><div class="label">日涨跌幅均值</div></div>
        <div class="stat-card"><div class="value">{df["pct_chg"].std():.4f}%</div><div class="label">日涨跌幅标准差</div></div>
        <div class="stat-card"><div class="value">{df["pct_chg"].skew():.4f}</div><div class="label">日涨跌幅偏度</div></div>
    </div>
</div>

<div class="chart-box">
    <img src="data:image/png;base64,{fig_to_base64(figs['diagnosis'])}" alt="数据诊断">
    <div class="chart-caption">图1-4 数据诊断可视化（缺失值检查、收盘价箱线图、日涨跌幅分布、成交量分布）</div>
</div>

<div class="interpretation">
    <p><strong>诊断解读：</strong>收盘价箱线图显示价格主要集中在 26.9~28.1 元区间，存在少数高价异常点；日涨跌幅分布近似正态但略有右偏（偏度0.049），峰度为1.30，略低于正态分布的3，说明分布比正态分布更平坦；成交量分布右偏明显（偏度1.69），存在放量交易日。</p>
</div>

<!-- 任务二：指标说明 -->
<h2>任务二：技术指标说明</h2>

<div class="info-box">
    <h3>2.1 RSI（相对强弱指数）</h3>
    <p><strong>计算方法：</strong></p>
    <div class="formula">
        RS = N日内平均涨幅 / N日内平均跌幅<br>
        RSI = 100 - 100 / (1 + RS)<br>
        （通常取 N = 14）
    </div>
    <p><strong>作用：</strong>RSI 是一种动量振荡指标，取值范围 0~100。通常以 70 为超买线、30 为超卖线。当 RSI 超过 70 时，表明股票可能被超买，存在回调风险；当 RSI 低于 30 时，表明股票可能被超卖，存在反弹机会。RSI 还可用于识别背离信号，即价格创新高/新低而 RSI 未同步创新高/新低，预示趋势可能反转。</p>
</div>

<div class="info-box">
    <h3>2.2 MACD（指数平滑异同移动平均线）</h3>
    <p><strong>计算方法：</strong></p>
    <div class="formula">
        DIF（快线）= EMA(close, 12) - EMA(close, 26)<br>
        DEA（慢线）= EMA(DIF, 9)<br>
        MACD柱 = (DIF - DEA) × 2
    </div>
    <p><strong>作用：</strong>MACD 是趋势跟踪动量指标，通过快慢均线之差捕捉趋势变化。DIF 上穿 DEA 形成"金叉"，为买入信号；DIF 下穿 DEA 形成"死叉"，为卖出信号。MACD 柱状图反映多空力量强弱变化，柱体由负转正预示多头力量增强。MACD 还可用于识别顶背离和底背离。</p>
</div>

<div class="info-box">
    <h3>2.3 布林带（Bollinger Bands）</h3>
    <p><strong>计算方法：</strong></p>
    <div class="formula">
        中轨 = SMA(close, 20)<br>
        上轨 = 中轨 + 2 × σ（20日标准差）<br>
        下轨 = 中轨 - 2 × σ
    </div>
    <p><strong>作用：</strong>布林带由 John Bollinger 提出，通过标准差衡量价格波动率。价格触及上轨可能超买，触及下轨可能超卖。布林带收窄表示波动率降低，可能酝酿趋势突破；布林带开口扩大表示趋势加速。价格在中轨上方运行视为多头趋势，在中轨下方运行为空头趋势。</p>
</div>

<!-- 任务三：指标可视化 -->
<h2>任务三：技术指标计算与可视化</h2>

<div class="chart-box">
    <img src="data:image/png;base64,{fig_to_base64(figs['rsi'])}" alt="RSI">
    <div class="chart-caption">图5  RSI(14) 相对强弱指数可视化</div>
</div>
<div class="interpretation">
    <p><strong>RSI 解读：</strong>在观察期内，RSI 多次触及 70 以上的超买区域和 30 附近的超卖区域。最新 RSI 值为 {df["RSI"].iloc[-1]:.2f}，处于{"超买" if df["RSI"].iloc[-1] > 70 else "超卖" if df["RSI"].iloc[-1] < 30 else "中性"}区间。可以看到 RSI 与收盘价之间存在一定的背离现象，对趋势反转有一定的预示作用。</p>
</div>

<div class="chart-box">
    <img src="data:image/png;base64,{fig_to_base64(figs['macd'])}" alt="MACD">
    <div class="chart-caption">图6  MACD 指标可视化</div>
</div>
<div class="interpretation">
    <p><strong>MACD 解读：</strong>DIF 与 DEA 在观察期内多次交叉，每次金叉（DIF上穿DEA）后股价通常出现一波上涨，死叉（DIF下穿DEA）后股价往往回调。MACD 柱状图（红色为正、绿色为负）直观反映了多空力量的此消彼长。最新 DIF={df["DIF"].iloc[-1]:.4f}，DEA={df["DEA"].iloc[-1]:.4f}，柱状值为{"正" if df["MACD_HIST"].iloc[-1] >= 0 else "负"}，多头{"占优" if df["MACD_HIST"].iloc[-1] >= 0 else "偏弱"}。</p>
</div>

<div class="chart-box">
    <img src="data:image/png;base64,{fig_to_base64(figs['boll'])}" alt="布林带">
    <div class="chart-caption">图7  布林带(Bollinger Bands)指标可视化</div>
</div>
<div class="interpretation">
    <p><strong>布林带解读：</strong>收盘价大部分时间在布林带上下轨之间运行。当价格触及上轨时短期有回调压力，触及下轨时有支撑反弹。布林带宽度（上轨减下轨）的变化反映了波动率的动态：收窄时市场相对平静，可能酝酿方向选择；开口扩大时趋势加速。最新收盘价 {df["close"].iloc[-1]:.2f} 元，上轨 {df["BOLL_UPPER"].iloc[-1]:.2f} 元，下轨 {df["BOLL_LOWER"].iloc[-1]:.2f} 元，中轨 {df["BOLL_MID"].iloc[-1]:.2f} 元。</p>
</div>

<!-- 任务四：KDJ -->
<h2>任务四：扩展指标——KDJ 随机指标</h2>

<div class="info-box">
    <h3>KDJ 指标介绍</h3>
    <p>KDJ 指标由 George C. Lane 创立，是技术分析中最常用的短线超买超卖指标之一。它通过计算一定周期内最高价、最低价与收盘价之间的关系，反映当前价格在近期价格区间中的相对位置，从而判断市场的超买超卖状态和短期转折信号。</p>
    <p><strong>计算方法：</strong></p>
    <div class="formula">
        RSV = (Close - Low_n) / (High_n - Low_n) × 100 &nbsp;&nbsp;(n=9)<br>
        K = 2/3 × 前日K + 1/3 × RSV<br>
        D = 2/3 × 前日D + 1/3 × K<br>
        J = 3 × K - 2 × D
    </div>
    <p><strong>作用：</strong>KDJ 取值范围理论上为 0~100（J线可超出）。通常以 80 为超买线、20 为超卖线。K 线上穿 D 线为"金叉"买入信号，K 线下穿 D 线为"死叉"卖出信号。J 线反应最灵敏，当 J 值超过 100 或低于 0 时，说明市场处于极端状态，反转概率增大。KDJ 适合短线交易，在震荡市中效果较好，在强趋势市中可能出现钝化。</p>
</div>

<div class="chart-box">
    <img src="data:image/png;base64,{fig_to_base64(figs['kdj'])}" alt="KDJ">
    <div class="chart-caption">图8  KDJ 随机指标可视化</div>
</div>
<div class="interpretation">
    <p><strong>KDJ 解读：</strong>K 线与 D 线在观察期内多次交叉，每次金叉（K上穿D）对应股价短期反弹，死叉（K下穿D）对应短期回调。J 线波动最为剧烈，多次触及 100 以上和 0 以下的极端区域，这些位置通常是短期反转的高概率信号。最新 K={df["K"].iloc[-1]:.2f}，D={df["D"].iloc[-1]:.2f}，J={df["J"].iloc[-1]:.2f}，KDJ 处于{"超买" if df["K"].iloc[-1] > 80 else "超卖" if df["K"].iloc[-1] < 20 else "中性"}区域。</p>
</div>

<!-- 指标对比汇总 -->
<h2>技术指标最新值汇总</h2>
<div class="info-box">
    <table>
        <tr><th>指标</th><th>关键参数</th><th>最新值</th><th>信号</th></tr>
        <tr><td>RSI(14)</td><td>超买>70, 超卖<30</td><td>{df["RSI"].iloc[-1]:.2f}</td><td>{"超买" if df["RSI"].iloc[-1] > 70 else "超卖" if df["RSI"].iloc[-1] < 30 else "中性"}</td></tr>
        <tr><td>DIF</td><td>MACD快线</td><td>{df["DIF"].iloc[-1]:.4f}</td><td>{"多头" if df["DIF"].iloc[-1] > 0 else "空头"}</td></tr>
        <tr><td>DEA</td><td>MACD慢线</td><td>{df["DEA"].iloc[-1]:.4f}</td><td>{"多头" if df["DEA"].iloc[-1] > 0 else "空头"}</td></tr>
        <tr><td>MACD柱</td><td>(DIF-DEA)×2</td><td>{df["MACD_HIST"].iloc[-1]:.4f}</td><td>{"红柱(多)" if df["MACD_HIST"].iloc[-1] >= 0 else "绿柱(空)"}</td></tr>
        <tr><td>布林带上轨</td><td>SMA20+2σ</td><td>{df["BOLL_UPPER"].iloc[-1]:.2f}</td><td>-</td></tr>
        <tr><td>布林带中轨</td><td>SMA20</td><td>{df["BOLL_MID"].iloc[-1]:.2f}</td><td>-</td></tr>
        <tr><td>布林带下轨</td><td>SMA20-2σ</td><td>{df["BOLL_LOWER"].iloc[-1]:.2f}</td><td>-</td></tr>
        <tr><td>K</td><td>KDJ K线</td><td>{df["K"].iloc[-1]:.2f}</td><td>{"超买" if df["K"].iloc[-1] > 80 else "超卖" if df["K"].iloc[-1] < 20 else "中性"}</td></tr>
        <tr><td>D</td><td>KDJ D线</td><td>{df["D"].iloc[-1]:.2f}</td><td>-</td></tr>
        <tr><td>J</td><td>3K-2D</td><td>{df["J"].iloc[-1]:.2f}</td><td>{"极端超买" if df["J"].iloc[-1] > 100 else "极端超卖" if df["J"].iloc[-1] < 0 else "正常"}</td></tr>
    </table>
</div>

<div class="summary">
    <p><strong>总结：</strong>通过对长江电力日线数据的技术指标分析，可以看出不同指标从不同维度刻画了市场状态。RSI 反映价格动量强弱，MACD 捕捉趋势转折，布林带衡量波动率边界，KDJ 识别短期超买超卖。在实际交易中，建议多指标组合使用，相互验证以提高信号可靠性。</p>
</div>

<p style="text-align:center; color:#888; margin:30px 0;">数据来源：Tushare Pro | 分析工具：Python (pandas, matplotlib) | 姓名：林富强</p>

</div>
</body>
</html>'''

html_path = os.path.join(OUTPUT_DIR, 'report.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nHTML 报告已保存：{html_path}')

print('\n' + '=' * 60)
print('任务三 & 任务四 完成！')
print(f'  - RSI 图表：{rsi_path}')
print(f'  - MACD 图表：{macd_path}')
print(f'  - 布林带图表：{boll_path}')
print(f'  - KDJ 图表：{kdj_path}')
print(f'  - HTML 报告：{html_path}')
print(f'  - 含指标数据：{output_csv}')
print('=' * 60)
