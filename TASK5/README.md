# TASK5：AI 交易引擎 — 机器学习算法与场景应用

> **作者**：林富强（北京大学 · 量化交易工作坊）
> **完成时间**：2026-07-17
> **提交物**：`林富强+TASK5.pdf`

---

## 一、任务简介

本任务聚焦**基础分类型机器学习算法**在量化交易中的应用，使用两类数据集对比五种模型：

- **方案 A：乳腺癌数据集**（sklearn 内置）— 通用二分类 baseline，随机划分
- **方案 B：长江电力 (600900.SH) 股票数据** — 金融真实场景，时间顺序划分，不可随机打乱

### 五种模型

| 模型 | 类型 | 特点 |
|------|------|------|
| 线性回归 (Linear Regression) | 回归→分类 | 快速、可解释、baseline |
| 逻辑回归 (Logistic Regression) | 分类 | 输出概率、线性边界 |
| 决策树 (Decision Tree) | 分类 | 高度可解释、易过拟合 |
| 随机森林 (Random Forest) | 集成分类 | 准确率高、特征重要性 |
| KNN (K-Nearest Neighbors) | 分类 | 简单、非线性 |

### 评估指标

混淆矩阵、Accuracy、Precision、Recall、F1 Score、ROC 曲线、AUC。

---

## 二、目录结构

```
TASK5/
├── 林富强+TASK5.pdf              # ★ 最终提交 PDF
├── 林富强+TASK5.docx             # Word 源文件（保留以备修改）
├── README.md                     # 本文档
├── spec.md                       # 任务规范文档（理论+实现方案）
│
├── code/                         # Python 实现（按职责分包拆分）
│   ├── main.py                   # 主入口：一键运行全流程
│   ├── generate_report.py        # 报告生成：docx → PDF
│   │
│   ├── config/                   # 阶段1：配置中心
│   │   ├── __init__.py           # 统一导出
│   │   ├── paths.py              # 路径常量（ROOT_DIR / DATA_DIR / IMAGE_DIR）
│   │   ├── params.py             # 超参数、随机种子、测试集比例
│   │   ├── features.py           # 特征工程参数（MA / RSI / 动量等）
│   │   └── style.py              # A 股配色、模型颜色、字体设置
│   │
│   ├── data_loader/              # 阶段2：数据加载与特征工程
│   │   ├── __init__.py           # 统一导出
│   │   ├── breast_cancer.py      # 乳腺癌数据集加载
│   │   ├── stock_data.py         # 股票数据加载 + RSI 计算
│   │   ├── split.py              # 数据划分（随机 / 时间顺序）
│   │   └── preprocess.py         # StandardScaler 标准化
│   │
│   ├── models/                   # 阶段3：模型定义与训练
│   │   ├── __init__.py           # 统一导出
│   │   ├── builders.py           # 五模型实例化
│   │   └── trainer.py            # 训练与预测（含线性回归阈值处理）
│   │
│   ├── evaluation/               # 阶段4：模型评估
│   │   ├── __init__.py           # 统一导出
│   │   ├── metrics.py            # 指标计算（CM/Acc/Precision/Recall/F1/AUC）
│   │   └── display.py            # 混淆矩阵打印 + ROC 数据提取
│   │
│   └── visualization/            # 阶段5：可视化
│       ├── __init__.py           # 触发 matplotlib 配置 + 统一导出
│       ├── _common.py            # matplotlib 中文设置 + 共享颜色常量
│       ├── confusion_matrix.py   # 混淆矩阵热力图
│       ├── roc.py                # ROC 曲线对比图
│       ├── auc_bar.py            # AUC 柱状图
│       └── feature_importance.py # 随机森林特征重要性图
│
├── data/                         # 数据文件
│   ├── breast_cancer.csv         # sklearn 乳腺癌数据集导出
│   ├── stock_returns.csv         # 股票特征 + 标签
│   └── ml_results.json           # 模型评估结果
│
└── images/                       # 生成的图表（共 20 张）
    ├── breast_cancer_fig1_cm_dt.png ~ breast_cancer_fig7_feature_imp.png  # 乳腺癌: 7 张/数据集
    └── stock_600900_fig1_cm_dt.png ~ stock_600900_fig7_feature_imp.png    # 股票: 7 张/数据集
```

---

## 三、设计原则

### 3.1 代码架构

- **分包管理**：`config/` → `data_loader/` → `models/` → `evaluation/` → `visualization/`，按数据流方向组织
- **`__init__.py` 只做导出**：不含业务代码，纯 `from .xxx import yyy` 统一暴露接口
- **模块职责单一**：每个 `.py` 只负责一个明确功能，如 `split.py` 只管划分、`preprocess.py` 只管标准化
- **包内引用**：同级模块通过 `from . import xxx` 引用，不产生循环依赖

### 3.2 数据划分策略

| 数据集 | 划分方式 | 原因 |
|--------|----------|------|
| 乳腺癌 | `train_test_split` 随机划分（80/20） | 非时间序列，可随机 |
| 长江电力 | 时间顺序划分（前 80% 训练，后 20% 测试） | 时间序列，**严禁随机打乱**（防止未来函数） |

### 3.3 可视化配色

遵循 A 股"红涨绿跌"习惯：

| 含义 | 颜色 | 色值 |
|------|------|------|
| 涨/正收益 | 红色 | `#C0392B` |
| 跌/负收益 | 绿色 | `#27AE60` |
| 模型颜色 | 各模型固定配色 | 区分于 `style.py` |

matplotlib 中文字体：`SimHei`（黑体），`axes.unicode_minus=False`。

### 3.4 输出图表

每个数据集生成 **7 张图**：

| 标号 | 图名 | 内容 |
|------|------|------|
| fig1 | 混淆矩阵-决策树 | Decision Tree 混淆矩阵热力图 |
| fig2 | 混淆矩阵-随机森林 | Random Forest 混淆矩阵热力图 |
| fig3 | 混淆矩阵-线性回归 | Linear Regression 混淆矩阵热力图 |
| fig4 | 混淆矩阵-KNN | KNN 混淆矩阵热力图 |
| fig5 | ROC 曲线对比 | 五模型 ROC 曲线 + AUC 值 |
| fig6 | AUC 柱状图 | 五模型 AUC 横向柱状图对比 |
| fig7 | 特征重要性 | 随机森林 Top-N 特征重要性 |

两个数据集共 **14 张图**（加上报告生成过程中的图共 20 张）。

---

## 四、运行方式

### 4.1 环境要求

```text
python>=3.8
scikit-learn>=1.3
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
python-docx>=1.1
docx2pdf>=0.1.8
```

### 4.2 运行全流程

```bash
cd TASK5/code
python main.py
```

将依次执行：
1. 方案 A：乳腺癌数据集全流程（加载→划分→训练→评估→7 图）
2. 方案 B：长江电力股票全流程（加载→划分→训练→评估→7 图）
3. 保存评估结果至 `data/ml_results.json`

### 4.3 生成报告

```bash
cd TASK5/code
python generate_report.py
```

生成 `林富强+TASK5.docx` 并通过 `docx2pdf` 转为 `林富强+TASK5.pdf`（格式：宋体/五号/1.5倍行距/0段间距/两端对齐）。

---

## 五、关键实验结果

| 数据集 | 最优模型 | AUC | 关键发现 |
|--------|----------|-----|----------|
| 乳腺癌 | Random Forest | ≈0.99 | 医学数据特征强，RF 表现优异 |
| 长江电力 | — | <0.5 | 简单技术指标对次日涨跌预测力有限，无模型 AUC 超过 0.5 |

> **教学意义**：股票数据结果不佳并非失败，恰恰验证了技术指标预测短期走势的困难性，引出有效市场假说和量化交易中 ML 应用的现实挑战。

---

## 六、代码重构记录

> 2026-07-16：初版完成，代码集中在各 `__init__.py`
>
> 2026-07-17：**二次重构** — 将每个包从单一 `__init__.py` 拆分为职责独立的 `.py` 模块文件
> - `config/` → `paths.py` + `params.py` + `features.py` + `style.py`
> - `data_loader/` → `breast_cancer.py` + `stock_data.py` + `split.py` + `preprocess.py`
> - `models/` → `builders.py` + `trainer.py`
> - `evaluation/` → `metrics.py` + `display.py`
> - `visualization/` → `_common.py` + 4 个绘图模块
> - 所有 `__init__.py` 改为纯导出，不含业务逻辑
> - 验证：`main.py` 和 `generate_report.py` 均一次跑通，结果与重构前完全一致
