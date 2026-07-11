# -*- coding: utf-8 -*-
"""
TASK4 海龟交易策略配置模块。
所有参数集中管理，包括唐奇安通道周期、ATR、止损/止盈、仓位管理等。
"""

import os
from dataclasses import dataclass, field

# ==================== 路径常量 ====================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMAGE_DIR = os.path.join(BASE_DIR, 'images')

# Tushare Token
TOKEN = 'eedeac8183a4726f28d85aade5731a3182166105900e5ddfd6c8b402'


@dataclass
class TurtleConfig:
    """海龟策略总配置"""
    # 初始资金
    initial_capital: float = 100000.0

    # 唐奇安通道周期
    entry_window: int = 20       # 入场窗口：突破N日最高价买入
    exit_window: int = 10        # 出场窗口：跌破N日最低价卖出

    # ATR 配置
    atr_period: int = 20         # ATR 计算周期

    # 止损：入场价 - 2 × ATR
    atr_stop_multiplier: float = 2.0  # ATR 止损倍数

    # 加仓规则
    add_atr_step: float = 0.5    # 每上涨多少 ATR 加仓一次
    max_units: int = 4           # 最大持仓单位数

    # 风险参数：每个单位亏损 = 账户资金 × risk_per_trade
    risk_per_trade: float = 0.01  # 每笔交易风险 = 1% 账户资金

    # 交易成本
    slippage: float = 0.001      # 滑点 0.1%
    commission_rate: float = 0.0003  # 佣金率 0.03%
    commission_min: float = 5.0  # 最低佣金 5元
    stamp_duty_rate: float = 0.0005  # 印花税率 0.05%（仅卖出）

    # 策略名称
    name: str = '海龟策略（系统一）'
    stock_name: str = '长江电力'
    ts_code: str = '600900.SH'
