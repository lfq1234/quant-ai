# -*- coding: utf-8 -*-
"""
风险控制模块：单笔止损 / 总仓位上限 / 最大回撤熔断 / 单日大跌熔断。
"""

from config import RiskControl


class RiskManager:
    """风险管理器：四层防线"""

    def __init__(self, risk_config: RiskControl):
        self.config = risk_config
        self.trading_halted = False
        self.peak_equity = 0.0

    def update_peak(self, equity: float):
        """更新历史最高净值"""
        self.peak_equity = max(self.peak_equity, equity)

    def check_drawdown_halt(self, equity: float) -> bool:
        """
        检查累计回撤是否触发熔断。
        返回 True 表示应暂停新开仓。
        """
        if self.peak_equity > 0:
            drawdown = (equity - self.peak_equity) / self.peak_equity
            if drawdown <= -self.config.max_drawdown_cutoff:
                self.trading_halted = True
        return self.trading_halted

    def check_daily_loss_halt(self, daily_return: float) -> bool:
        """
        检查单日亏损是否触发熔断。
        返回 True 表示应暂停新开仓。
        """
        if daily_return <= -self.config.daily_loss_cutoff:
            self.trading_halted = True
        return self.trading_halted

    def clip_position_fraction(self, fraction: float) -> float:
        """总仓位控制：限制最大持仓比例"""
        return min(fraction, self.config.max_total_position_pct)

    def max_shares_by_risk(self, price: float, equity: float, stop_loss: float) -> int:
        """
        单笔止损控制：保证最大亏损不超过总资金的 max_single_loss_pct。
        返回允许买入的最大股数。
        """
        if stop_loss <= 0:
            return 999999
        max_risk_capital = equity * self.config.max_single_loss_pct
        risk_per_share = price * stop_loss
        return int(max_risk_capital / risk_per_share) if risk_per_share > 0 else 0

    @property
    def is_halted(self) -> bool:
        """当前是否处于熔断状态"""
        return self.trading_halted
