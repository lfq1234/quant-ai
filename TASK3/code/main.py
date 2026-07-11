# -*- coding: utf-8 -*-
"""
主入口：执行生产级双均线策略回测。
运行方式: cd code && python main.py
"""

import os
import json
import pandas as pd

from config import (BacktestConfig, EntryRule, ExitRule, RiskControl,
                    CostConfig, PositionMode, BASE_DIR, DATA_DIR, IMAGE_DIR)
from data_loader import load_stock_data, fetch_stock_data, save_stock_data
from indicators import calc_indicators
from entry_rules import generate_signals
from backtest_engine import BacktestEngine
from plots import (plot_strategy, plot_backtest, plot_drawdown,
                   plot_metrics_radar, plot_exit_reasons,
                   plot_position_comparison, plot_period_comparison,
                   plot_stock_comparison)


def get_image_path(short_period: int, long_period: int, filename: str) -> str:
    """获取策略图片保存路径（按周期分文件夹）"""
    subdir = os.path.join(IMAGE_DIR, f'{short_period}_{long_period}')
    os.makedirs(subdir, exist_ok=True)
    return os.path.join(subdir, filename)


def main():
    print('=' * 70)
    print('TASK3 双均线策略回测 — 生产级（入场/出场/仓位/风控四要素）')
    print('=' * 70)

    # 默认生产级配置
    config = BacktestConfig(
        name='生产基准策略',
        entry=EntryRule(
            short_period=5, long_period=20,
            use_rsi_filter=True, rsi_upper=70.0,
            use_volume_filter=True, volume_threshold=1.0,
            use_trend_filter=False
        ),
        exit=ExitRule(
            take_profit=0.10, stop_loss=0.05,
            use_signal_exit=True, max_holding_days=20
        ),
        risk=RiskControl(
            max_single_loss_pct=0.02, max_total_position_pct=0.80,
            max_drawdown_cutoff=0.20, daily_loss_cutoff=0.05
        ),
        cost=CostConfig(
            slippage=0.001, commission_rate=0.0003,
            commission_min=5.0, stamp_duty_rate=0.0005
        ),
        position_mode=PositionMode.KELLY,
        fixed_fraction=0.25, kelly_fraction=0.5, kelly_min_trades=5
    )

    # ---------- 1. 加载长江电力数据 ----------
    print('\n[1] 加载长江电力（600900.SH）股价数据...')
    df_cjdl = load_stock_data('cjdl_600900_2025-2026.csv')
    print(f'  数据范围: {df_cjdl["trade_date"].min().strftime("%Y-%m-%d")} ~ '
          f'{df_cjdl["trade_date"].max().strftime("%Y-%m-%d")}')
    print(f'  交易日数: {len(df_cjdl)}')

    # ---------- 2. 基准策略 MA5/MA20 ----------
    print('\n[2] 生产基准策略 MA5/MA20 回测...')
    engine = BacktestEngine(config)
    df_signal = calc_indicators(df_cjdl, config)
    df_signal = generate_signals(df_signal, config)
    df_bt, results = engine.run(df_signal)

    print(f'  初始资金: {results["initial_capital"]:,.0f} 元')
    print(f'  最终资金: {results["final_value"]:,.2f} 元')
    print(f'  总收益率: {results["total_return"]:.2f}%')
    print(f'  年化收益: {results["annual_return"]:.2f}%')
    print(f'  买入持有: {results["buy_hold_return"]:.2f}%')
    print(f'  超额收益: {results["excess_return"]:.2f}%')
    print(f'  最大回撤: {results["max_drawdown"]:.2f}%')
    print(f'  夏普比率: {results["sharpe_ratio"]:.3f}')
    print(f'  索提诺比: {results["sortino_ratio"]:.3f}')
    print(f'  波动率:   {results["volatility"]:.2f}%')
    print(f'  Calmar:  {results["calmar_ratio"]:.3f}')
    print(f'  胜率:     {results["win_rate"]:.2f}%')
    print(f'  盈亏比:   {results["profit_loss_ratio"]:.3f}')
    print(f'  交易次数: {results["n_trades"]}')
    print(f'  平均持仓: {results["avg_holding_days"]} 天')
    print(f'  总成本:   {results["total_cost"]:.2f} 元')
    print(f'  出场原因: {results["exit_reasons"]}')

    buy_mask = df_signal['signal'] == 1
    sell_mask = df_signal['signal'] == -1
    buy_dates = df_signal.loc[buy_mask, 'trade_date'].tolist()
    buy_prices = df_signal.loc[buy_mask, 'close'].tolist()
    sell_dates = df_signal.loc[sell_mask, 'trade_date'].tolist()
    sell_prices = df_signal.loc[sell_mask, 'close'].tolist()

    # ---------- 3. 绘制基准策略图表 ----------
    print('\n[3] 绘制基准策略图表...')
    sp, lp = config.entry.short_period, config.entry.long_period
    plot_strategy(df_signal, config, buy_dates, buy_prices, sell_dates, sell_prices,
                  get_image_path(sp, lp, 'strategy.png'))
    plot_backtest(df_bt, results, get_image_path(sp, lp, 'backtest.png'))
    plot_drawdown(df_bt, results, get_image_path(sp, lp, 'drawdown.png'))
    plot_metrics_radar(results, get_image_path(sp, lp, 'metrics_radar.png'))
    plot_exit_reasons(results, get_image_path(sp, lp, 'exit_reasons.png'))

    # ---------- 4. 不同仓位管理模式对比 ----------
    print('\n[4] 不同仓位管理模式对比...')
    position_modes = [
        PositionMode.FIXED_AMOUNT, PositionMode.FIXED_FRACTION,
        PositionMode.KELLY, PositionMode.RISK_PARITY
    ]
    position_results = []
    for mode in position_modes:
        cfg = BacktestConfig(
            name=f'仓位模式_{mode.value}',
            entry=config.entry, exit=config.exit,
            risk=config.risk, cost=config.cost,
            position_mode=mode,
            fixed_amount=10000.0, fixed_fraction=0.25,
            kelly_fraction=0.5, kelly_min_trades=5
        )
        eng = BacktestEngine(cfg)
        df_temp = calc_indicators(df_cjdl, cfg)
        df_temp = generate_signals(df_temp, cfg)
        _, res = eng.run(df_temp)
        position_results.append(res)
        print(f'  {mode.value:15s}: 总收益={res["total_return"]:>7.2f}%, '
              f'超额={res["excess_return"]:>6.2f}%, '
              f'MDD={res["max_drawdown"]:>6.2f}%, 夏普={res["sharpe_ratio"]:>6.3f}, '
              f'胜率={res["win_rate"]:>5.1f}%, 盈亏比={res["profit_loss_ratio"]:>5.2f}, '
              f'交易={res["n_trades"]}次')

    plot_position_comparison(position_results,
                             os.path.join(IMAGE_DIR, 'comparison_positions.png'))

    # ---------- 5. 不同均线周期对比 ----------
    print('\n[5] 不同均线周期对比...')
    period_pairs = [(5, 10), (5, 15), (5, 20), (10, 20), (10, 30)]
    all_period_results = []
    for sp_p, lp_p in period_pairs:
        cfg = BacktestConfig(
            name=f'MA{sp_p}/MA{lp_p}',
            entry=EntryRule(short_period=sp_p, long_period=lp_p,
                            use_rsi_filter=True, rsi_upper=70.0,
                            use_volume_filter=True, volume_threshold=1.0),
            exit=ExitRule(take_profit=0.10, stop_loss=0.05,
                          use_signal_exit=True, max_holding_days=20),
            risk=config.risk, cost=config.cost,
            position_mode=PositionMode.KELLY,
            fixed_fraction=0.25, kelly_fraction=0.5, kelly_min_trades=5
        )
        eng = BacktestEngine(cfg)
        df_temp = calc_indicators(df_cjdl, cfg)
        df_temp = generate_signals(df_temp, cfg)
        _, res = eng.run(df_temp)
        all_period_results.append(res)
        print(f'  MA{sp_p}/MA{lp_p}: 总收益={res["total_return"]:>7.2f}%, '
              f'年化={res["annual_return"]:>6.2f}%, 超额={res["excess_return"]:>6.2f}%, '
              f'MDD={res["max_drawdown"]:>6.2f}%, 夏普={res["sharpe_ratio"]:>6.3f}, '
              f'胜率={res["win_rate"]:>5.1f}%, 盈亏比={res["profit_loss_ratio"]:>5.2f}, '
              f'交易={res["n_trades"]}次')

    plot_period_comparison(all_period_results,
                           os.path.join(IMAGE_DIR, 'comparison_periods.png'))

    # ---------- 6. 不同股票对比 ----------
    print('\n[6] 不同股票对比（MA5/MA20）...')
    stock_list = [
        ('600900.SH', '长江电力', df_cjdl),
        ('600519.SH', '贵州茅台', None),
        ('601318.SH', '中国平安', None),
    ]
    stock_results = []
    for ts_code, name, df_exist in stock_list:
        if df_exist is not None:
            df_s = df_exist.copy()
        else:
            print(f'  获取 {name}（{ts_code}）数据...')
            try:
                df_s = fetch_stock_data(ts_code)
                save_stock_data(df_s, ts_code)
            except Exception as e:
                print(f'  获取失败: {e}，尝试加载本地数据...')
                try:
                    df_s = load_stock_data(f'{ts_code.split(".")[0]}_data.csv')
                except Exception:
                    print(f'  本地数据也不存在，跳过')
                    continue

        cfg = BacktestConfig(
            name=name,
            entry=EntryRule(short_period=5, long_period=20,
                            use_rsi_filter=True, rsi_upper=70.0,
                            use_volume_filter=True, volume_threshold=1.0),
            exit=ExitRule(take_profit=0.10, stop_loss=0.05,
                          use_signal_exit=True, max_holding_days=20),
            risk=config.risk, cost=config.cost,
            position_mode=PositionMode.KELLY,
            fixed_fraction=0.25, kelly_fraction=0.5, kelly_min_trades=5
        )
        eng = BacktestEngine(cfg)
        df_s = calc_indicators(df_s, cfg)
        df_s = generate_signals(df_s, cfg)
        _, res = eng.run(df_s)
        res['name'] = name
        res['ts_code'] = ts_code
        stock_results.append(res)
        print(f'  {name}: 总收益={res["total_return"]:>7.2f}%, '
              f'买入持有={res["buy_hold_return"]:>7.2f}%, '
              f'超额={res["excess_return"]:>6.2f}%, '
              f'MDD={res["max_drawdown"]:>6.2f}%, '
              f'夏普={res["sharpe_ratio"]:>6.3f}, '
              f'胜率={res["win_rate"]:>5.1f}%, '
              f'盈亏比={res["profit_loss_ratio"]:>5.2f}')

    plot_stock_comparison(stock_results,
                          os.path.join(IMAGE_DIR, 'comparison_stocks.png'))

    # ---------- 7. 保存结果 ----------
    print('\n[7] 保存回测结果...')
    output = {
        'base': results,
        'positions': position_results,
        'periods': all_period_results,
        'stocks': stock_results,
        'trades': [
            {
                'entry_date': t.entry_date.strftime('%Y-%m-%d'),
                'exit_date': t.exit_date.strftime('%Y-%m-%d') if t.exit_date else None,
                'entry_price': round(t.entry_price, 3),
                'exit_price': round(t.exit_price, 3),
                'shares': t.shares,
                'gross_pnl': round(t.gross_pnl, 2),
                'cost': round(t.cost, 2),
                'net_pnl': round(t.net_pnl, 2),
                'net_return': round(t.net_return * 100, 2),
                'holding_days': t.holding_days,
                'exit_reason': t.exit_reason
            }
            for t in engine.trades
        ]
    }
    results_path = os.path.join(DATA_DIR, 'backtest_results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'  结果已保存: {results_path}')

    print('\n' + '=' * 70)
    print('TASK3 生产级回测完成！')
    print('=' * 70)


if __name__ == '__main__':
    main()
