# -*- coding: utf-8 -*-
"""模型评估指标：混淆矩阵、Accuracy/Precision/Recall/F1、AUC"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


def evaluate_model(y_true, y_pred, y_proba):
    """
    计算单个模型的全部评估指标。

    Returns:
        dict: {cm, accuracy, precision, recall, f1, auc}
    """
    cm = confusion_matrix(y_true, y_pred)
    auc = roc_auc_score(y_true, y_proba)

    metrics = {
        'cm': cm,
        'TN': cm[0, 0],
        'FP': cm[0, 1],
        'FN': cm[1, 0],
        'TP': cm[1, 1],
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'auc': auc,
    }
    return metrics


def evaluate_all(results, y_test):
    """
    评估所有模型，返回汇总 DataFrame 和带指标的 results。

    Returns:
        summary_df: DataFrame, 每行一个模型
        results: 更新后的 results（每个模型加入 'metrics'）
    """
    rows = []
    for name, res in results.items():
        m = evaluate_model(y_test, res['y_pred'], res['y_proba'])
        res['metrics'] = m
        rows.append({
            '模型': name,
            'Accuracy': m['accuracy'],
            'Precision': m['precision'],
            'Recall': m['recall'],
            'F1': m['f1'],
            'AUC': m['auc'],
            'TP': m['TP'],
            'TN': m['TN'],
            'FP': m['FP'],
            'FN': m['FN'],
        })

    summary_df = pd.DataFrame(rows)
    # 数值保留 4 位小数
    float_cols = ['Accuracy', 'Precision', 'Recall', 'F1', 'AUC']
    summary_df[float_cols] = summary_df[float_cols].round(4)

    return summary_df, results
