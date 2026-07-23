# -*- coding: utf-8 -*-
"""
============================================================================
TASK7 · JoinQuant 多因子截面选股策略（粘贴即用）
作者：林富强 / 北京大学
----------------------------------------------------------------------------
策略逻辑（承接 TASK6）：
    在每个调仓日，对股票池计算多类因子（动量 / 反转 / 量价 / 波动率 / 估值），
    在截面维度做 1%/99% 缩尾 + z-score 标准化，按设定权重合成综合得分，
    选取得分最高的 Top-N 只股票等权持有，到下一调仓日再平衡。

使用方式：
    1. 登录 https://www.joinquant.com ，进入「我的策略」→ 新建策略
    2. 把本文件全部内容粘贴进去（替换默认模板）
    3. 设置回测区间：建议 2014-01-01 ~ 2025-12-31（保证 252 日动量有数据）
       初始资金 1,000,000；调仓频率见 g.rebalance_month；撮合：真实价格
    4. 点「运行回测」→ 看收益/回撤 → 调 g 中参数 → 再跑（参数调优）
    5. 满意后点「开启实盘模拟」→ 观察实盘模拟表现（实盘模拟）
    6. 在结果页导出净值曲线 / 回撤曲线 / 收益分布截图，连同指标填入报告

所有可调参数都集中在 initialize() 调用的 init_parameters() 中，
平台上调优只需改这几个数字，无需动策略主体。
============================================================================
"""

# JoinQuant 基本面数据接口（估值/市值等）。平台环境自带，本行不能删。
from jqdata import *

import numpy as np
import pandas as pd


# ============================================================================
# 1. 可调参数（在平台上改这里即可完成「参数调优」）
# ============================================================================
def init_parameters(context):
    # ---- 基础参数 ----
    g.stock_num      = 30        # 持仓数量 Top-N（选得分最高的 N 只）
    g.rebalance_month = 3        # 调仓频率（月）：1=月度, 3=季度
    g.lookback       = 260       # 因子计算所需历史长度（须 >= 252，支撑 12 月动量窗口）
    g.universe       = 'hs300'   # 股票池：'hs300'=沪深300 / 'zz500'=中证500 / 'all'=全市场
    g.benchmark      = '000300.XSHG'

    # ---- 风控参数 ----
    g.max_position   = 1.0 / g.stock_num   # 单只股票最大仓位（等权）
    g.min_mktcap     = 20        # 剔除总市值低于该值（亿元）的小微盘，降低流动性风险
    g.drop_st        = True      # 剔除 ST / *ST
    g.drop_suspended = True      # 剔除停牌股
    g.drop_new       = 60        # 上市不足该交易日数的新股不参与（避免次新波动）

    # ---- 因子权重（正=看多该因子，负=反向）----
    # 因子含义见下方 compute_factors 注释，与 TASK6 的 12 因子体系一致
    g.factor_weights = {
        'mom_1m':        1.0,    # 1 个月动量（强者恒强）
        'mom_3m':        1.0,    # 3 个月动量
        'mom_12m_1m':    1.0,    # 12 月-1 月动量（剔除短期反转污染）
        'reversal_5d':   1.0,    # 5 日反转（短期均值回复，取正表示做反转）
        'turn_20d':      1.0,    # 20 日均量（流动性溢价）
        'vol_ratio':     1.0,    # 5/20 日量比（放量信号）
        'vol_20d':      -1.0,    # 20 日波动率（高波动折价）
        'vol_5d':       -1.0,    # 5 日波动率
        'rsi_14':        1.0,    # RSI（相对强弱）
        'ma_bias_20':    1.0,    # 20 日均线乖离率（趋势强度）
        'bb_pos':        1.0,    # 布林带位置
        'pe_ttm':       -1.0,    # 市盈率（低估值溢价，反向）
        'ln_market_cap': -1.0,   # 市值（小市值溢价，反向）
    }


# ============================================================================
# 2. 初始化
# ============================================================================
def initialize(context):
    init_parameters(context)

    set_option('use_real_price', True)                 # 使用真实价格撮合
    set_benchmark(g.benchmark)                          # 设置基准
    set_order_cost(OrderCost(
        open_tax=0, close_tax=0.001,                    # 印花税 0.1%（卖出收）
        open_commission=0.0003, close_commission=0.0003,  # 佣金万三
        min_commission=5), type='stock')                # 最低 5 元

    # 调仓：每月 1 号收盘后执行；季度调仓在 rebalance 内再判断月份
    run_monthly(rebalance, 1, time='close')
    # 每个交易日收盘后记录组合状态，用于平台画图
    run_daily(record_vars, time='after_close')


# ============================================================================
# 3. 股票池
# ============================================================================
def get_universe(context):
    if g.universe == 'hs300':
        stocks = get_index_stocks('000300.XSHG', date=context.current_dt)
    elif g.universe == 'zz500':
        stocks = get_index_stocks('000905.XSHG', date=context.current_dt)
    else:
        stocks = list(get_all_securities(['stock'], date=context.current_dt).index)

    # 剔除上市不足 g.drop_new 天的次新股
    valid = []
    for s in stocks:
        try:
            start = get_security_info(s).start_date
            if start is not None and (context.current_dt.date() - start).days >= g.drop_new:
                valid.append(s)
        except Exception:
            continue
    return valid


# ============================================================================
# 4. 因子计算（承接 TASK6 的 12 因子 + 估值/市值）
# ============================================================================
def compute_factors(context, stocks):
    # 行情数据（后复权）
    close = history(g.lookback, '1d', 'close',  stocks, df=True, skip_paused=True, fq='post')
    open_ = history(g.lookback, '1d', 'open',   stocks, df=True, skip_paused=True, fq='post')
    high = history(g.lookback, '1d', 'high',   stocks, df=True, skip_paused=True, fq='post')
    low  = history(g.lookback, '1d', 'low',    stocks, df=True, skip_paused=True, fq='post')
    vol  = history(g.lookback, '1d', 'volume', stocks, df=True, skip_paused=True, fq='post')

    ret = close.pct_change()                 # 日收益率
    ma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()

    f = pd.DataFrame(index=close.columns)    # 行=股票，列=因子

    # —— 动量类（用 shift 取值：数据不足时自动为 NaN，最后 dropna 剔除，避免 iloc 越界）——
    f['mom_1m']       = (close / close.shift(21) - 1).iloc[-1]            # 近 1 个月动量
    f['mom_3m']       = (close / close.shift(65) - 1).iloc[-1]            # 近 3 个月动量
    f['mom_12m_1m']   = (close.shift(21) / close.shift(251) - 1).iloc[-1] # 12 月-1 月动量
    # —— 反转类 ——
    f['reversal_5d']  = -ret.rolling(5).sum().iloc[-1]                     # 5 日反转
    # —— 量价类 ——
    f['turn_20d']     = vol.rolling(20).mean().iloc[-1]                    # 20 日均量
    f['vol_ratio']    = (vol.rolling(5).mean() / (vol.rolling(20).mean() + 1e-9)).iloc[-1]  # 量比
    # —— 波动率类 ——
    f['vol_20d']      = ret.rolling(20).std().iloc[-1]                     # 20 日波动率
    f['vol_5d']       = ret.rolling(5).std().iloc[-1]                      # 5 日波动率
    # —— 技术形态类 ——
    f['rsi_14']       = rsi_series(close, 14)                             # 14 日 RSI
    f['ma_bias_20']   = (close / ma20 - 1).iloc[-1]                       # 20 日均线乖离率
    f['bb_pos']       = ((close - ma20) / (2 * std20 + 1e-9)).iloc[-1]    # 布林带位置

    # —— 估值 / 规模（基本面，来自 jqdata）——
    q = query(valuation.code, valuation.pe_ratio, valuation.market_cap) \
            .filter(valuation.code.in_(stocks))
    fd = get_fundamentals(q, date=context.current_dt)
    pe_map  = dict(zip(fd['code'], fd['pe_ratio']))
    cap_map = dict(zip(fd['code'], fd['market_cap']))   # 单位：亿元
    f['pe_ttm']       = f.index.map(pe_map)
    f['ln_market_cap'] = np.log(f.index.map(cap_map).astype(float) + 1e-9)

    # 风控过滤
    if g.drop_st:
        # 注意：get_extras 返回的索引是交易日（无时分），而 context.current_dt
        # 带 15:00:00，直接 st.loc[current_dt, c] 会 KeyError。
        # 因此用 .iloc[0] 取该行值，避免按标签定位的精度问题。
        d = context.current_dt.strftime('%Y-%m-%d')
        st = get_extras('is_st', list(f.index), start_date=d, end_date=d)
        st_codes = [c for c in f.index if bool(st[c].iloc[0])]
        f = f.drop(st_codes)
    f = f[f['pe_ttm'] > 0]                       # 剔除亏损/异常 PE
    f = f[f['ln_market_cap'] > np.log(g.min_mktcap)]
    return f.dropna()


def rsi_series(close, n=14):
    """返回每只股票最新的 14 日 RSI"""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(n).mean()
    avg_loss = loss.rolling(n).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return (100 - 100 / (1 + rs)).iloc[-1]


# ============================================================================
# 5. 截面标准化 + 合成得分
# ============================================================================
def winsorize_zscore(s):
    """1%/99% 缩尾 + 截面 z-score 标准化"""
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    s = s.clip(lower=lo, upper=hi)
    return (s - s.mean()) / (s.std() + 1e-9)


def score_factors(factors):
    score = pd.Series(0.0, index=factors.index)
    for name, w in g.factor_weights.items():
        if name in factors.columns:
            score += w * winsorize_zscore(factors[name])
    return score


# ============================================================================
# 6. 调仓
# ============================================================================
def rebalance(context):
    # 季度调仓：仅当月份为 3 的倍数时执行
    if g.rebalance_month == 3 and context.current_dt.month % 3 != 0:
        return

    stocks = get_universe(context)
    if len(stocks) < g.stock_num:
        log.warn('股票池过小，跳过本次调仓')
        return

    factors = compute_factors(context, stocks)
    if factors.empty:
        return

    score = score_factors(factors)
    selected = score.sort_values(ascending=False).head(g.stock_num).index.tolist()

    # 卖出不在选中列表的持仓
    for s in context.portfolio.positions:
        if s not in selected:
            order_target_value(s, 0)

    # 等权买入选中股票
    target_value = context.portfolio.total_value / g.stock_num
    for s in selected:
        order_target_value(s, target_value)

    log.info('调仓完成，持有 %d 只，组合市值 %.0f'
             % (len(selected), context.portfolio.total_value))


# ============================================================================
# 7. 每日记录（平台画图用）
# ============================================================================
def record_vars(context):
    record(持仓数=len(context.portfolio.positions))
    record(现金比例=context.portfolio.available_cash / context.portfolio.total_value)
