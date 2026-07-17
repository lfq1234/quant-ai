# -*- coding: utf-8 -*-
"""TASK6 可视化模块 -- 统一导出（导入时自动配置 matplotlib 中文）"""

from . import _common  # noqa: F401 -- 触发 matplotlib 中文设置
from .feature_importance import plot_feature_importance
from .cumulative_return import plot_cumulative_return
from .drawdown import plot_drawdown
from .quarterly_return_bar import plot_quarterly_return
from .ic_curve import plot_ic_curve
from .model_comparison import plot_model_comparison
from .bonus_comparison import plot_bonus_comparison
