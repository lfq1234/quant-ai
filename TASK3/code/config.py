# -*- coding: utf-8 -*-
"""
配置模块：所有数据类、枚举和路径常量集中管理。
其他模块通过 from config import xxx 引用。
"""

import os
from dataclasses import dataclass, field
from enum import Enum

# ==================== 路径常量 ====================
# TASK3 根目录（code 的上一级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMAGE_DIR = os.path.join(BASE_DIR, 'images')

# Tushare Token
TOKEN = 'eedeac8183a4726f28d85aade5731a3182166105900e5ddfd6c8b402'


# ==================== 枚举 ====================
class PositionMode(str, Enum):
    """仓位管理模式"""
    FIXED_AMOUNT = 'fixed_amount'      # 每次固定金额
    FIXED_FRACTION = 'fixed_fraction'  # 每次固定比例
    KELLY = 'kelly'                    # 凯利公式
    RISK_PARITY = 'risk_parity'        # 风险平价（ATR）


# ==================== 配置数据类 ====================
@dataclass
class CostConfig:
    """交易成本配置"""
    slippage: float = 0.001          # 滑点 0.1%（买卖均影响）
    commission_rate: float = 0.0003  # 佣金率 0.03%
    commission_min: float = 5.0      # 最低佣金 5元
    stamp_duty_rate: float = 0.0005  # 印花税率 0.05%（仅卖出）


@dataclass
class EntryRule:
    """入场规则配置"""
    short_period: int = 5
    long_period: int = 20
    use_rsi_filter: bool = True      # RSI 过滤，避免超买买入
    rsi_period: int = 14
    rsi_upper: float = 70.0          # RSI 超过此值不买入
    use_volume_filter: bool = True   # 成交量过滤
    volume_period: int = 20
    volume_threshold: float = 1.0    # 当日成交量 >= 均量 × threshold 才买入
    use_trend_filter: bool = False   # 趋势强度过滤（收盘价在长均线上方）


@dataclass
class ExitRule:
    """出场规则配置"""
    take_profit: float = 0.10        # 止盈 10%
    stop_loss: float = 0.05          # 止损 5%
    use_signal_exit: bool = True     # 死叉信号出场
    max_holding_days: int = 20       # 时间出场


@dataclass
class RiskControl:
    """风险控制配置"""
    max_single_loss_pct: float = 0.02    # 单笔最大亏损 2%
    max_total_position_pct: float = 0.80  # 总持仓 80%
    max_drawdown_cutoff: float = 0.20     # 累计回撤 20% 熔断
    daily_loss_cutoff: float = 0.05       # 单日亏损 5% 熔断


@dataclass
class BacktestConfig:
    """回测总配置"""
    initial_capital: float = 100000.0
    entry: EntryRule = field(default_factory=EntryRule)
    exit: ExitRule = field(default_factory=ExitRule)
    risk: RiskControl = field(default_factory=RiskControl)
    cost: CostConfig = field(default_factory=CostConfig)
    position_mode: PositionMode = PositionMode.KELLY
    fixed_amount: float = 10000.0       # 固定金额模式每次投入
    fixed_fraction: float = 0.25        # 固定比例/凯利默认比例
    kelly_fraction: float = 0.5         # 半凯利系数
    kelly_min_trades: int = 5           # 启用凯利前最少历史交易数
    risk_parity_atr_period: int = 14    # 风险平价 ATR 周期
    risk_parity_multiplier: float = 1.0 # 风险平价乘数
    name: str = '默认策略'
