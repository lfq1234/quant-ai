# -*- coding: utf-8 -*-
"""
多股票 x 多参数组合测试：全面观察海龟策略在不同配置下的表现。
每组（股票×参数）生成策略图、净值曲线、回撤图，按参数组合建子文件夹保存。
"""

import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TurtleConfig, DATA_DIR, IMAGE_DIR
from data_loader import load_stock_data
from backtest_engine import TurtleBacktestEngine
from plots import plot_strategy, plot_backtest, plot_drawdown


def main():
    print('=' * 90)
    print('海龟策略多股票 x 多参数组合测试（含图表生成）')
    print('=' * 90)

    stocks = [
        ('600900.SH', '长江电力', 'cjdl_600900_2025-2026.csv'),
        ('600519.SH', '贵州茅台', '600519_data.csv'),
        ('601318.SH', '中国平安', '601318_data.csv'),
    ]

    param_sets = [
        (5, 3),
        (5, 5),
        (10, 5),
        (10, 10),
        (15, 7),
        (20, 10),
        (30, 15),
        (55, 20),
    ]

    all_results = []

    for ts_code, name, filename in stocks:
        print(f'\n{"=" * 90}')
        print(f'股票: {name} ({ts_code})')
        print(f'{"=" * 90}')

        try:
            df = load_stock_data(filename)
        except Exception as e:
            print(f'  加载失败: {e}')
            continue

        print(f'  数据范围: {df["trade_date"].min().strftime("%Y-%m-%d")} ~ '
              f'{df["trade_date"].max().strftime("%Y-%m-%d")}, {len(df)}个交易日')
        print()

        header = f'{"参数":<10} {"总收益":>8} {"年化":>8} {"买入持有":>8} {"超额":>8} {"MDD":>8} {"夏普":>8} {"胜率":>6} {"盈亏比":>6} {"交易":>4}'
        print(header)
        print('-' * len(header) + '-' * 10)

        for ew, xw in param_sets:
            cfg = TurtleConfig(
                name=f'{name}_{ew}_{xw}',
                stock_name=name,
                ts_code=ts_code,
                entry_window=ew,
                exit_window=xw,
                atr_period=min(ew, 20),
                risk_per_trade=0.01,
                max_units=4,
                add_atr_step=0.5,
                atr_stop_multiplier=2.0
            )
            eng = TurtleBacktestEngine(cfg)
            df_temp = df.copy()
            df_bt, res = eng.run(df_temp)

            all_results.append(res)

            print(f'{ew:>2}/{xw:<2}      '
                  f'{res["total_return"]:>7.2f}% '
                  f'{res["annual_return"]:>7.2f}% '
                  f'{res["buy_hold_return"]:>7.2f}% '
                  f'{res["excess_return"]:>+7.2f}% '
                  f'{res["max_drawdown"]:>7.2f}% '
                  f'{res["sharpe_ratio"]:>7.3f} '
                  f'{res["win_rate"]:>5.1f}% '
                  f'{res["profit_loss_ratio"]:>5.2f} '
                  f'{res["n_trades"]:>4}')

            # ========== 生成图表 ==========
            # 按参数组合建子文件夹：images/5_3/, images/10_5/, ...
            subdir = os.path.join(IMAGE_DIR, f'{ew}_{xw}')
            os.makedirs(subdir, exist_ok=True)

            # 从交易记录提取买卖日期和价格
            buy_dates = [t.entry_date for t in eng.trades]
            buy_prices = [t.entry_price for t in eng.trades]
            sell_dates = [t.exit_date for t in eng.trades if t.exit_date is not None]
            sell_prices = [t.exit_price for t in eng.trades if t.exit_date is not None]

            # 1. 策略信号图
            plot_strategy(
                df_bt, cfg,
                buy_dates, buy_prices,
                sell_dates, sell_prices,
                os.path.join(subdir, f'{name}_strategy.png')
            )

            # 2. 净值曲线图
            plot_backtest(
                df_bt, res,
                os.path.join(subdir, f'{name}_backtest.png')
            )

            # 3. 最大回撤图
            plot_drawdown(
                df_bt, res,
                os.path.join(subdir, f'{name}_drawdown.png')
            )

    # 找出每只股票的最优参数
    print(f'\n{"=" * 90}')
    print('各股票最优参数（按超额收益排序）')
    print(f'{"=" * 90}')

    for ts_code, name, _ in stocks:
        stock_res = [r for r in all_results if r['stock_name'] == name]
        if not stock_res:
            continue
        best = max(stock_res, key=lambda x: x['excess_return'])
        print(f'  {name}: 最优参数 {best["entry_window"]}/{best["exit_window"]}  '
              f'总收益={best["total_return"]:.2f}%, 超额={best["excess_return"]:+.2f}%, '
              f'夏普={best["sharpe_ratio"]:.3f}, 胜率={best["win_rate"]:.1f}%, '
              f'交易={best["n_trades"]}次')

    # 保存完整结果
    output_path = os.path.join(DATA_DIR, 'multi_param_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f'\n完整结果已保存: {output_path}')

    # 统计生成的图片
    total_images = 0
    for ew, xw in param_sets:
        subdir = os.path.join(IMAGE_DIR, f'{ew}_{xw}')
        if os.path.exists(subdir):
            n = len([f for f in os.listdir(subdir) if f.endswith('.png')])
            total_images += n
            print(f'  images/{ew}_{xw}/: {n} 张图片')
    print(f'  总计: {total_images} 张图片')


if __name__ == '__main__':
    main()
