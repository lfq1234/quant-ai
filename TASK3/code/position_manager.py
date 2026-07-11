# -*- coding: utf-8 -*-
"""
仓位管理模块：支持固定金额、固定比例、凯利公式、风险平价四种模式。
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional

from config import BacktestConfig, PositionMode


class PositionSizer:
    """仓位管理器：支持固定金额、固定比例、凯利公式、风险平价"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.trades: List[Dict] = []

    def update(self, net_return: float):
        """每完成一笔交易后更新历史记录"""
        self.trades.append({'return': net_return})

    def get_fraction(self, current_price: float, current_atr: Optional[float],
                     total_equity: float) -> float:
        """根据模式计算当前应投入的资金比例（0~1）"""
        mode = self.config.position_mode

        if mode == PositionMode.FIXED_AMOUNT:
            return min(self.config.fixed_amount / total_equity, 1.0)

        if mode == PositionMode.FIXED_FRACTION:
            return self.config.fixed_fraction

        if mode == PositionMode.KELLY:
            return self._kelly_fraction()

        if mode == PositionMode.RISK_PARITY:
            return self._risk_parity_fraction(current_price, current_atr, total_equity)

        return self.config.fixed_fraction

    def _kelly_fraction(self) -> float:
        """半凯利公式动态仓位"""
        if len(self.trades) < self.config.kelly_min_trades:
            return self.config.fixed_fraction

        wins = [t for t in self.trades if t['return'] > 0]
        losses = [t for t in self.trades if t['return'] <= 0]

        if len(losses) == 0 or len(self.trades) == 0:
            return self.config.fixed_fraction

        W = len(wins) / len(self.trades)
        avg_win = np.mean([t['return'] for t in wins]) if wins else 0.0
        avg_loss = abs(np.mean([t['return'] for t in losses])) if losses else 0.0

        if avg_loss < 1e-9 or avg_win <= 0:
            return self.config.fixed_fraction

        R = avg_win / avg_loss
        kelly = W - (1 - W) / R
        fraction = kelly * self.config.kelly_fraction
        return max(0.05, min(fraction, 0.50))

    def _risk_parity_fraction(self, price: float, atr: Optional[float],
                              total_equity: float) -> float:
        """基于 ATR 的风险平价仓位"""
        if atr is None or pd.isna(atr) or atr <= 0 or price <= 0:
            return self.config.fixed_fraction
        risk_per_unit = atr / price
        target_fraction = self.config.risk_parity_multiplier * 0.01 / risk_per_unit
        return max(0.05, min(target_fraction, 0.50))
