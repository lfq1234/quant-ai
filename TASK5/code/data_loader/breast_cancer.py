# -*- coding: utf-8 -*-
"""方案 A：sklearn 乳腺癌数据集加载"""

import pandas as pd
from sklearn.datasets import load_breast_cancer


def load_breast_cancer_data():
    """加载 sklearn 乳腺癌数据集，返回 X, y, feature_names"""
    data = load_breast_cancer()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = pd.Series(data.target, name='target')  # 0=恶性, 1=良性
    feature_names = list(data.feature_names)
    print(f"[乳腺癌数据集] 样本数: {len(X)}, 特征数: {len(feature_names)}")
    print(f"  类别分布: {dict(y.value_counts())}")
    return X, y, feature_names
