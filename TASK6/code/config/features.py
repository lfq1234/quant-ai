# -*- coding: utf-8 -*-
"""因子工程配置：12 个技术面因子定义"""

# 因子列名（与 factors.py 计算顺序一致）
FEATURE_COLS = [
    'mom_1m', 'mom_3m', 'mom_12m_1m', 'reversal_5d',
    'turn_20d', 'vol_ratio',
    'vol_20d', 'vol_change',
    'ma_bias_20', 'rsi_14', 'bb_pos',
    'ln_market_cap',
]

# 因子分组（用于文档描述）
FACTOR_GROUPS = {
    'momentum': ['mom_1m', 'mom_3m', 'mom_12m_1m', 'reversal_5d'],
    'liquidity': ['turn_20d', 'vol_ratio'],
    'volatility': ['vol_20d', 'vol_change'],
    'technical': ['ma_bias_20', 'rsi_14', 'bb_pos'],
    'size': ['ln_market_cap'],
}
