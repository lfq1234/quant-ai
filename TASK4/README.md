# TASK4：海龟交易策略 - 唐奇安通道突破回测系统

> 林富强 / 北京大学 · 量化交易工作坊 · 第四次作业

## 项目简介

基于经典海龟交易法则构建的量化回测系统，核心使用 **唐奇安通道突破** 作为入场信号，配合 **ATR 动态仓位管理**、**金字塔加仓** 和 **ATR 止损** 实现完整交易策略。

- **策略类型**：海龟交易系统（唐奇安通道突破）
- **回测标的**：长江电力(600900)、贵州茅台(600519)、中国平安(601318)
- **参数测试**：8 组入场/出场周期 × 3 只股票 = 24 组完整回测
- **仓位管理**：基于 ATR 的风险百分比仓位 + 金字塔加仓（最多 4 单位）
- **止损机制**：2 倍 ATR 动态止损 + 反向突破出场
- **回测周期**：2025-07-02 ~ 2026-07-02（约 243 个交易日）

---

## 目录结构

```
TASK4/
├── 林富强+TASK4.pdf                    # 最终作业 PDF
├── 林富强+TASK4.docx                   # Word 源文件
├── README.md                           # 本说明文件
│
├── code/                               # 代码模块
│   ├── config.py                       # 配置中心：策略参数、路径常量
│   ├── data_loader.py                  # 数据加载：CSV / Tushare API 双源
│   ├── indicators.py                   # 唐奇安通道 + ATR 指标计算
│   ├── signals.py                      # 突破买入 / 跌破卖出信号生成
│   ├── backtest_engine.py              # 回测引擎：ATR 仓位、金字塔加仓、动态止损
│   ├── plots.py                        # 绘图模块：信号图、净值曲线、回撤图、热力图等
│   ├── main.py                         # 主入口：基准回测 + 参数对比 + 多股对比 + 热力图
│   ├── test_multi_params.py            # 多股票 × 多参数组合测试（24 组 + 图表生成）
│   ├── generate_report.py              # 报告生成：Word + PDF
│   ├── fetch_2yr_data.py               # Tushare 数据获取脚本
│   ├── scan_stocks.py                  # 股票扫描工具
│   ├── check_data.py                   # 数据检查工具
│   ├── check_start.py                  # 起始日期检查
│   ├── check_windows.py                # Windows 兼容性检查
│   └── regen_heatmap.py                # 热力图重新生成工具
│
├── data/                               # 数据文件
│   ├── cjdl_600900_2025-2026.csv       # 长江电力日线数据
│   ├── 600519_data.csv                 # 贵州茅台日线数据
│   ├── 601318_data.csv                 # 中国平安日线数据
│   ├── cjdl_600900_2yr.csv             # 长江电力两年日线数据
│   ├── backtest_results.json           # 基准回测结果（JSON）
│   └── multi_param_results.json        # 24 组多参数回测结果（JSON）
│
└── images/                             # 图片资源（共 80 张）
    ├── comparison_periods.png          # 8 组参数周期对比图
    ├── comparison_stocks.png           # 3 只股票综合对比图
    ├── heatmap_multi_param.png         # 多股票 × 多参数超额收益热力图
    │
    ├── 5_3/                            # 入场 5 日 / 出场 3 日
    │   ├── 长江电力_strategy.png       #   信号图
    │   ├── 长江电力_backtest.png       #   净值曲线
    │   ├── 长江电力_drawdown.png       #   回撤图
    │   ├── 贵州茅台_strategy.png
    │   ├── 贵州茅台_backtest.png
    │   ├── 贵州茅台_drawdown.png
    │   ├── 中国平安_strategy.png
    │   ├── 中国平安_backtest.png
    │   └── 中国平安_drawdown.png
    │
    ├── 5_5/                            # 入场 5 日 / 出场 5 日（同上 9 张）
    ├── 10_5/                           # 入场 10 日 / 出场 5 日（同上 9 张）
    ├── 10_10/                          # 入场 10 日 / 出场 10 日（同上 9 张）
    ├── 15_7/                           # 入场 15 日 / 出场 7 日（同上 9 张）
    ├── 20_10/                          # 入场 20 日 / 出场 10 日（经典系统一）
    │   ├── strategy.png                #   基准策略信号图
    │   ├── backtest.png                #   基准净值曲线
    │   ├── drawdown.png                #   基准回撤图
    │   ├── metrics_radar.png           #   绩效雷达图
    │   ├── exit_reasons.png            #   出场原因饼图
    │   ├── 长江电力_strategy.png       #   + 3 只股票各 3 张
    │   ├── 长江电力_backtest.png
    │   ├── 长江电力_drawdown.png
    │   ├── 贵州茅台_strategy.png
    │   ├── 贵州茅台_backtest.png
    │   ├── 贵州茅台_drawdown.png
    │   ├── 中国平安_strategy.png
    │   ├── 中国平安_backtest.png
    │   └── 中国平安_drawdown.png
    ├── 30_15/                          # 入场 30 日 / 出场 15 日（同上 9 张）
    └── 55_20/                          # 入场 55 日 / 出场 20 日（经典系统二，同上 9 张）
```

---

## 模块说明

### 核心模块依赖关系

```
main.py
  ├── config.py            ← 全局配置（所有模块共用）
  ├── data_loader.py       ← 加载数据
  ├── indicators.py        ← 计算唐奇安通道 + ATR
  ├── signals.py           ← 生成突破买入/跌破卖出信号
  ├── backtest_engine.py   ← 整合信号 + ATR 仓位 + 加仓 + 止损执行回测
  └── plots.py             ← 生成可视化图表

test_multi_params.py
  ├── config.py / data_loader.py / backtest_engine.py / plots.py
  └── 24 组回测 + 每组 3 张图

generate_report.py
  └── 读取 data/*.json + images/ → 生成 Word + PDF
```

### 各模块职责

| 模块 | 职责 | 关键类/函数 |
|------|------|-------------|
| `config.py` | 策略参数配置：通道周期、ATR 周期、风险比例、加仓倍数、止损系数 | `TurtleConfig` |
| `data_loader.py` | 从 CSV 或 Tushare API 加载股票日线数据 | `load_stock_data()` |
| `indicators.py` | 计算唐奇安通道（上轨/下轨）和 ATR | `calc_indicators()` |
| `signals.py` | 基于通道突破生成买入/卖出信号 | `generate_signals()` |
| `backtest_engine.py` | 完整回测引擎：ATR 仓位计算、金字塔加仓、动态止损、净值跟踪 | `TurtleBacktestEngine`, `Trade` |
| `plots.py` | 信号图、净值曲线、回撤图、雷达图、对比图、热力图 | `plot_strategy()`, `plot_backtest()`, `plot_multi_param_heatmap()` |
| `main.py` | 主入口：基准回测 + 8 组参数对比 + 3 股对比 + 热力图 | `main()` |
| `test_multi_params.py` | 24 组多参数交叉回测 + 每组生成 3 张图表 | `main()` |
| `generate_report.py` | 读取回测结果，生成 Word + PDF 报告 | `generate_report()` |

---

## 策略逻辑

### 海龟交易系统核心规则

| 要素 | 规则 | 说明 |
|------|------|------|
| **入场信号** | 收盘价突破 N 日最高价 | 唐奇安通道上轨突破 |
| **出场信号** | 收盘价跌破 M 日最低价 | 唐奇安通道下轨跌破 |
| **仓位计算** | 风险百分比法 | 每笔交易风险 = 总资金 × 1% |
| **仓位单位** | Unit = (资金 × 1%) / (ATR × 合约乘数) | ATR 越大，仓位越小 |
| **金字塔加仓** | 价格每上涨 0.5 × ATR 加仓 1 单位 | 最多加仓 4 单位 |
| **止损** | 入场价 - 2 × ATR | 每次加仓后止损上移 |
| **ATR 周期** | 默认 20 日 | 衡量市场波动率 |

### 测试参数组合

| 编号 | 入场周期 | 出场周期 | 说明 |
|------|----------|----------|------|
| 1 | 5 | 3 | 极短周期，信号最敏感 |
| 2 | 5 | 5 | 短周期对称 |
| 3 | 10 | 5 | 短周期 |
| 4 | 10 | 10 | 短周期对称 |
| 5 | 15 | 7 | 中短周期 |
| 6 | 20 | 10 | 系统一（经典海龟） |
| 7 | 30 | 15 | 中长周期 |
| 8 | 55 | 20 | 系统二（经典海龟） |

---

## 关键回测结果

### 基准策略（长江电力，20/10 参数）

| 指标 | 数值 |
|------|------|
| 总收益率 | -6.20% |
| 年化收益 | -6.95% |
| 买入持有 | -5.87% |
| 最大回撤 | -7.41% |
| 夏普比率 | -1.719 |
| 胜率 | 0.0% |
| 交易次数 | 3 |

### 三只股票最优参数对比

| 股票 | 最优参数 | 策略收益 | 买入持有 | 超额收益 | 最大回撤 | 胜率 |
|------|----------|----------|----------|----------|----------|------|
| 中国平安 | 20/10 | +2.43% | -15.96% | **+18.40%** | -9.23% | 50% |
| 贵州茅台 | 55/20 | -3.88% | -16.26% | **+12.38%** | -6.73% | 0% |
| 长江电力 | 10/5 | -3.10% | -11.58% | **+8.48%** | -6.01% | 50% |

> 回测期间（2025-2026）A 股整体处于下跌趋势，海龟策略通过通道突破 + ATR 止损有效控制了下行风险，三只股票均跑赢买入持有。

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

### 运行多参数交叉测试

```bash
cd code
python test_multi_params.py
```

24 组回测结果保存到 `data/multi_param_results.json`，每组 3 张图表保存到 `images/{参数}/` 子文件夹。

### 生成报告

```bash
cd code
python generate_report.py
```

生成的 `林富强+TASK4.docx` 和 `林富强+TASK4.pdf` 位于 TASK4 根目录。

---

## 可视化说明

所有图表采用 **中国股市配色习惯（红涨绿跌）**：

- **红色**：正收益 / 跑赢买入持有
- **绿色**：负收益 / 跑输买入持有
- 热力图使用 `RdYlGn_r` 反转色表，红色越深表示超额收益越高
- 对比图柱状图按正负值着色，正收益红色、负收益绿色
