# -*- coding: utf-8 -*-
"""
TASK5 主入口
AI 交易引擎：机器学习算法与场景应用

流程：
  方案 A：乳腺癌数据集（通用二分类 baseline）
    1. 加载数据 → 2. 随机划分 → 3. 标准化 → 4. 训练五模型 → 5. 评估 → 6. 画图

  方案 B：长江电力股票数据（金融场景，时间序列划分）
    1. 加载数据+特征工程 → 2. 时间顺序划分 → 3. 标准化 → 4. 训练五模型 → 5. 评估 → 6. 画图

五种模型：线性回归、逻辑回归、决策树、随机森林、KNN
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# 确保能 import 同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data_loader import (
    load_breast_cancer_data,
    load_stock_data,
    split_breast_cancer,
    split_stock,
    standardize,
)
from models import build_models, train_and_predict
from evaluation import evaluate_all, print_confusion_matrix, get_roc_data
from visualization import (
    plot_confusion_matrix,
    plot_roc_curves,
    plot_auc_bar,
    plot_feature_importance,
)


def run_dataset(dataset_name, X, y, feature_names, split_func, split_kwargs,
                y_test_extra=None):
    """
    通用流程：对一个数据集执行完整的 加载→划分→训练→评估→画图 流程。

    Args:
        dataset_name: 数据集名称（用于日志和文件名前缀）
        X, y, feature_names: 数据和特征名
        split_func: 划分函数
        split_kwargs: 划分函数的参数
        y_test_extra: 额外信息（如日期），仅用于日志

    Returns:
        summary_df: 评估指标汇总
        results: 模型结果字典
    """
    print(f"\n{'=' * 60}")
    print(f"  数据集：{dataset_name}")
    print(f"{'=' * 60}")

    # --- 1. 数据划分 ---
    print(f"\n[1/5] 数据划分")
    X_train, X_test, y_train, y_test = split_func(X, y, **split_kwargs)

    # --- 2. 特征标准化 ---
    print(f"\n[2/5] 特征标准化")
    X_train_s, X_test_s, scaler = standardize(X_train, X_test)
    print(f"  StandardScaler: fit on train ({len(X_train_s)}), transform on test ({len(X_test_s)})")

    # --- 3. 模型训练 ---
    print(f"\n[3/5] 模型训练")
    models = build_models()
    results = train_and_predict(models, X_train_s, X_test_s, y_train)

    # --- 4. 模型评估 ---
    print(f"\n[4/5] 模型评估")
    summary_df, results = evaluate_all(results, y_test)

    # 打印混淆矩阵
    for name, res in results.items():
        print_confusion_matrix(res['metrics']['cm'], name)

    # 打印汇总表
    print(f"\n  指标汇总:")
    print(summary_df.to_string(index=False))

    # --- 5. 画图 ---
    print(f"\n[5/5] 生成图表")
    img_prefix = dataset_name.lower().replace(' ', '_')

    # 图1: 决策树混淆矩阵
    plot_confusion_matrix(
        results['Decision Tree']['metrics']['cm'],
        'Decision Tree',
        os.path.join(config.IMAGE_DIR, f'{img_prefix}_fig1_cm_dt.png'),
        dataset_name
    )

    # 图2: 随机森林混淆矩阵
    plot_confusion_matrix(
        results['Random Forest']['metrics']['cm'],
        'Random Forest',
        os.path.join(config.IMAGE_DIR, f'{img_prefix}_fig2_cm_rf.png'),
        dataset_name
    )

    # 图3: 线性回归混淆矩阵
    plot_confusion_matrix(
        results['Linear Regression']['metrics']['cm'],
        'Linear Regression',
        os.path.join(config.IMAGE_DIR, f'{img_prefix}_fig3_cm_lr.png'),
        dataset_name
    )

    # 图4: KNN 混淆矩阵
    plot_confusion_matrix(
        results['KNN']['metrics']['cm'],
        'KNN',
        os.path.join(config.IMAGE_DIR, f'{img_prefix}_fig4_cm_knn.png'),
        dataset_name
    )

    # 图5: ROC 曲线对比
    plot_roc_curves(
        results, y_test,
        os.path.join(config.IMAGE_DIR, f'{img_prefix}_fig5_roc.png'),
        dataset_name
    )

    # 图6: AUC 柱状图
    plot_auc_bar(
        summary_df,
        os.path.join(config.IMAGE_DIR, f'{img_prefix}_fig6_auc_bar.png'),
        dataset_name
    )

    # 图7: 随机森林特征重要性
    plot_feature_importance(
        results['Random Forest']['model'],
        feature_names,
        os.path.join(config.IMAGE_DIR, f'{img_prefix}_fig7_feature_imp.png'),
        top_n=min(10, len(feature_names)),
        model_name='Random Forest'
    )

    return summary_df, results


def main():
    print("=" * 60)
    print("  TASK5: AI 交易引擎 — 机器学习算法与场景应用")
    print("  作者: 林富强")
    print("=" * 60)

    # 确保图片目录存在
    os.makedirs(config.IMAGE_DIR, exist_ok=True)

    all_summaries = {}

    # ==================== 方案 A：乳腺癌数据集 ====================
    print("\n>>> 方案 A：乳腺癌数据集（通用二分类 baseline）")
    X_cancer, y_cancer, feat_cancer = load_breast_cancer_data()

    summary_cancer, results_cancer = run_dataset(
        'Breast Cancer',
        X_cancer, y_cancer, feat_cancer,
        split_func=split_breast_cancer,
        split_kwargs={'test_size': config.TEST_SIZE, 'random_state': config.RANDOM_STATE},
    )
    all_summaries['breast_cancer'] = summary_cancer.to_dict('records')

    # ==================== 方案 B：股票数据集 ====================
    print("\n>>> 方案 B：长江电力股票数据（金融场景）")
    X_stock, y_stock, feat_stock, dates = load_stock_data()

    summary_stock, results_stock = run_dataset(
        'Stock_600900',
        X_stock, y_stock, feat_stock,
        split_func=split_stock,
        split_kwargs={'test_size': config.TEST_SIZE},
    )
    all_summaries['stock'] = summary_stock.to_dict('records')

    # ==================== 保存结果 ====================
    results_path = os.path.join(config.DATA_DIR, 'ml_results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(all_summaries, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 评估结果已保存: {results_path}")

    # ==================== 最终汇总 ====================
    print("\n" + "=" * 60)
    print("  最终汇总")
    print("=" * 60)

    print("\n【乳腺癌数据集】")
    print(summary_cancer.to_string(index=False))

    print("\n【股票数据集（长江电力）】")
    print(summary_stock.to_string(index=False))

    print(f"\n[TASK5] 全流程完成！")
    print(f"  图表目录: {config.IMAGE_DIR}")
    print(f"  结果文件: {results_path}")


if __name__ == '__main__':
    main()
