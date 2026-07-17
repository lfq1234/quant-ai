# quant-ai

量化交易工作坊作业 - 林富强 / 北京大学

## 目录结构

```
quant-ai/
├── TASK1/                    # 量化交易初体验：从零搭建数据引擎
│   ├── 林富强+TASK1.pdf      # 最终作业 PDF
│   ├── 林富强+TASK1.docx     # Word 源文件
│   ├── generate_task1.py     # 文档生成脚本
│   ├── fetch_cjdl.py         # Tushare 数据获取脚本
│   ├── cjdl_600900_2025-2026.csv  # 长江电力日线数据
│   ├── cjdl_close_price.png  # 收盘价曲线图
│   ├── report.html           # 任务三可视化报告
│   └── README.md
├── TASK2/                    # 数据炼金术：数据诊断与构造交易指标
│   ├── 林富强+TASK2.pdf      # 最终作业 PDF
│   ├── 林富强+TASK2.docx     # Word 源文件
│   ├── data_diagnosis.py     # 任务一：数据诊断脚本
│   ├── calculate_indicators.py  # 任务三+四：指标计算与可视化脚本
│   ├── generate_task2.py     # 作业文档生成脚本
│   ├── report.html           # HTML 可视化报告
│   ├── data_with_indicators.csv  # 含全部指标计算结果的完整数据
│   ├── descriptive_stats.csv # 描述性统计量表
│   ├── diagnosis_summary.json   # 数据诊断摘要
│   ├── data_diagnosis.png    # 数据诊断可视化图
│   ├── chart_rsi.png         # RSI 指标图表
│   ├── chart_macd.png        # MACD 指标图表
│   ├── chart_boll.png        # 布林带指标图表
│   ├── chart_kdj.png         # KDJ 指标图表
│   └── conversation_log.md   # 对话记录
├── TASK3/                    # 策略实战：均线交叉策略回测系统
│   ├── 林富强+TASK3.pdf      # 最终作业 PDF
│   ├── 林富强+TASK3.docx     # Word 源文件
│   ├── README.md             # TASK3 说明文件
│   ├── conversation_log.md   # 本次会话记录
│   ├── code/                 # 代码模块（模块化拆分，10个模块）
│   │   ├── config.py         # 配置中心：数据类、枚举、路径常量
│   │   ├── data_loader.py    # 数据加载（CSV / Tushare）
│   │   ├── indicators.py     # 技术指标（RSI、ATR、均线）
│   │   ├── entry_rules.py    # 入场规则（金叉 + RSI + 量能）
│   │   ├── position_manager.py  # 仓位管理（四种模式）
│   │   ├── exit_rules.py     # 出场规则（止盈/止损/信号/时间）
│   │   ├── risk_manager.py   # 风险控制（四层防线）
│   │   ├── backtest_engine.py   # 回测引擎
│   │   ├── plots.py          # 绘图模块
│   │   ├── main.py           # 主入口
│   │   └── generate_report.py   # 报告生成
│   ├── data/                 # 数据文件
│   │   ├── 600519_data.csv   # 贵州茅台日线
│   │   ├── 601318_data.csv   # 中国平安日线
│   │   ├── cjdl_600900_2025-2026.csv  # 长江电力日线
│   │   └── backtest_results.json     # 回测结果
│   └── images/               # 图片资源
│       ├── 5_15/             # MA5/MA15 策略图表（3张）
│       ├── 5_20/             # MA5/MA20 策略图表（5张）
│       └── comparison_*.png  # 对比类图表（3张）
├── TASK4/                    # 海龟交易策略：唐奇安通道突破回测系统
│   ├── 林富强+TASK4.pdf      # 最终作业 PDF
│   ├── 林富强+TASK4.docx     # Word 源文件
│   ├── README.md             # TASK4 说明文件
│   ├── code/                 # 代码模块（15个脚本）
│   │   ├── config.py         # 策略配置：唐奇安通道周期、ATR、止损参数
│   │   ├── data_loader.py    # 数据加载：CSV / Tushare API
│   │   ├── indicators.py     # 唐奇安通道 + ATR 指标计算
│   │   ├── signals.py        # 突破买入 / 跌破卖出信号
│   │   ├── backtest_engine.py   # 回测引擎：ATR 仓位、金字塔加仓、动态止损
│   │   ├── plots.py          # 绘图：信号图、净值曲线、回撤图、热力图等
│   │   ├── main.py           # 主入口：基准回测 + 参数对比 + 多股对比
│   │   ├── test_multi_params.py  # 多股票×多参数 24 组交叉回测
│   │   ├── generate_report.py   # 报告生成：Word + PDF
│   │   └── ...               # 辅助工具脚本
│   ├── data/                 # 数据文件
│   │   ├── 600519_data.csv   # 贵州茅台日线
│   │   ├── 601318_data.csv   # 中国平安日线
│   │   ├── cjdl_600900_2025-2026.csv  # 长江电力日线
│   │   ├── backtest_results.json     # 基准回测结果
│   │   └── multi_param_results.json  # 24 组多参数回测结果
│   └── images/               # 图片资源（共 80 张）
│       ├── 5_3/ ~ 55_20/     # 8 组参数 × 3 只股票 × 3 张图 = 72 张
│       ├── comparison_periods.png  # 参数周期对比图
│       ├── comparison_stocks.png   # 多股对比图
│       └── heatmap_multi_param.png # 超额收益热力图
├── TASK5/                    # AI 交易引擎：机器学习算法与场景应用
│   ├── 林富强+TASK5.pdf      # 最终作业 PDF
│   ├── 林富强+TASK5.docx     # Word 源文件
│   ├── README.md             # TASK5 说明文件
│   ├── spec.md               # 任务规范文档
│   ├── code/                 # 代码模块（5 个包，24 个 .py 文件）
│   │   ├── main.py           # 主入口：双数据集全流程
│   │   ├── generate_report.py   # 报告生成：docx → PDF
│   │   ├── config/           # 配置中心（5 文件）
│   │   │   ├── paths.py / params.py / features.py / style.py
│   │   ├── data_loader/      # 数据加载与特征工程（5 文件）
│   │   │   ├── breast_cancer.py / stock_data.py / split.py / preprocess.py
│   │   ├── models/           # 模型定义与训练（3 文件）
│   │   │   ├── builders.py / trainer.py
│   │   ├── evaluation/       # 模型评估（3 文件）
│   │   │   ├── metrics.py / display.py
│   │   └── visualization/    # 可视化（6 文件）
│   │       ├── _common.py / confusion_matrix.py / roc.py / auc_bar.py / feature_importance.py
│   ├── data/                 # 数据文件
│   │   ├── breast_cancer.csv / stock_returns.csv / ml_results.json
│   └── images/               # 图片资源（共 20 张）
│       ├── breast_cancer_fig1~7_*.png   # 乳腺癌数据集: 7 张
│       └── stock_600900_fig1~7_*.png    # 股票数据集: 7 张
└── README.md
```

## TASK3 重构备注

> 2026-07-11：TASK3 完成代码模块化重构

- **背景**：原始 `strategy_backtest.py` 为 1131 行单体文件，逻辑高度耦合，不利于复用
- **改动**：按职责拆分为 10 个独立模块（config / data_loader / indicators / entry_rules / position_manager / exit_rules / risk_manager / backtest_engine / plots / main）
- **目录整理**：图片按均线周期分类到 `images/5_15/` 和 `images/5_20/`，对比图放 `images/` 根目录；数据统一放 `data/`；代码统一放 `code/`
- **验证**：模块化代码运行结果与原单体文件完全一致，PDF 已重新生成

## TASK4 备注

> 2026-07-11：TASK4 海龟交易策略完成

- **策略**：唐奇安通道突破 + ATR 仓位管理 + 金字塔加仓 + 动态止损
- **测试范围**：8 组参数（5/3 ~ 55/20）× 3 只股票 = 24 组完整回测
- **关键发现**：回测期间 A 股整体下跌，海龟策略三只股票均跑赢买入持有，中国平安超额收益达 +18.40%
- **图表配色**：全部采用中国股市习惯（红涨绿跌），热力图使用 RdYlGn_r 反转色表
- **可视化**：每组参数×股票生成 3 张图（信号图/净值曲线/回撤图），按参数组合建子文件夹，共 80 张图片

## TASK5 备注

> 2026-07-17：TASK5 机器学习分类任务完成

- **任务**：五种分类模型（线性回归/逻辑回归/决策树/随机森林/KNN）在双数据集上的对比实验
- **数据集**：乳腺癌（随机划分）+ 长江电力股票数据（时间顺序划分，不可随机打乱）
- **代码架构**：按数据流方向分包 → `config/` `data_loader/` `models/` `evaluation/` `visualization/`，共 24 个 .py 文件
- **设计原则**：`__init__.py` 只做纯导出，不含业务代码；每个 .py 模块职责单一
- **二次重构（07-17）**：从各包单一 `__init__.py` 拆分为独立模块文件，提高可维护性和可读性
- **关键发现**：
  - 乳腺癌数据集：Random Forest 表现最优，AUC ≈ 0.99
  - 股票数据集：五模型 AUC 均低于 0.5，验证简单技术指标预测短期走势困难
- **输出**：每个数据集 7 张图（4 混淆矩阵 + ROC 曲线 + AUC 柱状图 + 特征重要性），共 14+ 张图
- **验证**：`main.py` 和 `generate_report.py` 均一次跑通，重构前后结果完全一致
