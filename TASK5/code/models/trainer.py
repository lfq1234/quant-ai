# -*- coding: utf-8 -*-
"""模型训练与预测：统一接口 fit / predict / predict_proba"""

import numpy as np


def train_and_predict(models, X_train, X_test, y_train):
    """
    训练所有模型，返回结果字典。

    对于 LinearRegression（回归模型用于分类）：
      - predict 输出连续值，以 0.5 为阈值判定类别
      - 将连续预测值 clip 到 [0, 1] 作为概率/评分

    Returns:
        results: {name: {'model':, 'y_pred':, 'y_proba':,}}
    """
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)

        if name == 'Linear Regression':
            # 回归模型：输出连续值，阈值 0.5 做分类
            y_pred_raw = model.predict(X_test)
            y_pred = (y_pred_raw >= 0.5).astype(int)
            # clip 到 [0,1] 作为评分用于 ROC/AUC
            y_proba = np.clip(y_pred_raw, 0, 1)
        else:
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

        results[name] = {
            'model': model,
            'y_pred': y_pred,
            'y_proba': y_proba,
        }
        print(f"  [{name}] 训练完成，预测评分范围: [{y_proba.min():.4f}, {y_proba.max():.4f}]")
    return results
