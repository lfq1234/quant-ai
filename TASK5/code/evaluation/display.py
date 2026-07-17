# -*- coding: utf-8 -*-
"""评估结果展示：混淆矩阵打印、ROC 曲线数据"""

from sklearn.metrics import roc_curve


def print_confusion_matrix(cm, model_name):
    """友好打印混淆矩阵"""
    print(f"\n  [{model_name}] 混淆矩阵:")
    print(f"           预测跌(0)  预测涨(1)")
    print(f"  实际跌(0)   TN={cm[0,0]:>5d}    FP={cm[0,1]:>5d}")
    print(f"  实际涨(1)   FN={cm[1,0]:>5d}    TP={cm[1,1]:>5d}")


def get_roc_data(y_true, y_proba):
    """计算 ROC 曲线数据"""
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)
    return fpr, tpr, thresholds
