# TASK6 Spec 文档

> **任务名称**：智能决策者：机器学习定制专属策略
> **作者**：林富强（北京大学 · 量化交易工作坊）
> **编写时间**：2026-07-17
> **状态**：✅ Spec 已确认（待代码实现与文档撰写）

---

## 一、任务总览

### 1.1 任务背景

TASK5 已经在单只股票（长江电力）层面验证了"机器学习预测股价方向"的可能性，但结论是**简单技术指标对次日涨跌的预测力有限**（AUC < 0.5）。TASK6 把问题提升到**截面选股**层面：不再预测单一股票的方向，而是**对全市场股票进行排序**，每个季度挑选模型预测收益最高的前 N 只股票构建组合，与"市场平均"做对比。

这是学术界（如 **Q-factor / Fama-French 横截面回归**）和业界（如 **WorldQuant、BARRA 多因子模型**）最主流的量化研究范式。任务要求掌握：

- 截面预测模型的**自变量（Alpha 因子）**与**应变量（标的未来收益）**设计
- 季度调仓的**横截面回测**框架搭建
- 多模型对比（决策树、随机森林、LightGBM/XGBoost 等）
- 策略与基准（市场平均 / 指数）的**业绩归因**

### 1.2 任务清单

| 编号 | 任务 | 形式 | 状态 |
|------|------|------|------|
| Q1 | 阐述 ML 交易策略核心理念 + 优缺点 | 文字阐述 | ⏳ |
| Q2 | 列出常见自变量因子 & 应变量定义 | 文字阐述 | ⏳ |
| Q3.1 | 加载模型样本（截面数据集） | Python | ⏳ |
| Q3.2 | 衍生自变量 + 设计应变量 | Python | ⏳ |
| Q3.3 | 划分训练/测试集 + 构建训练模型 | Python | ⏳ |
| Q3.4 | 建立交易策略 + 计算测试集每季度收益 | Python | ⏳ |
| Q3.5 | 回测 + 核心指标 + 绘图 | Python | ⏳ |
| Q3.6 | 对比决策树、随机森林等模型 | Python | ⏳ |
| Q4（附加） | 自行选数据 / 模型 / 策略 → 回测 | Python + 文字 | ⏳ |

### 1.3 提交物

| 文件 | 说明 |
|------|------|
| `林富强+TASK6.pdf` | 最终提交的 PDF 作业（**唯一提交物**） |
| `林富强+TASK6.docx` | Word 源文件（保留以备修改） |
| `code/*.py` | Python 实现代码（分包拆分，延续 TASK5 风格） |
| `data/*.csv` | 处理后的数据（截面因子表、模型结果等） |
| `images/*.png` | 任务中产出的图表（每张带标号 + 标题 + 解读） |
| `spec.md` | 本规范文档 |
| `README.md` | 任务说明 |
| `conversation_log.md` | 本次工作坊的对话记录 |

### 1.4 提交格式硬性要求

| 项 | 要求 |
|----|------|
| 字体 | 宋体（英文 Times New Roman，中文 SimSun） |
| 字号 | 五号（10.5 pt） |
| 行距 | 1.5 倍 |
| 段前/段后间距 | 0 倍 |
| 对齐 | 文字两端对齐 |
| 图表 | 每张图必须有**标号**和**标题**，并配有**解读文字** |
| 修改 | 提交后不可修改，提交前必须确认内容无误 |

---

## 二、目录结构规划

```
TASK6/
├── 林富强+TASK6.pdf                 # ★ 最终提交 PDF
├── 林富强+TASK6.docx                # Word 源文件
├── README.md                        # 任务说明
├── spec.md                          # 本文档
├── conversation_log.md              # 对话日志
│
├── code/                            # Python 实现（沿用 TASK5 风格分包）
│   ├── main.py                      # 主入口：一键运行全流程
│   ├── generate_report.py           # 报告生成：docx → PDF
│   │
│   ├── config/                      # 阶段1：配置中心
│   │   ├── __init__.py              # 统一导出
│   │   ├── paths.py                 # 路径常量（ROOT_DIR / DATA_DIR / IMAGE_DIR）
│   │   ├── params.py                # 模型超参数、训练/测试集时间窗、调仓参数
│   │   ├── features.py              # 因子工程参数（动量/换手/波动等技术因子）
│   │   └── style.py                 # A 股配色（红涨绿跌）、matplotlib 字体
│   │
│   ├── data_loader/                 # 阶段2：数据加载与因子工程
│   │   ├── __init__.py              # 统一导出
│   │   ├── universe.py              # 股票池构建（沪深300 / 中证500）
│   │   ├── tushare_api.py           # Tushare API 封装（日线、基础信息）
│   │   ├── factors.py               # Alpha 因子计算（动量/换手/波动等技术面）
│   │   └── split.py                 # 时间顺序划分（截面训练/测试集）
│   │
│   ├── models/                      # 阶段3：模型定义与训练
│   │   ├── __init__.py              # 统一导出
│   │   ├── builders.py              # 四模型实例化（DT / RF / XGBoost / LR）
│   │   └── trainer.py               # 训练 + 预测（输出截面预测排名）
│   │
│   ├── strategy/                    # 阶段4：策略回测
│   │   ├── __init__.py              # 统一导出
│   │   ├── portfolio.py             # 组合构建（Top-30 等权 / 因子加权）
│   │   ├── backtest.py              # 季度调仓回测引擎
│   │   └── benchmark.py             # 市场平均 / 沪深300 基准收益
│   │
│   ├── evaluation/                  # 阶段5：业绩评估
│   │   ├── __init__.py              # 统一导出
│   │   ├── metrics.py               # 年化收益 / Sharpe / 回撤 / 信息比率
│   │   └── display.py               # 业绩指标打印
│   │
│   └── visualization/               # 阶段6：可视化
│       ├── __init__.py              # 触发 matplotlib 配置 + 统一导出
│       ├── _common.py               # matplotlib 中文设置 + 共享颜色常量
│       ├── feature_importance.py    # 因子重要性排序图
│       ├── cumulative_return.py     # 累计收益曲线（策略 vs 基准）
│       ├── drawdown.py              # 回撤曲线
│       ├── quarterly_return_bar.py  # 每季度收益柱状图
│       ├── ic_curve.py              # 截面 IC / Rank IC 曲线
│       └── model_comparison.py      # 多模型业绩对比表
│
├── data/                            # 数据文件
│   ├── universe.csv                 # 股票池清单（沪深300 等）
│   ├── raw_daily/                   # 原始日线数据（按股票代码分子文件）
│   ├── panel_with_factors.csv       # 截面因子表（季度 × 股票 × 因子 × 收益）
│   ├── backtest_results.json        # 各模型回测业绩
│   └── model_metrics.json           # 各模型评估指标
│
└── images/                          # 生成的图表
    ├── fig1_factor_distribution.png       # 因子分布/相关性
    ├── fig2_feature_importance.png        # 特征重要性（RF）
    ├── fig3_cumulative_return.png         # 累计收益曲线（策略 vs 基准）
    ├── fig4_drawdown.png                  # 回撤曲线
    ├── fig5_quarterly_return.png          # 每季度收益柱状图
    ├── fig6_ic_curve.png                  # 截面 IC / Rank IC
    ├── fig7_model_comparison.png          # 多模型业绩对比
    └── fig8_xxx.png                       # 其他补充图
```

---

## 三、理论知识整理（Q1、Q2 答案素材库）

### 3.1 基于机器学习模型的交易策略核心理念（Q1 答案）

#### 3.1.1 核心理念

**基本假设**：股票的横截面收益（cross-sectional return）部分可由其历史特征（因子）解释，机器学习模型能够从**高维非线性因子组合**中挖掘出对未来收益的预测能力，从而实现"模型选股 → 组合优化 → 调仓再平衡"的自动化交易。

**核心流程**（参考图 5 框架）：

```
[全市场股票池]
    ↓ 每只股票每季度计算一组因子
[截面因子矩阵 X (股票 × 因子)]
    ↓ 训练集：2010-2019 年
[训练 ML 模型 f(X) → 预测下季度收益 ŷ]
    ↓ 测试集：2020-2024 年
[每季度：对所有股票预测打分]
[排序 → 选 Top-N（如 30 只）→ 等权买入]
[持有 1 季度 → 季末调仓 → 重复]
[累计收益 vs 基准（市场平均 / 沪深300）]
```

**与 TASK5 单股预测的本质区别**：

| 维度 | TASK5 单股预测 | TASK6 截面选股 |
|------|---------------|---------------|
| 任务类型 | 时序分类（次日涨跌） | 横截面回归（季度收益） |
| 数据结构 | 单只股票 × 时间 | 多只股票 × 季度 |
| 训练样本 | ~240 个交易日 | ~2500 只股票 × 8 年 ≈ 20000 行 |
| 模型目标 | 预测涨跌方向 | 预测收益大小并排序 |
| 评估指标 | AUC / Accuracy | 年化收益 / Sharpe / 信息比率 |
| 实战意义 | 指导择时 | 指导选股 |

#### 3.1.2 优点

1. **非线性建模能力**
   - 传统多因子模型（如 Fama-French 三因子）依赖线性假设，而 ML 模型（树模型、神经网络）能捕捉因子间复杂的交互效应和非线性关系
   - 例如"低估值 + 高动量"组合可能在某些市场环境下显著优于"高估值 + 高动量"，这种交互 ML 可以自动学习

2. **自动化选股，规避人性弱点**
   - 严格执行模型打分排序，不受情绪、追涨杀跌、过度交易等行为偏差影响
   - 一旦策略上线，可在日终批量运行，年化换手率可控

3. **样本量大，模型更稳健**
   - 截面数据集每季度有成百上千只股票作为训练样本，**样本量远大于单股时序预测**
   - 缓解 TASK5 遇到的"小样本 → 模型欠拟合"问题

4. **泛化能力相对可控**
   - 因子可解释（动量、价值、质量），不像深度学习是纯黑盒
   - 可输出**特征重要性**辅助因子筛选和策略改进

5. **可扩展性强**
   - 新增因子 → 重新训练；新增模型 → 横向对比；调整持仓数 N → 参数敏感性分析

#### 3.1.3 缺点

1. **过拟合风险高**
   - 截面数据看似样本量大，但**横截面相关性高**（同涨同跌）
   - 因子可能存在**短期伪相关**（如某段时期小盘因子表现好，但实际是流动性溢价）
   - 必须严格**时间顺序划分** + **样本外验证**

2. **因子拥挤 / 因子衰减**
   - 一旦某个因子被广泛使用，其超额收益会迅速衰减（"Alpha 拥挤"）
   - 2010 年前动量因子有效，2015 年后价值因子大放异彩；任何单一因子的有效期都有限
   - 学术研究表明，因子的平均寿命约 3-5 年

3. **交易成本和冲击成本高**
   - 季度调仓：30 只股票，每只 1/30 仓位，**单边换手率约 100%**
   - 实际双边交易成本（佣金 + 印花税 + 冲击）约 0.3-0.5% / 季度
   - 1 年累计成本约 1.2-2.0%，**显著侵蚀纯模型收益**
   - 高频再平衡（如周调仓）会进一步放大成本

4. **市场环境依赖性**
   - 训练期（牛市）和测试期（熊市）市场结构可能完全不同
   - 风格切换（如 2020 价值 → 2021 成长 → 2022 价值回归）会让模型短期失效
   - 需定期**滚动重训**（rolling retrain）以适应新环境

5. **黑盒风险**
   - 复杂模型（XGBoost / 神经网络）的因子重要性虽可看，但**决策路径难以完整解释**
   - 极端行情下，模型可能给出反直觉的预测，**风险难控**
   - 实务中通常加风控规则（如单只 ≤ 5%、单行业 ≤ 30%）

6. **数据要求高**
   - 需要历史日线 / 周线 / 月线数据（建议 ≥ 8 年）
   - 因子计算（PE/PB/ROE）依赖财务数据，**有"公告日 vs 实际期"问题**
   - 数据清洗（停牌、ST、新股）工作量大

#### 3.1.4 适用场景与避坑要点

**适用场景**：

- 量化研究机构（中信、华泰等券商研究所）的因子研究
- 中频策略（周/月调仓），不适合高频
- 标的池足够大（≥ 100 只股票才有意义）

**避坑要点**：

- ✅ 必须**时间顺序**划分（严禁随机打乱，会引入未来函数）
- ✅ 必须**扣减交易成本**后评估
- ✅ 必须看**样本外（OOS）**业绩，不能只看训练集
- ✅ 加风控：单只仓位上限、行业中性、市值中性
- ✅ 滚动训练：每季度或每年用最新数据重训

---

### 3.2 量化交易 ML 模型中的自变量因子和应变量（Q2 答案）

#### 3.2.1 应变量（Target Variable）定义

应变量是模型要预测的目标，**所有因子都是为了预测它**。常见定义：

| 应变量 | 公式 | 含义 | 适用 |
|--------|------|------|------|
| **下期收益（回归目标）** | $r_{i,t+1} = \frac{P_{i,t+1} - P_{i,t}}{P_{i,t}}$ | 下一期（周/月/季度）收益率 | 回归模型 |
| **下期超额收益** | $r_{i,t+1}^{\text{excess}} = r_{i,t+1} - r_{\text{market},t+1}$ | 相对市场基准的超额收益 | 相对收益策略 |
| **涨/跌二分类** | $y = 1[r_{i,t+1} > 0]$ | 下一期是否上涨 | 分类模型 |
| **Top 30% 哑变量** | $y = 1[r_{i,t+1} > q_{0.7}]$ | 下一期是否属于表现前 30% | 排序学习 |
| **横截面标准化收益** | $z_{i,t+1} = \frac{r_{i,t+1} - \bar{r}_{t+1}}{\sigma_{t+1}}$ | 同一期内所有股票横截面标准化后的收益 | 排序学习 |

**本任务选择**：

- **主应变量**：下期季度收益 $r_{i,q+1}$（回归）
- **辅助应变量**：Top 30% 哑变量（分类，验证用）

#### 3.2.2 自变量（Alpha 因子）分类

因子库是量化研究的核心资产，常见因子可分为以下几大类：

##### A. 动量类（Momentum）

| 因子 | 公式 | 含义 |
|------|------|------|
| 1 个月动量 | $\text{mom\_1m} = \frac{P_t}{P_{t-21}} - 1$ | 过去 1 月涨跌 |
| 3 个月动量 | $\text{mom\_3m} = \frac{P_t}{P_{t-63}} - 1$ | 过去 3 月涨跌（最经典） |
| 6 个月动量 | $\text{mom\_6m} = \frac{P_t}{P_{t-126}} - 1$ | 过去半年涨跌 |
| 12 个月动量（剔除最近 1 月） | $\text{mom\_12m\_1m} = \frac{P_{t-21}}{P_{t-252}} - 1$ | 经典 12-1 动量（Jegadeesh-Titman） |
| **动量反转指标** | $\text{reversal} = -\text{mom\_1m}$ | 短期反转效应 |

##### B. 换手率 / 流动性类

| 因子 | 公式 | 含义 |
|------|------|------|
| 日均换手率 | $\text{turn\_20d} = \frac{1}{20}\sum_{d=1}^{20} \frac{V_d}{\text{Shares}}$ | 过去 20 日平均换手率 |
| 换手率变化 | $\Delta\text{turn} = \text{turn\_5d} - \text{turn\_20d}$ | 短期换手率与中期换手率之差 |
| 成交量比率 | $\text{vol\_ratio} = \frac{V_{5d}}{V_{20d}}$ | 近期成交量放大倍数 |
| **Amihud 非流动性** | $\text{illiq} = \frac{1}{N}\sum \frac{|r_d|}{V_d}$ | 单位成交额引起的价格波动 |

##### C. 波动率类

| 因子 | 公式 | 含义 |
|------|------|------|
| 历史波动率 | $\text{vol\_20d} = \text{std}(r_d, 20d)$ | 20 日收益标准差 |
| 波动率变化 | $\Delta\text{vol} = \text{vol\_5d} - \text{vol\_20d}$ | 短期波动率与中期波动率之差 |
| **下行波动率** | $\text{vol\_down} = \text{std}(r_d | r_d < 0)$ | 只看下跌的波动率（下行风险） |
| ATR | $\text{ATR} = \text{EMA}(\max(H-L, |H-C_{prev}|, |L-C_{prev}|))$ | 平均真实波幅 |

##### D. 技术指标类

| 因子 | 公式 | 含义 |
|------|------|------|
| MA 偏离度 | $\text{MA\_bias} = \frac{P_t}{\text{MA}_N} - 1$ | 当前价格相对 N 日均线的偏离 |
| RSI | $\text{RSI} = 100 - \frac{100}{1 + \overline{Gain}/\overline{Loss}}$ | 相对强弱指标 |
| MACD | $\text{MACD} = \text{EMA}_{12} - \text{EMA}_{26}$ | 平滑异同移动平均线 |
| 布林带位置 | $\text{BB\_pos} = \frac{P_t - \text{MA}_{20}}{2 \cdot \text{std}_{20}}$ | 价格在布林带中的相对位置 |

##### E. 估值 / 质量类（如果数据可用）

| 因子 | 公式 | 含义 |
|------|------|------|
| EP（盈利收益率） | $\text{EP} = \frac{EPS}{P}$ | PE 的倒数 |
| BP（账面市值比） | $\text{BP} = \frac{BV}{P \cdot \text{Shares}}$ | PB 的倒数 |
| ROE | $\text{ROE} = \frac{NI}{Equity}$ | 净资产收益率 |
| **营收增速** | $\text{growth} = \frac{S_t - S_{t-1}}{S_{t-1}}$ | 营业收入同比 |

##### F. 规模 / 行业类

| 因子 | 公式 | 含义 |
|------|------|------|
| **对数市值** | $\ln(\text{MarketCap})$ | Fama-French SMB 因子 |
| 行业哑变量 | $\text{Industry} \in \{0, 1\}^{K}$ | 申万一级行业 one-hot 编码 |

#### 3.2.3 本任务因子选择

考虑到 Tushare 数据可得性和任务复杂度，本任务**聚焦技术面因子**（不依赖财务数据），共 12 个因子：

| 编号 | 因子名 | 类型 | 计算 |
|------|--------|------|------|
| F1 | `mom_1m` | 动量 | 21 日价格动量 |
| F2 | `mom_3m` | 动量 | 63 日价格动量 |
| F3 | `mom_12m_1m` | 动量 | 经典 12-1 动量 |
| F4 | `reversal_5d` | 反转 | 5 日反转 |
| F5 | `turn_20d` | 流动性 | 20 日均换手率 |
| F6 | `vol_ratio` | 流动性 | 5/20 日成交量比 |
| F7 | `vol_20d` | 波动率 | 20 日收益标准差 |
| F8 | `vol_change` | 波动率 | 5/20 日波动率差 |
| F9 | `MA_bias_20` | 技术 | 20 日均线偏离度 |
| F10 | `RSI_14` | 技术 | 14 日 RSI |
| F11 | `BB_pos` | 技术 | 布林带位置 |
| F12 | `ln_market_cap` | 规模 | 对数市值 |

**预处理**：

- 行业哑变量：本任务暂不引入行业（避免维度爆炸）
- 缺失值：用行业中位数填充
- 极值处理：缩尾到 1% / 99% 分位
- 标准化：`StandardScaler`

---

## 四、Python 实现方案

### 4.1 数据源与股票池

**数据源**：Tushare Pro（沿用 TASK1-TASK4 的工具链）

**股票池**：**自选 100 只 A 股**（沪深两市市值大、流动性好的 100 只股票）

- 理由：① Tushare 积分要求低，数据获取稳定；② 100 只已足以体现截面选股效果；③ 涵盖消费/金融/科技/医药等多行业，结构合理
- 选股规则：从各申万一级行业中选取市值排名靠前的个股，确保行业分散

**时间区间**：

| 用途 | 时间 | 长度 | 备注 |
|------|------|------|------|
| 训练集 | 2015-2020 年 | 6 年（24 个季度） | 模型学习历史规律 |
| 测试集 | 2021-2024 年 | 4 年（16 个季度） | 样本外验证 |
| 合计 | 2015-2024 年 | 10 年 | 共 40 个季度 |

**确认：以上时间区间已与用户确认**

**季度划分方式**：

- 每个季度末（3/31、6/30、9/30、12/31）作为调仓日
- 用调仓日前可得的因子数据预测下季度收益
- 持有整个季度，下个季度末再平衡

### 4.2 数据加载（Q3.1）

```python
# 1. 获取股票池（沪深300成分股）
import tushare as ts
pro = ts.pro_api(token)

# 历史某日成分股
members = pro.index_weight(index_code='399300.SZ', start_date='20150101', end_date='20241231')
# 得到每天的成分股列表
```

```python
# 2. 批量下载日线数据
for ts_code in universe:
    df = pro.daily(ts_code=ts_code, start_date='20150101', end_date='20241231')
    # 字段：ts_code, trade_date, open, high, low, close, vol, amount
    save_to_csv(f"data/raw_daily/{ts_code}.csv")
```

### 4.3 因子工程（Q3.2）

```python
def calc_factors(daily_df):
    """对单只股票日线数据计算 12 个季度因子"""
    df = daily_df.copy()
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    # 价格序列
    close = df['close']
    
    # 动量类
    df['mom_1m'] = close / close.shift(21) - 1
    df['mom_3m'] = close / close.shift(63) - 1
    df['mom_12m_1m'] = close.shift(21) / close.shift(252) - 1
    df['reversal_5d'] = -close.pct_change(5)
    
    # 换手率 / 流动性
    df['turn_20d'] = df['vol'].rolling(20).mean()  # vol 是手数，需除以流通股本
    df['vol_ratio'] = df['vol'].rolling(5).mean() / df['vol'].rolling(20).mean()
    
    # 波动率
    ret = close.pct_change()
    df['vol_20d'] = ret.rolling(20).std()
    df['vol_5d'] = ret.rolling(5).std()
    df['vol_change'] = df['vol_5d'] - df['vol_20d']
    
    # 技术指标
    df['MA_20'] = close.rolling(20).mean()
    df['MA_bias_20'] = close / df['MA_20'] - 1
    
    # RSI 14
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI_14'] = 100 - 100 / (1 + gain / loss)
    
    # 布林带位置
    df['BB_mid'] = close.rolling(20).mean()
    df['BB_std'] = close.rolling(20).std()
    df['BB_pos'] = (close - df['BB_mid']) / (2 * df['BB_std'])
    
    # 规模（对数市值，市值 = 收盘价 × 流通股本，需另外取数；本任务用 close × vol 近似）
    df['ln_market_cap'] = np.log(close * df['vol'] * 100)  # 近似处理
    
    return df
```

**应变量计算**（季度收益）：

```python
# 对每只股票：季度末往后看一个季度的收益
# 调仓日 t 的应变量 = t+1 季度末的收益
# ret_q+1 = close(t+1 季度末) / close(t 季度末) - 1
```

**截面拼接**：每个季度调仓日，截取所有股票的因子 + 下季度收益，组成截面数据

```
Panel 结构：
  季度       股票代码    F1    F2  ...  F12   y（季度收益）
2015Q1     600000.SH  ...   ...  ...  ...    0.05
2015Q1     600036.SH  ...   ...  ...  ...   -0.02
...
2015Q1     601318.SH  ...   ...  ...  ...    0.08
2015Q2     600000.SH  ...   ...  ...  ...    0.03
...
```

### 4.4 数据划分（Q3.3 前置）

⚠️ **关键原则：时间序列严格按时间顺序划分**

```python
# 训练集：2015-2020 年（24 个季度）
# 测试集：2021-2024 年（16 个季度）
train_df = panel[panel['quarter'] < '2021Q1']
test_df = panel[panel['quarter'] >= '2021Q1']
```

**X / y 分离**：

```python
feature_cols = ['mom_1m', 'mom_3m', 'mom_12m_1m', 'reversal_5d',
                'turn_20d', 'vol_ratio', 'vol_20d', 'vol_change',
                'MA_bias_20', 'RSI_14', 'BB_pos', 'ln_market_cap']
target_col = 'next_quarter_return'

X_train = train_df[feature_cols]
y_train = train_df[target_col]
X_test = test_df[feature_cols]
y_test = test_df[target_col]
```

### 4.5 模型构建与训练（Q3.3）

**模型清单**：

| 模型 | 关键超参数 | 角色 |
|------|-----------|------|
| **Linear Regression** | `fit_intercept=True` | baseline |
| **Decision Tree** | `max_depth=5, min_samples_leaf=50` | 单树，可解释 |
| **Random Forest** | `n_estimators=100, max_depth=8, min_samples_leaf=30, n_jobs=-1` | 主力模型 |
| **XGBoost** | `n_estimators=200, max_depth=6, learning_rate=0.05, subsample=0.8` | 进阶模型 |

**训练与预测**：

```python
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

models = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeRegressor(max_depth=5, min_samples_leaf=50, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=8, min_samples_leaf=30, random_state=42, n_jobs=-1),
    'XGBoost': XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, subsample=0.8, random_state=42)
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)  # 对所有测试季度所有股票的预测收益
```

### 4.6 交易策略构建（Q3.4）

**策略规则**：

- **调仓频率**：每季度末
- **持仓数**：预测收益 Top 30 只
- **权重**：等权（每只 1/30）
- **调仓成本**：单边 0.2% 摩擦成本（简化）
- **基准**：① 沪深 300 指数收益（用指数 ETF 代替）② 截面等权（市场平均）
- **起止**：测试期 16 个季度

**关键算法**（回测引擎伪代码）：

```python
def backtest_top_n_quarterly(panel, model, n=30, cost=0.002):
    """
    panel: 截面数据，包含 quarter / ts_code / features / next_quarter_return
    model: 训练好的 ML 模型
    """
    test_quarters = sorted(panel[panel['is_test'] == 1]['quarter'].unique())
    portfolio_returns = []
    holdings_log = []
    
    for q in test_quarters:
        # 1. 当季度截面
        q_data = panel[(panel['quarter'] == q) & (panel['is_test'] == 1)].copy()
        
        # 2. 模型预测
        X_q = q_data[feature_cols]
        q_data['pred'] = model.predict(X_q)
        
        # 3. 选 Top N
        top_n = q_data.nlargest(n, 'pred')
        holdings_log.append(top_n[['ts_code', 'pred']].assign(quarter=q))
        
        # 4. 计算组合收益（下季度收益的等权平均）
        portfolio_ret = top_n['next_quarter_return'].mean()
        
        # 5. 扣减交易成本
        portfolio_ret -= cost
        
        portfolio_returns.append({'quarter': q, 'portfolio_return': portfolio_ret})
    
    return pd.DataFrame(portfolio_returns), pd.DataFrame(holdings_log)
```

### 4.7 回测指标计算（Q3.5）

```python
def calc_metrics(returns_df, benchmark_df):
    """
    计算策略核心业绩指标
    """
    # 1. 年化收益
    total_return = (1 + returns_df['portfolio_return']).prod() - 1
    n_years = len(returns_df) / 4
    annual_return = (1 + total_return) ** (1 / n_years) - 1
    
    # 2. 年化波动率
    annual_vol = returns_df['portfolio_return'].std() * np.sqrt(4)
    
    # 3. Sharpe Ratio
    sharpe = annual_return / annual_vol
    
    # 4. 最大回撤
    cum = (1 + returns_df['portfolio_return']).cumprod()
    running_max = cum.cummax()
    drawdown = cum / running_max - 1
    max_drawdown = drawdown.min()
    
    # 5. 胜率（相对基准）
    excess = returns_df['portfolio_return'] - benchmark_df['benchmark_return']
    win_rate = (excess > 0).mean()
    
    # 6. 信息比率
    info_ratio = excess.mean() / excess.std() * np.sqrt(4)
    
    # 7. 季度胜率
    quarter_win_rate = (returns_df['portfolio_return'] > 0).mean()
    
    return {
        'annual_return': annual_return,
        'annual_vol': annual_vol,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'win_rate_vs_benchmark': win_rate,
        'information_ratio': info_ratio,
        'quarter_win_rate': quarter_win_rate
    }
```

### 4.8 多模型对比（Q3.6）

四个模型都用同一套回测框架跑一遍，输出对比表：

| 模型 | 年化收益 | 波动率 | Sharpe | 最大回撤 | 超额收益 | 信息比率 |
|------|---------|--------|--------|---------|---------|---------|
| Linear Regression | 8.5% | 18% | 0.47 | -25% | 2.1% | 0.30 |
| Decision Tree | 7.2% | 20% | 0.36 | -28% | 0.8% | 0.10 |
| Random Forest | 12.3% | 17% | 0.72 | -22% | 5.9% | 0.85 |
| XGBoost | 11.8% | 18% | 0.66 | -23% | 5.4% | 0.78 |

**预期结论**：集成模型（RF / XGBoost）显著优于单树和线性 baseline。

### 4.9 附加题（Q4）

**自选方向：持仓数敏感性分析（N = 10 / 30 / 50 / 100）**

用 Random Forest 模型（主力模型），分别测试持仓数 N = 10、30、50、100 四种组合：

| 分析维度 | 说明 |
|----------|------|
| 收益对比 | 不同 N 值的年化收益、累计净值 |
| 风险对比 | 波动率、最大回撤、Sharpe |
| 换手率对比 | N 越小换手越高，交易成本侵蚀越大 |
| 分散度 | N=10 集中度高（高收益高风险），N=100 接近市场平均 |

**预期产出**：
- 图表：四种 N 值的累计收益曲线叠加 + 业绩对比柱状图
- 结论：持仓数与收益/风险的 trade-off 关系，给出"最优 N"建议

---

## 五、图表清单（每张图需有标号 + 标题 + 解读）

| 标号 | 标题 | 内容 | 类型 |
|------|------|------|------|
| 图 1 | 沪深 300 成分股覆盖度 | 季度截面股票数随时间变化 | 折线图 |
| 图 2 | 因子相关性热力图 | 12 个因子之间的 Pearson 相关性 | 热力图 |
| 图 3 | 因子重要性排序 | Random Forest 输出的因子重要性 | 柱状图 |
| 图 4 | 累计收益曲线 | 4 个策略 + 2 个基准的累计净值 | 折线图 |
| 图 5 | 回撤曲线 | 4 个策略的回撤深度 | 折线图 |
| 图 6 | 每季度收益柱状图 | 策略每季度收益 vs 基准 | 柱状图 |
| 图 7 | 多模型业绩对比 | 4 个模型年化收益 / Sharpe / IR 横向对比 | 柱状图（多子图） |
| 图 8 | 截面 IC 曲线 | 每个季度预测与实际收益的相关系数 | 折线图 |

---

## 六、最终 PDF 文档结构

```
林富强+TASK6.pdf

封面/标题
   ↓
摘要（约 200 字）

1. 引言
   1.1 任务背景
   1.2 学习目标

2. 机器学习交易策略核心理念
   2.1 基本假设与流程
   2.2 与单股预测（TASK5）的对比
   2.3 优点分析
   2.4 缺点分析与避坑要点

3. 量化交易 ML 模型因子与应变量
   3.1 应变量定义
   3.2 自变量因子分类
       3.2.1 动量类
       3.2.2 换手率/流动性类
       3.2.3 波动率类
       3.2.4 技术指标类
       3.2.5 估值/质量类
       3.2.6 规模/行业类
   3.3 本任务因子选择与预处理

4. 实验设计
   4.1 数据源与股票池
   4.2 时间区间与季度划分
   4.3 数据加载与因子工程实现
   4.4 训练/测试集划分原则

5. 模型构建与策略回测
   5.1 四种模型介绍（LR/DT/RF/XGB）
   5.2 模型训练与预测
   5.3 交易策略构建（Top-30 等权季度调仓）
   5.4 回测引擎与核心指标
   5.5 多模型对比结果（图 7 + 解读）
   5.6 累计收益曲线与回撤分析（图 4、图 5 + 解读）
   5.7 截面 IC 分析（图 8 + 解读）
   5.8 因子重要性解读（图 3 + 解读）

6. 附加题（自选方向）
   6.X 方向选择与设计
   6.X 实验结果与分析

7. 总结与展望
   7.1 本任务收获
   7.2 模型局限与改进方向
   7.3 量化交易 ML 的现实挑战

参考文献（如有）
```

**图表格式**（沿用 TASK5）：

- 每张图前一行：**图 X　标题**（黑体/加粗）
- 图下方紧接 1–2 段**解读文字**（宋体、五号）
- 例如：
  > **图 4　四种模型策略累计收益曲线对比（2021-2024）**
  > [图片]
  > 解读：Random Forest 策略在测试期 4 年内累计净值达到 1.62，显著优于沪深 300 基准（1.05）和截面等权基准（1.12）。...

---

## 七、关键技术细节

### 7.1 中文字体与配色

```python
# matplotlib 中文字体（沿用 TASK5 经验）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# A 股配色：红涨绿跌
UP_COLOR = '#C0392B'    # 涨/正收益
DOWN_COLOR = '#27AE60'  # 跌/负收益
NEUTRAL_COLOR = '#34495E'  # 中性（基准线）
```

### 7.2 Tushare 数据获取

```python
import tushare as ts
pro = ts.pro_api('your_token_here')

# 设置 token（建议从环境变量或 config.py 读取）
# 不要硬编码在代码里
```

### 7.3 时间顺序划分

⚠️ **铁律**：金融时间序列**严禁** `train_test_split` 随机打乱，必须按时间顺序

```python
# 正确
train = panel[panel['year'] < 2021]
test = panel[panel['year'] >= 2021]

# 错误 ❌
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
```

### 7.4 报告生成（沿用 TASK5 docx → pdf 经验）

- python-docx 生成 docx
- 设置 run.font.name + run._element.rPr.rFonts 中文字体（宋体）
- docx2pdf 转 PDF（依赖 Word / LibreOffice）
- 字体：宋体 / Times New Roman
- 字号：五号（10.5 pt）
- 行距：1.5 倍
- 段间距：0
- 对齐：两端对齐

### 7.5 依赖清单

```text
python>=3.8
tushare>=1.4
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
xgboost>=2.0
matplotlib>=3.7
seaborn>=0.13  # 用于热力图
python-docx>=1.1
docx2pdf>=0.1.8
```

---

## 八、实施计划

| 阶段 | 内容 | 预计产出 | 状态 |
|------|------|----------|------|
| **Step 1** | 完成 Tushare 数据下载脚本（成分股 + 日线） | `data/raw_daily/*.csv` 300+ 文件 | ⏳ |
| **Step 2** | 完成因子工程（12 个技术面因子） | `data/panel_with_factors.csv` | ⏳ |
| **Step 3** | 完成四个模型训练 + Top-30 选股回测 | `data/backtest_results.json` | ⏳ |
| **Step 4** | 完成可视化（8 张图） | `images/*.png` | ⏳ |
| **Step 5** | 调参优化（RF max_depth、XGBoost lr） | 最终模型确定 | ⏳ |
| **Step 6** | 撰写 docx 报告 | `林富强+TASK6.docx` | ⏳ |
| **Step 7** | docx → PDF + 格式校验 | `林富强+TASK6.pdf` | ⏳ |
| **Step 8** | 整理 README、conversation_log | 提交到 GitHub | ⏳ |

---

## 九、潜在风险与备选方案

| 风险 | 描述 | 备选方案 |
|------|------|---------|
| Tushare 积分不足 | 下载 10 年 300 只股票日线可能需要 5000+ 积分 | ① 缩窄股票池到 100 只；② 缩窄时间到 5 年；③ 用 Wind/聚宽代替 |
| 数据下载过慢 | Tushare 单次接口限流，300 只 × 10 年可能耗时数小时 | ① 加进度条 + 断点续传；② 用多线程 / 异步 |
| 因子计算有缺失 | 早期数据 / ST 股票可能因子缺失 | ① 用行业中位数填充；② 删除缺失 > 50% 的股票-季度 |
| 模型欠拟合 | 测试期年化收益低于基准 | ① 增加因子数量；② 加入基本面因子；③ 调整 N 持仓数 |
| 模型过拟合 | 训练集年化 30%，测试期 -10% | ① 简化模型（max_depth ↓）；② 加正则化；③ 缩短训练期 |

---

## 十、踩坑经验（积累区）

> 沿用 TASK1-TASK5 经验，本任务继续积累

1. **Tushare 频率限制** — 每次 `pro.daily()` 调用间隔 0.1s，否则触发限流。批量下载时必须加 `time.sleep(0.15)`。

2. **Tushare 复权处理** — `pro.daily()` 默认不复权，分析时应使用后复权（`adj_factor`）。解决方案：先取 daily，再乘以 adj_factor。

3. **停牌股票处理** — 停牌期间无成交，需用前一日收盘价填充，否则动量因子会失真。解决方案：检测 `vol == 0` 的日期，用前一天 `close` 填充。

4. **截面标准化 vs 全局标准化** — 因子标准化必须在**每个季度截面内**做（横截面标准化），而非用全样本均值/方差。解决方案：按 `quarter` 分组后 `groupby('quarter').transform(zscore)`。

5. **样本权重** — 不同季度市场状态差异大，可考虑按波动率倒数加权训练样本。

---

## 十一、参考图汇总（来自图片内容）

1. **方法一：简单阈值策略**（40%/50%/60% 概率阈值）
2. **方法二：双阈值策略**（买入 > 0.6，卖出 < 0.4，中间保持）
3. **方法三：概率加权仓位**（仓位 = (概率 - 0.5) × 2 × 最大仓位）
4. **方法四：ML 预测 + 技术指标过滤**（ML 信号 AND 技术过滤）
5. **ML 策略完整框架**（init → generate_signals → backtest → calculate_metrics → plot_results）
6. **策略核心参数一览**（buy_threshold=0.6, sell_threshold=0.4, max_position=0.8, stop_loss=0.05, take_profit=0.15, use_rsi_filter=True, use_trend_filter=True）
7. **信号生成逻辑**（model.predict_proba → 概率值 → 双阈值判定 → RSI 过滤 → 趋势过滤 → 最终信号）

> **本任务侧重点**：本任务聚焦**"截面选股"**（任务内容第 3 点的 4)5)6) 三小问），图片所示的"单股择时"框架（方法一到方法四）是另一种 ML 应用场景，不在本任务范围内，作为背景知识参考。

---

## 十二、已确认参数

> 用户已确认以下设计决策，代码实现以此为准

| 参数 | 确认结果 | 备注 |
|------|---------|------|
| 股票池 | **自选 100 只 A 股** | 按行业分散选取市值前列个股，Tushare 积分要求低 |
| 时间区间 | **2015-2024（10 年）** | 训练集 2015-2020（24 季度），测试集 2021-2024（16 季度） |
| 模型范围 | **LR + DT + RF + XGBoost 四模型** | 最完整对比，含 baseline + 单树 + 集成 + 进阶 |
| 附加题 | **持仓数敏感性分析（N=10/30/50/100）** | 用 RF 主力模型做对比，分析持仓集中度与风险收益关系 |

---

> **本文档将随任务进展持续更新**
