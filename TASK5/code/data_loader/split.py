# -*- coding: utf-8 -*-
"""数据划分：乳腺癌（随机划分）、股票（时间顺序划分）"""

import config


def split_breast_cancer(X, y, test_size=None, random_state=None):
    """
    乳腺癌数据集划分：随机划分（非时间序列）
    使用 train_test_split + stratify 保持类别比例
    """
    from sklearn.model_selection import train_test_split
    if test_size is None:
        test_size = config.TEST_SIZE
    if random_state is None:
        random_state = config.RANDOM_STATE

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"[乳腺癌划分] 随机划分 (stratify=y)")
    print(f"  训练集: {len(X_train)}, 测试集: {len(X_test)}")
    return X_train, X_test, y_train, y_test


def split_stock(X, y, test_size=None):
    """
    股票数据集划分：时间顺序划分（不能随机打乱！）
    前 (1-test_size) 训练，后 test_size 测试
    """
    if test_size is None:
        test_size = config.TEST_SIZE

    split_idx = int(len(X) * (1 - test_size))
    X_train = X.iloc[:split_idx].copy()
    X_test = X.iloc[split_idx:].copy()
    y_train = y.iloc[:split_idx].copy()
    y_test = y.iloc[split_idx:].copy()

    print(f"[股票划分] 时间顺序划分 (注意: 不打乱)")
    print(f"  训练集: {len(X_train)} (前 {split_idx} 个交易日)")
    print(f"  测试集: {len(X_test)} (后 {len(X) - split_idx} 个交易日)")
    return X_train, X_test, y_train, y_test
