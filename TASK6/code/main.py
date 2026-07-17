# -*- coding: utf-8 -*-
"""
TASK6 主入口
智能决策者：机器学习定制专属策略

流程：
  1. 下载数据（100 只 A 股日线，缓存到 CSV）
  2. 构建截面面板（季度因子 + 下季度收益）
  3. 时间顺序划分训练/测试集
  4. 训练四模型（LR / DT / RF / XGBoost）
  5. 季度调仓回测（Top-30 等权）
  6. 业绩评估（年化收益 / Sharpe / 回撤 / IC）
  7. 绘制图表（8 张）
  8. 附加题：持仓数敏感性（N=10/30/50/100）
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data_loader import download_all, build_panel, split_panel
from models import build_models, train_and_predict
from strategy import backtest_all_models, calc_benchmark
from evaluation import evaluate_all_models, print_metrics_table
from visualization import (
    plot_feature_importance,
    plot_cumulative_return,
    plot_drawdown,
    plot_quarterly_return,
    plot_ic_curve,
    plot_model_comparison,
    plot_bonus_comparison,
)


def main():
    print('=' * 60)
    print('  TASK6: Smart Decision Maker -- ML Custom Strategy')
    print('  Author: Lin Fuqiang (Peking University)')
    print('=' * 60)

    os.makedirs(config.IMAGES_DIR, exist_ok=True)
    os.makedirs(config.RAW_DIR, exist_ok=True)

    # === 1. Download data ===
    print('\n[1/8] Downloading daily data...')
    download_all()

    # === 2. Build panel ===
    print('\n[2/8] Building cross-sectional panel...')
    panel = build_panel()
    panel.to_csv(str(config.PANEL_FILE), index=False, encoding='utf-8-sig')
    print(f'  Panel saved: {len(panel)} rows')

    # === 3. Split ===
    print('\n[3/8] Splitting train/test (time-ordered)...')
    train_df, test_df = split_panel(panel)

    # === 4. Train models ===
    print('\n[4/8] Training models...')
    models = build_models()
    results = train_and_predict(models, train_df, test_df)

    # === 5. Benchmark ===
    print('\n[5/8] Calculating benchmark...')
    bench_df = calc_benchmark(test_df)

    # === 6. Backtest ===
    print('\n[6/8] Running quarterly backtest...')
    all_returns = backtest_all_models(results)

    # === 7. Evaluate ===
    print('\n[7/8] Evaluating performance...')
    summary, ic_dict = evaluate_all_models(all_returns, bench_df, results)
    print_metrics_table(summary)

    # Print IC summary
    for name, ic_df in ic_dict.items():
        print(f'  [{name}] Mean IC={ic_df["ic"].mean():.4f}, '
              f'Mean Rank IC={ic_df["rank_ic"].mean():.4f}')

    # === 8. Visualize ===
    print('\n[8/8] Generating charts...')
    img = config.IMAGES_DIR

    # Fig 1: Cumulative return
    plot_cumulative_return(
        {k: v for k, v in all_returns.items() if not k.startswith('_')},
        bench_df,
        os.path.join(img, 'fig1_cumulative_return.png'),
    )

    # Fig 2: Drawdown
    plot_drawdown(
        {k: v for k, v in all_returns.items() if not k.startswith('_')},
        os.path.join(img, 'fig2_drawdown.png'),
    )

    # Fig 3: Quarterly return bar (RF)
    plot_quarterly_return(
        {k: v for k, v in all_returns.items() if not k.startswith('_')},
        bench_df,
        os.path.join(img, 'fig3_quarterly_return.png'),
        model_name='Random Forest',
    )

    # Fig 4: Model comparison
    plot_model_comparison(summary, os.path.join(img, 'fig4_model_comparison.png'))

    # Fig 5: IC curve (RF)
    plot_ic_curve(ic_dict, os.path.join(img, 'fig5_ic_curve.png'), 'Random Forest')

    # Fig 6: Feature importance (RF)
    plot_feature_importance(
        results['Random Forest']['model'],
        os.path.join(img, 'fig6_feature_importance.png'),
        'Random Forest',
    )

    # Fig 7: Feature importance (XGBoost)
    if 'XGBoost' in results:
        plot_feature_importance(
            results['XGBoost']['model'],
            os.path.join(img, 'fig7_xgb_feature_importance.png'),
            'XGBoost',
        )

    # Fig 8: Bonus - N sensitivity
    if '_bonus_N_sensitivity' in all_returns:
        plot_bonus_comparison(
            all_returns['_bonus_N_sensitivity'],
            bench_df,
            os.path.join(img, 'fig8_bonus_n_sensitivity.png'),
        )

    # === Save results ===
    results_path = str(config.RESULTS_FILE)
    save_data = {
        'summary': summary.to_dict('records'),
        'ic_summary': {name: {'mean_ic': float(ic_df['ic'].mean()),
                              'mean_rank_ic': float(ic_df['rank_ic'].mean())}
                       for name, ic_df in ic_dict.items()},
    }
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
    print(f'\n[OK] Results saved: {results_path}')

    # === Final summary ===
    print('\n' + '=' * 60)
    print('  TASK6 Complete!')
    print('=' * 60)
    print(f'  Images: {config.IMAGES_DIR}')
    print(f'  Data:   {config.DATA_DIR}')
    print(f'\n  Performance Summary:')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
