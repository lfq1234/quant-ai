# -*- coding: utf-8 -*-
"""模型构建：实例化五种分类模型"""

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

import config


def build_models():
    """构建五个分类模型，返回 {name: model} 字典"""
    models = {
        'Linear Regression': LinearRegression(**config.MODEL_PARAMS['Linear Regression']),
        'Logistic Regression': LogisticRegression(**config.MODEL_PARAMS['Logistic Regression']),
        'Decision Tree': DecisionTreeClassifier(**config.MODEL_PARAMS['Decision Tree']),
        'Random Forest': RandomForestClassifier(**config.MODEL_PARAMS['Random Forest']),
        'KNN': KNeighborsClassifier(**config.MODEL_PARAMS['KNN']),
    }
    return models
