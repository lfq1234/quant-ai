# -*- coding: utf-8 -*-
"""模型超参数、随机种子、数据划分比例"""

# 全局随机种子
RANDOM_STATE = 42

# 数据划分
TEST_SIZE = 0.2  # 测试集占比

# 模型超参数
MODEL_PARAMS = {
    'Linear Regression': {},
    'Logistic Regression': {
        'max_iter': 1000,
        'random_state': RANDOM_STATE,
    },
    'Decision Tree': {
        'max_depth': 5,
        'random_state': RANDOM_STATE,
    },
    'Random Forest': {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': RANDOM_STATE,
        'n_jobs': -1,
    },
    'KNN': {
        'n_neighbors': 5,
    },
}
