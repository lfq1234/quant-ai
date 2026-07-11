# -*- coding: utf-8 -*-
"""
出场规则模块：止盈 / 止损 / 信号 / 时间 四位一体。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd

from config import ExitRule


@dataclass
class TradeRecord:
    """单笔交易记录"""
    entry_date: datetime
    exit_date: Optional[datetime] = None
    entry_price: float = 0.0
    exit_price: float = 0.0
    shares: int = 0
    gross_pnl: float = 0.0
    cost: float = 0.0
    net_pnl: float = 0.0
    net_return: float = 0.0
    holding_days: int = 0
    exit_reason: str = ''  # signal / take_profit / stop_loss / time_exit / final


class ExitChecker:
    """出场条件检查器"""

    def __init__(self, exit_rule: ExitRule):
        self.rule = exit_rule

    def check(self, row: pd.Series, entry_price: float, holding_days: int) -> Optional[str]:
        """
        检查是否触发出场条件，返回出场原因或 None。

        检查顺序：止损 > 止盈 > 时间出场 > 信号出场
        """
        price = row['close']
        unrealized_return = (price - entry_price) / entry_price

        # 止损出场
        if unrealized_return <= -self.rule.stop_loss:
            return 'stop_loss'

        # 止盈出场
        if unrealized_return >= self.rule.take_profit:
            return 'take_profit'

        # 时间出场
        if holding_days >= self.rule.max_holding_days:
            return 'time_exit'

        # 信号出场（死叉）
        if self.rule.use_signal_exit and row['signal'] == -1:
            return 'signal'

        return None
