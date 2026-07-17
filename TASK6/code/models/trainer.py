# -*- coding: utf-8 -*-
"""模型训练与预测：统一接口 fit / predict"""

import config


def train_and_predict(models, train_df, test_df):
    """
    训练所有模型，返回结果字典。

    每个模型用训练集因子 fit，在测试集上 predict（预测下季度收益）。

    Returns:
        results: {name: {'model':, 'test_pred': DataFrame[ts_code, quarter_str, pred, actual]}}
    """
    X_train = train_df[config.FEATURE_COLS]
    y_train = train_df['next_return']

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)

        # 在测试集上预测
        X_test = test_df[config.FEATURE_COLS]
        y_pred = model.predict(X_test)

        pred_df = test_df[['quarter_str', 'ts_code']].copy()
        pred_df['pred'] = y_pred
        pred_df['actual'] = test_df['next_return'].values

        results[name] = {'model': model, 'pred_df': pred_df}
        print(f'  [{name}] trained, test predictions: {len(pred_df)} rows')

    return results
