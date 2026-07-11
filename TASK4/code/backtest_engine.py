# -*- coding: utf-8 -*-
"""
海龟策略回测引擎：基于唐奇安通道突破 + ATR 仓位管理 + 动态止损。
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

from config import TurtleConfig
from indicators import calc_indicators
from signals import generate_signals


@dataclass
class TradeRecord:
    """单笔交易记录"""
    entry_date: datetime
    exit_date: Optional[datetime] = None
    entry_price: float = 0.0
    exit_price: float = 0.0
    shares: int = 0
    units: int = 0
    gross_pnl: float = 0.0
    cost: float = 0.0
    net_pnl: float = 0.0
    net_return: float = 0.0
    holding_days: int = 0
    exit_reason: str = ''  # stop_loss / exit_signal / final


class TurtleBacktestEngine:
    """海龟策略回测引擎"""

    def __init__(self, config: TurtleConfig):
        self.config = config
        self.trades: List[TradeRecord] = []

    def _calc_buy_cost(self, price: float, shares: int) -> Tuple[float, float]:
        """计算买入总成本与交易成本"""
        amount = price * shares
        slippage_cost = amount * self.config.slippage
        commission = max(amount * self.config.commission_rate, self.config.commission_min)
        return amount + slippage_cost + commission, slippage_cost + commission

    def _calc_sell_proceeds(self, price: float, shares: int) -> Tuple[float, float]:
        """计算卖出实得金额与交易成本"""
        amount = price * shares
        slippage_cost = amount * self.config.slippage
        commission = max(amount * self.config.commission_rate, self.config.commission_min)
        stamp_duty = amount * self.config.stamp_duty_rate
        return amount - slippage_cost - commission - stamp_duty, slippage_cost + commission + stamp_duty

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """执行海龟策略回测"""
        df = df.copy()
        df = calc_indicators(df, self.config)
        df = generate_signals(df, self.config)

        # 从第一个有效数据开始（等通道和ATR计算完成）
        start_idx = max(self.config.entry_window, self.config.atr_period) - 1
        df_bt = df.iloc[start_idx:].copy().reset_index(drop=True)

        cash = self.config.initial_capital
        total_shares = 0
        portfolio_values = []

        # 持仓状态
        position = 0  # 0=空仓, 1=持仓
        entry_price = 0.0
        entry_date = None
        entry_atr = 0.0
        current_units = 0
        holding_days = 0
        stop_loss_price = 0.0

        for i, row in df_bt.iterrows():
            price = row['close']
            date = row['trade_date']
            atr = row['ATR'] if not pd.isna(row['ATR']) else 0
            equity = cash + total_shares * price
            portfolio_values.append(equity)

            # 持仓状态下
            if position == 1:
                holding_days += 1
                exit_reason = None

                # 1. 动态止损检查：价格跌破止损价
                if price <= stop_loss_price:
                    exit_reason = 'stop_loss'
                # 2. 反向突破出场：价格跌破 exit_window 日最低价
                elif row['signal'] == -1:
                    exit_reason = 'exit_signal'

                if exit_reason:
                    effective_sell_price = price * (1 - self.config.slippage)
                    proceeds, cost = self._calc_sell_proceeds(effective_sell_price, total_shares)
                    cash += proceeds

                    gross_pnl = (effective_sell_price - entry_price) * total_shares
                    net_pnl = proceeds - entry_price * total_shares
                    net_return = net_pnl / (entry_price * total_shares) if entry_price * total_shares > 0 else 0

                    trade = TradeRecord(
                        entry_date=entry_date, exit_date=date,
                        entry_price=entry_price, exit_price=effective_sell_price,
                        shares=total_shares, units=current_units,
                        gross_pnl=gross_pnl, cost=cost,
                        net_pnl=net_pnl, net_return=net_return,
                        holding_days=holding_days, exit_reason=exit_reason
                    )
                    self.trades.append(trade)

                    total_shares = 0
                    position = 0
                    entry_price = 0.0
                    entry_date = None
                    entry_atr = 0.0
                    current_units = 0
                    holding_days = 0
                    stop_loss_price = 0.0
                    continue

                # 3. 加仓逻辑：每上涨 add_atr_step × ATR，加仓 1 单位，最多 max_units
                if current_units < self.config.max_units and atr > 0:
                    target_price = entry_price + self.config.add_atr_step * entry_atr * current_units
                    if price >= target_price:
                        # 计算新单位头寸
                        unit_shares = int((self.config.initial_capital * self.config.risk_per_trade) / (atr * (1 + self.config.slippage)))
                        if unit_shares > 0:
                            effective_buy_price = price * (1 + self.config.slippage)
                            total_cost, _ = self._calc_buy_cost(effective_buy_price, unit_shares)
                            if total_cost <= cash:
                                cash -= total_cost
                                total_shares += unit_shares
                                current_units += 1
                                # 更新止损价（以最新加仓价为基准）
                                stop_loss_price = effective_buy_price - self.config.atr_stop_multiplier * atr

            # 空仓状态下，检查入场信号
            elif position == 0 and row['signal'] == 1 and atr > 0:
                effective_buy_price = price * (1 + self.config.slippage)
                # 单位头寸 = (账户资金 × risk_per_trade) / ATR
                unit_shares = int((self.config.initial_capital * self.config.risk_per_trade) / (atr * (1 + self.config.slippage)))

                if unit_shares > 0:
                    total_cost, _ = self._calc_buy_cost(effective_buy_price, unit_shares)
                    if total_cost <= cash:
                        cash -= total_cost
                        total_shares = unit_shares
                        position = 1
                        entry_price = effective_buy_price
                        entry_date = date
                        entry_atr = atr
                        current_units = 1
                        holding_days = 0
                        stop_loss_price = effective_buy_price - self.config.atr_stop_multiplier * atr

        df_bt['portfolio_value'] = portfolio_values
        df_bt['daily_return'] = df_bt['portfolio_value'].pct_change()

        # 若最后一行仍持仓，按收盘价清仓
        if position == 1 and entry_date is not None:
            last_price = df_bt['close'].iloc[-1]
            last_date = df_bt['trade_date'].iloc[-1]
            effective_sell_price = last_price * (1 - self.config.slippage)
            proceeds, cost = self._calc_sell_proceeds(effective_sell_price, total_shares)
            cash += proceeds

            gross_pnl = (effective_sell_price - entry_price) * total_shares
            net_pnl = proceeds - entry_price * total_shares
            net_return = net_pnl / (entry_price * total_shares) if entry_price * total_shares > 0 else 0

            self.trades.append(TradeRecord(
                entry_date=entry_date, exit_date=last_date,
                entry_price=entry_price, exit_price=effective_sell_price,
                shares=total_shares, units=current_units,
                gross_pnl=gross_pnl, cost=cost,
                net_pnl=net_pnl, net_return=net_return,
                holding_days=holding_days, exit_reason='final'
            ))
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

        # 交易质量
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
            avg_units = np.mean([t.units for t in closed_trades])
        else:
            win_rate = 0.0
            profit_loss_ratio = 0.0
            avg_holding_days = 0.0
            total_cost = 0.0
            exit_reasons = {}
            avg_units = 0.0

        calmar = annual_return / abs(max_drawdown) if max_drawdown < 0 else 0.0

        # 索提诺比率
        downside = daily_returns[daily_returns < 0]
        sortino = (np.sqrt(252) * (daily_returns.mean() - 0.02/252) / downside.std()
                   if len(downside) > 0 and downside.std() > 0 else 0.0)

        return {
            'name': self.config.name,
            'stock_name': self.config.stock_name,
            'entry_window': self.config.entry_window,
            'exit_window': self.config.exit_window,
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
            'avg_units': round(avg_units, 2),
            'total_cost': round(total_cost, 2),
            'exit_reasons': exit_reasons,
            'start_date': df_bt['trade_date'].iloc[0].strftime('%Y-%m-%d'),
            'end_date': df_bt['trade_date'].iloc[-1].strftime('%Y-%m-%d'),
            'n_trading_days': n_days,
        }
