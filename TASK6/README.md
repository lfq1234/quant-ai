# TASK6：智能决策者 — 机器学习定制专属策略

> **作者**：林富强（北京大学 · 量化交易工作坊）
> **完成时间**：2026-07-17
> **提交物**：`林富强TASK6.pdf`

---

## 一、任务简介

本任务聚焦**机器学习截面选股策略**，从 TASK5 的"单股时序预测"升级到"全市场截面排序选股"：

- **股票池**：自选 100 只 A 股（沪深两市，行业分散，Tushare 积分友好）
- **时间区间**：2015-2024 年（训练集 2015-2020，测试集 2021-2024）
- **策略逻辑**：每个季度末用 ML 模型预测下季度收益率 → 选 Top-30 持仓 → 季度调仓
- **对比基准**：100 只股票等权组合

### 四种模型

| 模型 | 类型 | 特点 |
|------|------|------|
| 线性回归 (Linear Regression) | 回归 | 快速、可解释、baseline |
| 决策树 (Decision Tree) | 树模型 | 高度可解释、易过拟合 |
| 随机森林 (Random Forest) | 集成学习 | 降低方差、特征重要性 |
| XGBoost | 梯度提升 | 正则化、高精度、进阶 |

### 评估指标

年化收益、年化波动、Sharpe Ratio、最大回撤、季度胜率、胜基准率、IC / Rank IC。

---

## 二、目录结构

```
TASK6/
├── 林富强TASK6.pdf                # ★ 最终提交 PDF
├── 林富强TASK6.docx               # Word 源文件（保留以备修改）
├── README.md                      # 本文档
├── spec.md                        # 任务规范文档（理论+实现方案）
│
├── code/                          # Python 实现（按职责分包拆分）
│   ├── main.py                    # 主入口：一键运行全流程
│   ├── build_report.py            # 报告生成：docx → PDF
│   │
│   ├── config/                    # 配置中心
│   │   ├── __init__.py            # 统一导出
│   │   ├── paths.py               # 路径常量
│   │   ├── params.py              # 超参数、随机种子、时间区间
│   │   ├── features.py            # 因子列名定义
│   │   └── style.py               # A 股配色、模型颜色
│   │
│   ├── data_loader/               # 数据加载与因子工程
│   │   ├── __init__.py            # 统一导出
│   │   ├── universe.py            # 100 只股票池定义
│   │   ├── tushare_api.py         # Tushare 日线数据下载
│   │   ├── factors.py             # 12 个技术因子计算
│   │   ├── panel.py               # 截面面板构建 + 标准化
│   │   └── split.py               # 时间顺序划分训练/测试集
│   │
│   ├── models/                    # 模型定义与训练
│   │   ├── __init__.py            # 统一导出
│   │   ├── builders.py            # 四模型实例化
│   │   └── trainer.py             # 训练与预测
│   │
│   ├── strategy/                  # 交易策略
│   │   ├── __init__.py            # 统一导出
│   │   ├── portfolio.py           # Top-N 选股组合构建
│   │   ├── backtest.py            # 季度调仓回测引擎
│   │   └── benchmark.py           # 等权基准计算
│   │
│   ├── evaluation/                # 评估指标
│   │   ├── __init__.py            # 统一导出
│   │   ├── metrics.py             # 收益/风险/IC 指标计算
│   │   └── display.py             # 结果打印
│   │
│   └── visualization/             # 可视化
│       ├── __init__.py            # matplotlib 配置 + 统一导出
│       ├── _common.py             # 中文字体 + 共享常量
│       ├── cumulative_return.py   # 累计净值曲线
│       ├── drawdown.py            # 回撤曲线
│       ├── quarterly_return_bar.py # 季度收益柱状图
│       ├── model_comparison.py    # 模型对比柱状图
│       ├── ic_curve.py            # IC 时序曲线
│       ├── feature_importance.py  # 特征重要性（RF）
│       └── bonus_comparison.py    # 附加题：持仓数敏感性
│
├── data/                          # 数据文件
│   ├── raw_daily/                 # 100 只股票原始日线 CSV
│   ├── panel_with_factors.csv     # 因子面板（含标签）
│   └── backtest_results.json      # 回测结果
│
└── images/                        # 生成的图表（共 8 张）
    ├── fig1_cumulative_return.png      # 累计净值曲线
    ├── fig2_drawdown.png               # 回撤曲线
    ├── fig3_quarterly_return.png       # 季度收益柱状图
    ├── fig4_model_comparison.png       # 模型对比柱状图
    ├── fig5_ic_curve.png               # IC 时序曲线
    ├── fig6_feature_importance.png     # RF 特征重要性
    ├── fig7_xgb_feature_importance.png # XGBoost 特征重要性
    └── fig8_bonus_n_sensitivity.png    # 附加题：N 敏感性
```

---

## 三、设计原则

### 3.1 代码架构

- **分包管理**：`config/` → `data_loader/` → `models/` → `strategy/` → `evaluation/` → `visualization/`，按数据流方向组织
- **`__init__.py` 只做导出**：不含业务代码，纯 `from .xxx import yyy` 统一暴露接口
- **模块职责单一**：每个 `.py` 只负责一个明确功能
- **包内引用**：同级模块通过 `from . import xxx` 引用，不产生循环依赖

### 3.2 因子体系

| 因子类别 | 因子名称 | 计算方式 |
|----------|----------|----------|
| 动量类 | mom_1m / mom_3m / mom_6m / mom_12m | 过去 N 月收益率 |
| 均线类 | ma_ratio_5 / ma_ratio_20 / ma_ratio_60 | 收盘价 / 移动均线 |
| 波动类 | vol_1m / vol_3m | 日收益率标准差（年化） |
| 流动性 | turnover_1m / turnover_3m | 成交额 / 流通市值 |
| 技术指标 | rsi_14 | 14 日 RSI |

共 **12 个因子**，每个季度末截面对全部 100 只股票计算。

### 3.3 数据划分策略

| 用途 | 时间 | 季度数 | 说明 |
|------|------|--------|------|
| 训练集 | 2015-2020 | 24 | 模型学习历史规律 |
| 测试集 | 2021-2024 | 16 | 样本外验证 |

**严格按时间顺序划分**，不可随机打乱（防止未来函数）。

### 3.4 可视化配色

遵循 A 股"红涨绿跌"习惯：

| 含义 | 颜色 | 色值 |
|------|------|------|
| 涨/正收益 | 红色 | `#C0392B` |
| 跌/负收益 | 绿色 | `#27AE60` |
| 模型颜色 | 各模型固定配色 | 区分于 `style.py` |

matplotlib 中文字体：`SimHei`（黑体），`axes.unicode_minus=False`。

---

## 四、运行方式

### 4.1 环境要求

```text
python>=3.8
scikit-learn>=1.3
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
xgboost>=2.0
scipy>=1.10
python-docx>=1.1
docx2pdf>=0.1.8
tushare>=1.2
```

### 4.2 运行全流程

```bash
cd TASK6/code
python main.py
```

将依次执行：
1. 下载 100 只股票日线数据（Tushare Pro）
2. 计算 12 个技术因子，构建截面面板
3. 按时间顺序划分训练集 / 测试集
4. 训练 LR / DT / RF / XGBoost 四模型
5. 基于模型预测做 Top-30 季度调仓回测
6. 计算收益、风险、IC 等核心指标
7. 生成 8 张图表
8. 附加题：N=10/30/50/100 持仓数敏感性分析

### 4.3 生成报告

```bash
cd TASK6/code
python build_report.py
```

生成 `林富强TASK6.docx` 并通过 `docx2pdf` 转为 `林富强TASK6.pdf`（格式：宋体/五号/1.5倍行距/0段间距/两端对齐）。

---

## 五、关键实验结果

| 模型 | 年化收益 | 年化波动 | Sharpe | 最大回撤 | 季胜率 | 胜基准率 |
|------|----------|----------|--------|----------|--------|----------|
| Linear Regression | -3.83% | 17.16% | -0.22 | -22.77% | 46.67% | 26.67% |
| Decision Tree | 2.40% | 17.31% | 0.14 | -16.92% | 46.67% | 33.33% |
| Random Forest | -1.30% | 19.44% | -0.07 | -20.45% | 46.67% | 33.33% |
| **XGBoost** | **3.10%** | 18.50% | **0.17** | **-16.61%** | **53.33%** | **53.33%** |
| 等权基准 | 2.25% | — | — | — | — | — |

**核心发现**：
- XGBoost 是唯一跑赢等权基准的模型（年化 3.10% vs 2.25%），且在最大回撤和胜率上均表现最优
- Decision Tree 微幅超越基准，说明即使单棵树也能捕捉部分截面规律
- Linear Regression 表现最差，线性假设在 A 股截面收益预测中明显不足
- XGBoost 的 IC 为 +0.013，是四模型中唯一正 IC

### 附加题：持仓数敏感性（N = 10 / 30 / 50 / 100）

| N | 年化收益 | 最大回撤 | Sharpe | 特征 |
|---|----------|----------|--------|------|
| 10 | 最高 | 最大 | 中 | 集中度高，收益弹性大但风险高 |
| 30 | 中高 | 中 | 最优 | 收益风险平衡点 |
| 50 | 中 | 较小 | 中 | 分散度提升，收益略降 |
| 100 | 最低 | 最小 | 低 | 接近市场平均，alpha 被稀释 |

---

## 六、技术踩坑记录

| 问题 | 解决方案 |
|------|----------|
| Tushare `adj_factor` API 限流（1次/分钟） | 改用 `pct_chg` 累积构建后复权价格，跳过 adj_factor 调用 |
| pandas 新版 `fillna(method='ffill')` 废弃 | 改用 `.ffill()` |
| 截面因子含 NaN 导致模型训练失败 | panel 构建阶段 `fillna(0)` + `dropna(subset=['next_return'])` |
| IC 计算空记录报错 | 增加 `len(ic_df) == 0` 判空处理 |
