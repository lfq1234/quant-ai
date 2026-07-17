# -*- coding: utf-8 -*-
"""模型构建：实例化四个回归模型"""

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

import config


def build_models():
    """构建四个回归模型，返回 {name: model} 字典"""
    p = config.MODEL_PARAMS
    models = {
        'Linear Regression': LinearRegression(**p['Linear Regression']),
        'Decision Tree': DecisionTreeRegressor(**p['Decision Tree']),
        'Random Forest': RandomForestRegressor(**p['Random Forest']),
    }
    # XGBoost（可能未安装）
    try:
        from xgboost import XGBRegressor
        models['XGBoost'] = XGBRegressor(**p['XGBoost'])
    except ImportError:
        print('  [Warning] xgboost not installed, skipping XGBoost')
    return models
