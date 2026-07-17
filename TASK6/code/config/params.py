# -*- coding: utf-8 -*-
"""模型超参数、时间划分、组合参数"""

# 全局随机种子
RANDOM_STATE = 42

# 时间划分：训练集 < TRAIN_END_YEAR，测试集 >= TRAIN_END_YEAR
TRAIN_END_YEAR = 2021  # 训练 2015-2020，测试 2021-2024

# 策略参数
TOP_N = 30            # 每季度选 Top-N 只股票
COST_PER_TRADE = 0.002  # 单边交易成本 0.2%

# 季度末日期（月日），用于截面调仓
QUARTER_END_DATES = ['0331', '0630', '0930', '1231']

# 四个回归模型超参数
MODEL_PARAMS = {
    'Linear Regression': {},
    'Decision Tree': {
        'max_depth': 5,
        'min_samples_leaf': 50,
        'random_state': RANDOM_STATE,
    },
    'Random Forest': {
        'n_estimators': 100,
        'max_depth': 8,
        'min_samples_leaf': 30,
        'random_state': RANDOM_STATE,
        'n_jobs': -1,
    },
    'XGBoost': {
        'n_estimators': 200,
        'max_depth': 6,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'random_state': RANDOM_STATE,
        'n_jobs': -1,
    },
}
