# TASK3：策略实战 - 均线交叉策略回测系统

> 林富强 / 北京大学 · 量化交易工作坊 · 第三次作业

## 项目简介

基于均线交叉信号的量化回测系统，覆盖 **入场 → 仓位 → 出场 → 风控** 四大核心模块，支持多标的、多周期、多仓位模式对比分析。

- **策略类型**：均线交叉（MA5/MA15、MA5/MA20）
- **回测标的**：贵州茅台(600519)、中国平安(601318)、长江电力(600900)
- **仓位模式**：固定仓位、ATR 仓位、凯利公式、风险平价
- **出场机制**：止盈出场、止损出场、信号反转出场、时间止损出场
- **风控体系**：单笔止损、日度回撤、组合回撤、极端行情四层防线

---

## 目录结构

```
TASK3/
├── 林富强+TASK3.pdf                 # 最终作业 PDF
├── 林富强+TASK3.docx                # Word 源文件
├── README.md                        # 本说明文件
│
├── code/                            # 代码模块（模块化拆分）
│   ├── __init__.py                  # 包初始化
│   ├── config.py                    # 配置中心：数据类、枚举、路径常量
│   ├── data_loader.py               # 数据加载：CSV / Tushare API 双源
│   ├── indicators.py                # 技术指标：RSI、ATR、均线、波动率
│   ├── entry_rules.py               # 入场规则：金叉信号 + RSI 过滤 + 成交量确认
│   ├── position_manager.py          # 仓位管理：固定/ATR/凯利/风险平价 四种模式
│   ├── exit_rules.py                # 出场规则：止盈/止损/信号反转/时间止损
│   ├── risk_manager.py              # 风险控制：单笔止损 → 日度回撤 → 组合回撤 → 极端行情
│   ├── backtest_engine.py           # 回测引擎：整合四要素执行完整回测
│   ├── plots.py                     # 绘图模块：策略图、回测曲线、回撤图、雷达图等
│   ├── main.py                      # 主入口：运行完整回测流程
│   └── generate_report.py           # 报告生成：生成 Word + PDF 文档
│
├── data/                            # 数据文件
│   ├── 600519_data.csv              # 贵州茅台日线数据
│   ├── 601318_data.csv              # 中国平安日线数据
│   ├── cjdl_600900_2025-2026.csv    # 长江电力日线数据
│   └── backtest_results.json        # 回测结果（JSON 格式）
│
└── images/                          # 图片资源
    ├── comparison_periods.png       # 周期对比图（MA5/15 vs MA5/20）
    ├── comparison_positions.png     # 仓位模式对比图
    ├── comparison_stocks.png        # 标的对比图
    ├── 5_15/                        # MA5/MA15 策略图表
    │   ├── strategy.png             # 策略信号图
    │   ├── backtest.png             # 回测净值曲线
    │   └── drawdown.png             # 回撤分析图
    └── 5_20/                        # MA5/MA20 策略图表
        ├── strategy.png             # 策略信号图
        ├── backtest.png             # 回测净值曲线
        ├── drawdown.png             # 回撤分析图
        ├── metrics_radar.png        # 绩效雷达图
        └── exit_reasons.png         # 出场原因分布图
```

---

## 模块说明

### 核心模块依赖关系

```
main.py
  ├── config.py          ← 全局配置（所有模块共用）
  ├── data_loader.py     ← 加载数据
  ├── indicators.py      ← 计算技术指标
  ├── entry_rules.py     ← 生成入场信号
  ├── position_manager.py ← 计算仓位
  ├── exit_rules.py      ← 检查出场条件
  ├── risk_manager.py    ← 风控检查
  ├── backtest_engine.py ← 整合上述模块执行回测
  └── plots.py           ← 生成可视化图表

generate_report.py
  └── 读取 data/backtest_results.json + images/ → 生成 Word + PDF
```

### 各模块职责

| 模块 | 职责 | 关键类/函数 |
|------|------|-------------|
| `config.py` | 集中管理配置：数据类定义、枚举、路径常量 | `StrategyConfig`, `PositionMode`, `ExitReason` |
| `data_loader.py` | 从 CSV 或 Tushare API 加载股票日线数据 | `load_data()`, `load_from_tushare()` |
| `indicators.py` | 计算技术指标：均线、RSI、ATR、波动率 | `calc_ma()`, `calc_rsi()`, `calc_atr()` |
| `entry_rules.py` | 根据均线金叉 + RSI 过滤 + 成交量确认生成买入信号 | `generate_signals()` |
| `position_manager.py` | 四种仓位模式：固定、ATR、凯利公式、风险平价 | `PositionManager` |
| `exit_rules.py` | 四种出场：止盈、止损、信号反转、时间止损 | `ExitChecker`, `Trade` |
| `risk_manager.py` | 四层风控防线：单笔止损 → 日度回撤 → 组合回撤 → 极端行情 | `RiskManager` |
| `backtest_engine.py` | 整合入场/仓位/出场/风控执行完整回测 | `BacktestEngine` |
| `plots.py` | 所有可视化：策略图、净值曲线、回撤图、雷达图、对比图 | `plot_strategy()`, `plot_backtest()` |
| `main.py` | 程序入口，编排完整回测流程 | `main()` |
| `generate_report.py` | 读取回测结果，生成 Word + PDF 报告 | `generate_report()` |

---

## 快速开始

### 环境依赖

```bash
pip install pandas numpy matplotlib tushare python-docx fpdf2
```

### 运行回测

```bash
cd code
python main.py
```

回测结果保存到 `data/backtest_results.json`，图片保存到 `images/`。

### 生成报告

```bash
cd code
python generate_report.py
```

生成的 `林富强+TASK3.docx` 和 `林富强+TASK3.pdf` 位于 TASK3 根目录。

---

## 重构说明

本次将原始单体文件 `strategy_backtest.py`（1131 行）按职责拆分为 10 个独立模块：

| 重构前 | 重构后 | 说明 |
|--------|--------|------|
| 单体文件 1131 行 | 10 个模块 + 2 个入口 | 每个模块职责单一 |
| 所有逻辑耦合 | 模块间通过 `config.py` 共享配置 | 改一处不影响全局 |
| 难以复用 | 可独立 import 单个模块 | 如 `from entry_rules import generate_signals` |
| 图片散落根目录 | 按 `5_15`/`5_20` 分类 | 对比图单独放根目录 |
| 数据与代码混放 | 独立 `data/` 文件夹 | 干净分离 |
