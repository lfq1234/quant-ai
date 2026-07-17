# -*- coding: utf-8 -*-
"""特征标准化：StandardScaler"""

import pandas as pd
from sklearn.preprocessing import StandardScaler


def standardize(X_train, X_test):
    """StandardScaler: fit on train, transform on test"""
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns, index=X_test.index)
    return X_train_scaled, X_test_scaled, scaler
