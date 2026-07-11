# -*- coding: utf-8 -*-
"""
回测引擎模块：整合入场、出场、仓位、风控四要素，执行完整回测。
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

from config import BacktestConfig
from indicators import calc_indicators
from entry_rules import generate_signals
from position_manager import PositionSizer
from exit_rules import TradeRecord, ExitChecker
from risk_manager import RiskManager


class BacktestEngine:
    """生产级双均线回测引擎"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.position_sizer = PositionSizer(config)
        self.exit_checker = ExitChecker(config.exit)
        self.risk_manager = RiskManager(config.risk)
        self.trades: List[TradeRecord] = []
        self.current_trade: Optional[TradeRecord] = None

    def _calc_buy_cost(self, price: float, shares: int) -> Tuple[float, float]:
        """计算买入总成本与交易成本（含滑点和佣金）"""
        amount = price * shares
        slippage_cost = amount * self.config.cost.slippage
        commission = max(amount * self.config.cost.commission_rate,
                         self.config.cost.commission_min)
        return amount + slippage_cost + commission, slippage_cost + commission

    def _calc_sell_proceeds(self, price: float, shares: int) -> Tuple[float, float]:
        """计算卖出实得金额与交易成本（含滑点、佣金、印花税）"""
        amount = price * shares
        slippage_cost = amount * self.config.cost.slippage
        commission = max(amount * self.config.cost.commission_rate,
                         self.config.cost.commission_min)
        stamp_duty = amount * self.config.cost.stamp_duty_rate
        return amount - slippage_cost - commission - stamp_duty, \
               slippage_cost + commission + stamp_duty

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """执行回测，返回 (回测DataFrame, 结果字典)"""
        df = df.copy()
        df = calc_indicators(df, self.config)
        df = generate_signals(df, self.config)

        lp = self.config.entry.long_period
        start_idx = max(lp - 1, self.config.risk_parity_atr_period - 1, 20)
        df_bt = df.iloc[start_idx:].copy().reset_index(drop=True)

        cash = self.config.initial_capital
        shares = 0
        position = 0
        portfolio_values = []
        entry_price = 0.0
        entry_date = None
        holding_days = 0
        peak_equity = self.config.initial_capital
        self.risk_manager.peak_equity = peak_equity

        for i, row in df_bt.iterrows():
            price = row['close']
            date = row['trade_date']
            equity = cash + shares * price
            portfolio_values.append(equity)

            # 风控：更新峰值、检查回撤与单日亏损
            self.risk_manager.update_peak(equity)
            self.risk_manager.check_drawdown_halt(equity)
            daily_return = ((portfolio_values[-1] - portfolio_values[-2]) /
                            portfolio_values[-2]) if i > 0 else 0
            self.risk_manager.check_daily_loss_halt(daily_return)

            # 持仓状态下，优先检查出场条件
            if position == 1:
                holding_days += 1
                exit_reason = self.exit_checker.check(row, entry_price, holding_days)
                if exit_reason:
                    effective_sell_price = price * (1 - self.config.cost.slippage)
                    proceeds, cost = self._calc_sell_proceeds(effective_sell_price, shares)
                    cash += proceeds

                    gross_pnl = (effective_sell_price - entry_price) * shares
                    net_pnl = proceeds - entry_price * shares
                    net_return = net_pnl / (entry_price * shares)

                    trade = TradeRecord(
                        entry_date=entry_date, exit_date=date,
                        entry_price=entry_price, exit_price=effective_sell_price,
                        shares=shares, gross_pnl=gross_pnl, cost=cost,
                        net_pnl=net_pnl, net_return=net_return,
                        holding_days=holding_days, exit_reason=exit_reason
                    )
                    self.trades.append(trade)
                    self.position_sizer.update(net_return)

                    shares = 0
                    position = 0
                    entry_price = 0.0
                    entry_date = None
                    holding_days = 0

            # 空仓状态下，检查入场信号
            elif position == 0 and row['signal'] == 1 and not self.risk_manager.is_halted:
                atr = row['ATR'] if 'ATR' in row else None
                fraction = self.position_sizer.get_fraction(price, atr, equity)

                # 总仓位控制
                fraction = self.risk_manager.clip_position_fraction(fraction)
                capital_to_use = equity * fraction

                # 单笔止损控制
                max_shares_by_risk = self.risk_manager.max_shares_by_risk(
                    price, equity, self.config.exit.stop_loss
                )

                effective_buy_price = price * (1 + self.config.cost.slippage)
                shares_to_buy = int(capital_to_use / effective_buy_price)
                shares_to_buy = min(shares_to_buy, max_shares_by_risk)

                if shares_to_buy > 0:
                    total_cost, _ = self._calc_buy_cost(effective_buy_price, shares_to_buy)
                    if total_cost <= cash:
                        cash -= total_cost
                        shares = shares_to_buy
                        position = 1
                        entry_price = effective_buy_price
                        entry_date = date
                        holding_days = 0

        df_bt['portfolio_value'] = portfolio_values
        df_bt['daily_return'] = df_bt['portfolio_value'].pct_change()

        # 若最后一行仍持仓，按收盘价清仓
        if position == 1 and entry_date is not None:
            last_price = df_bt['close'].iloc[-1]
            last_date = df_bt['trade_date'].iloc[-1]
            effective_sell_price = last_price * (1 - self.config.cost.slippage)
            proceeds, cost = self._calc_sell_proceeds(effective_sell_price, shares)
            cash += proceeds
            gross_pnl = (effective_sell_price - entry_price) * shares
            net_pnl = proceeds - entry_price * shares
            net_return = net_pnl / (entry_price * shares)

            self.trades.append(TradeRecord(
                entry_date=entry_date, exit_date=last_date,
                entry_price=entry_price, exit_price=effective_sell_price,
                shares=shares, gross_pnl=gross_pnl, cost=cost,
                net_pnl=net_pnl, net_return=net_return,
                holding_days=holding_days, exit_reason='final'
            ))
            self.position_sizer.update(net_return)
            df_bt.loc[df_bt.index[-1], 'portfolio_value'] = cash

        # 买入持有基准
        first_price = df_bt['close'].iloc[0]
        last_price = df_bt['close'].iloc[-1]
        buy_hold_return = (last_price - first_price) / first_price

        results = self._calc_metrics(df_bt, buy_hold_return)
        return df_bt, results

    def _calc_metrics(self, df_bt: pd.DataFrame, buy_hold_return: float) -> Dict:
        """计算完整绩效指标"""
        initial = self.config.initial_capital
        final_value = df_bt['portfolio_value'].iloc[-1]
        total_return = (final_value - initial) / initial

        n_days = len(df_bt)
        n_years = n_days / 252
        annual_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0

        excess_return = total_return - buy_hold_return

        # 最大回撤
        cummax = df_bt['portfolio_value'].cummax()
        drawdown = (df_bt['portfolio_value'] - cummax) / cummax
        max_drawdown = drawdown.min()

        # 夏普比率
        daily_returns = df_bt['daily_return'].dropna()
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            annual_rf = 0.02
            daily_rf = annual_rf / 252
            excess = daily_returns - daily_rf
            sharpe = np.sqrt(252) * excess.mean() / excess.std()
        else:
            sharpe = 0.0

        volatility = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 0 else 0.0

        # 交易质量指标
        closed_trades = self.trades
        n_trades = len(closed_trades)
        if n_trades > 0:
            wins = [t for t in closed_trades if t.net_pnl > 0]
            losses = [t for t in closed_trades if t.net_pnl <= 0]
            win_rate = len(wins) / n_trades
            avg_win = np.mean([t.net_return for t in wins]) if wins else 0.0
            avg_loss = abs(np.mean([t.net_return for t in losses])) if losses else 0.0
            profit_loss_ratio = avg_win / avg_loss if avg_loss > 1e-9 else 0.0
            avg_holding_days = np.mean([t.holding_days for t in closed_trades])
            total_cost = sum(t.cost for t in closed_trades)
            exit_reasons = {}
            for t in closed_trades:
                exit_reasons[t.exit_reason] = exit_reasons.get(t.exit_reason, 0) + 1
        else:
            win_rate = 0.0
            profit_loss_ratio = 0.0
            avg_holding_days = 0.0
            total_cost = 0.0
            exit_reasons = {}

        calmar = annual_return / abs(max_drawdown) if max_drawdown < 0 else 0.0

        # 索提诺比率
        downside = daily_returns[daily_returns < 0]
        sortino = (np.sqrt(252) * (daily_returns.mean() - 0.02/252) / downside.std()
                   if len(downside) > 0 and downside.std() > 0 else 0.0)

        return {
            'name': self.config.name,
            'short_period': self.config.entry.short_period,
            'long_period': self.config.entry.long_period,
            'position_mode': self.config.position_mode.value,
            'initial_capital': initial,
            'final_value': round(final_value, 2),
            'total_return': round(total_return * 100, 2),
            'annual_return': round(annual_return * 100, 2),
            'buy_hold_return': round(buy_hold_return * 100, 2),
            'excess_return': round(excess_return * 100, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'sharpe_ratio': round(sharpe, 3),
            'sortino_ratio': round(sortino, 3),
            'volatility': round(volatility * 100, 2),
            'calmar_ratio': round(calmar, 3),
            'win_rate': round(win_rate * 100, 2),
            'profit_loss_ratio': round(profit_loss_ratio, 3),
            'n_trades': n_trades,
            'avg_holding_days': round(avg_holding_days, 1),
            'total_cost': round(total_cost, 2),
            'exit_reasons': exit_reasons,
            'start_date': df_bt['trade_date'].iloc[0].strftime('%Y-%m-%d'),
            'end_date': df_bt['trade_date'].iloc[-1].strftime('%Y-%m-%d'),
            'n_trading_days': n_days,
        }
