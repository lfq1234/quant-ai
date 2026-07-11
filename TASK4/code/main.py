# -*- coding: utf-8 -*-
"""
TASK4 主入口：执行海龟交易策略回测。
运行方式: cd code && python main.py
"""

import os
import sys
import json
import pandas as pd

# 确保可以导入同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TurtleConfig, IMAGE_DIR, DATA_DIR
from data_loader import load_stock_data, fetch_stock_data, save_stock_data
from backtest_engine import TurtleBacktestEngine
from plots import (plot_strategy, plot_backtest, plot_drawdown,
                   plot_metrics_radar, plot_exit_reasons,
                   plot_period_comparison, plot_stock_comparison,
                   plot_multi_param_heatmap)


def main():
    print('=' * 70)
    print('TASK4 海龟交易策略回测 —— 唐奇安通道 + ATR + 动态止损')
    print('=' * 70)

    # 默认配置：系统一（突破20日最高，跌破10日最低）
    config = TurtleConfig(
        name='海龟策略（系统一）',
        stock_name='长江电力',
        ts_code='600900.SH',
        entry_window=20,
        exit_window=10,
        atr_period=20,
        risk_per_trade=0.01,
        max_units=4,
        add_atr_step=0.5,
        atr_stop_multiplier=2.0
    )

    # ========== 1. 加载长江电力数据 ==========
    print('\n[1] 加载长江电力（600900.SH）股价数据...')
    df = load_stock_data('cjdl_600900_2025-2026.csv')
    print(f'  数据范围: {df["trade_date"].min().strftime("%Y-%m-%d")} ~ '
          f'{df["trade_date"].max().strftime("%Y-%m-%d")}')
    print(f'  交易日数: {len(df)}')

    # ========== 2. 基准策略回测（20/10） ==========
    print(f'\n[2] 海龟策略回测（入场{config.entry_window}日，出场{config.exit_window}日）...')
    engine = TurtleBacktestEngine(config)
    df_bt, results = engine.run(df)

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
    print(f'  平均加仓: {results["avg_units"]} 单位')
    print(f'  总成本:   {results["total_cost"]:.2f} 元')
    print(f'  出场原因: {results["exit_reasons"]}')

    # 提取买卖信号点
    buy_dates, buy_prices = [], []
    sell_dates, sell_prices = [], []
    for t in engine.trades:
        buy_dates.append(t.entry_date)
        buy_prices.append(t.entry_price)
        if t.exit_date and t.exit_reason != 'final':
            sell_dates.append(t.exit_date)
            sell_prices.append(t.exit_price)
    # final 清仓也标记
    if engine.trades and engine.trades[-1].exit_reason == 'final':
        sell_dates.append(engine.trades[-1].exit_date)
        sell_prices.append(engine.trades[-1].exit_price)

    # 需要完整数据（含通道）用于画图
    df_full = df.copy()
    from indicators import calc_indicators
    df_full = calc_indicators(df_full, config)

    # ========== 3. 绘制基准策略图表 ==========
    print('\n[3] 绘制基准策略图表...')
    subdir = os.path.join(IMAGE_DIR, f'{config.entry_window}_{config.exit_window}')
    os.makedirs(subdir, exist_ok=True)
    plot_strategy(df_full, config, buy_dates, buy_prices, sell_dates, sell_prices,
                  os.path.join(subdir, 'strategy.png'))
    plot_backtest(df_bt, results, os.path.join(subdir, 'backtest.png'))
    plot_drawdown(df_bt, results, os.path.join(subdir, 'drawdown.png'))
    plot_metrics_radar(results, os.path.join(subdir, 'metrics_radar.png'))
    plot_exit_reasons(results, os.path.join(subdir, 'exit_reasons.png'))

    # ========== 4. 不同通道周期对比 ==========
    print('\n[4] 不同通道周期对比...')
    period_pairs = [
        (5, 3),     # 极短周期，信号最敏感
        (5, 5),     # 短周期对称
        (10, 5),    # 短周期
        (10, 10),   # 短周期对称
        (15, 7),    # 中短周期
        (20, 10),   # 系统一（经典海龟）
        (30, 15),   # 中长周期
        (55, 20),   # 系统二（经典海龟）
    ]
    all_period_results = []
    for ew, xw in period_pairs:
        cfg = TurtleConfig(
            name=f'海龟_{ew}_{xw}',
            stock_name=config.stock_name,
            ts_code=config.ts_code,
            entry_window=ew, exit_window=xw,
            atr_period=20,
            risk_per_trade=0.01, max_units=4,
            add_atr_step=0.5, atr_stop_multiplier=2.0
        )
        eng = TurtleBacktestEngine(cfg)
        df_temp = df.copy()
        _, res = eng.run(df_temp)
        all_period_results.append(res)
        print(f'  入场{ew}/出场{xw}: 总收益={res["total_return"]:>7.2f}%, '
              f'年化={res["annual_return"]:>6.2f}%, 超额={res["excess_return"]:>6.2f}%, '
              f'MDD={res["max_drawdown"]:>6.2f}%, 夏普={res["sharpe_ratio"]:>6.3f}, '
              f'胜率={res["win_rate"]:>5.1f}%, 盈亏比={res["profit_loss_ratio"]:>5.2f}, '
              f'交易={res["n_trades"]}次')

    plot_period_comparison(all_period_results,
                           os.path.join(IMAGE_DIR, 'comparison_periods.png'))

    # ========== 5. 不同股票对比 ==========
    print('\n[5] 不同股票对比（海龟策略）...')
    stock_list = [
        ('600900.SH', '长江电力', 'cjdl_600900_2025-2026.csv'),
        ('600519.SH', '贵州茅台', '600519_data.csv'),
        ('601318.SH', '中国平安', '601318_data.csv'),
    ]
    stock_results = []
    for ts_code, name, filename in stock_list:
        try:
            df_s = load_stock_data(filename)
        except Exception as e:
            print(f'  {name}: 加载失败 {e}，跳过')
            continue

        cfg = TurtleConfig(
            name=name, stock_name=name, ts_code=ts_code,
            entry_window=20, exit_window=10, atr_period=20,
            risk_per_trade=0.01, max_units=4,
            add_atr_step=0.5, atr_stop_multiplier=2.0
        )
        eng = TurtleBacktestEngine(cfg)
        df_temp = df_s.copy()
        _, res = eng.run(df_temp)
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

    # ========== 5.5 多股票x多参数热力图 ==========
    print('\n[5.5] 多股票x多参数热力图...')
    multi_param_path = os.path.join(DATA_DIR, 'multi_param_results.json')
    if os.path.exists(multi_param_path):
        with open(multi_param_path, 'r', encoding='utf-8') as f:
            multi_results = json.load(f)
        plot_multi_param_heatmap(multi_results,
                                 os.path.join(IMAGE_DIR, 'heatmap_multi_param.png'))
    else:
        print('  未找到 multi_param_results.json，请先运行 test_multi_params.py')

    # ========== 6. 保存结果 ==========
    print('\n[6] 保存回测结果...')
    output = {
        'base': results,
        'periods': all_period_results,
        'stocks': stock_results,
        'trades': [
            {
                'entry_date': t.entry_date.strftime('%Y-%m-%d'),
                'exit_date': t.exit_date.strftime('%Y-%m-%d') if t.exit_date else None,
                'entry_price': round(t.entry_price, 3),
                'exit_price': round(t.exit_price, 3),
                'shares': t.shares,
                'units': t.units,
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
    print('TASK4 海龟策略回测完成！')
    print('=' * 70)


if __name__ == '__main__':
    main()
