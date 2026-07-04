# TASK2 对话记录

## 对话时间：2026年7月4日

---

### 用户
先看下我桌面的quant-ai项目，这个是github的项目，在里面新建TASK2文件夹，之后的操作文件都在这个文件夹里面

### 助手
查看了桌面 quant-ai 项目结构，TASK1 文件夹包含9个文件（md、py、csv、png、html等）。在 `C:\Users\LENOVO\Desktop\quant-ai\` 下创建了 TASK2 文件夹，后续所有操作文件都放在这个文件夹里。

---

### 用户
TASK1文件夹里面是我上一次的作业，这次的作业会需要用到TASK1文件里面的数据，但是不要修改他的内容，你记住

### 助手
详细查看了 TASK1 的全部内容：
- README.md：任务说明，标的为长江电力(600900.SH)，数据时间2025-07-02至2026-07-02，共243个交易日
- fetch_cjdl.py：Tushare Pro 数据获取脚本，使用 pro.daily 接口
- generate_task1.py：docx/pdf 生成脚本，格式为宋体五号、1.5倍行距、0段间距、两端对齐
- cjdl_600900_2025-2026.csv：CSV字段包括 ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount

确认原则：TASK1 文件夹只读不写，TASK2 需要数据时直接引用 TASK1 的 CSV，绝不改动 TASK1 原文件。将信息写入记忆文件。

---

### 用户
【任务内容】

今天的任务包括以下四个问题：

1. 对数据进行基础的诊断分析，检查缺失值，计算描述性统计量。编写py代码对TASK1的csv数据做处理

2. 通过搜索和大模型了解基础描述指标，包括 RSI，MACD，布林带（Bollinger Bands）三个指标，给出具体计算方法以及作用。这个任务写一个文档来描述

3. python编程实现以下内容：加载已存储的股价数据，计算RSI，MACD，布林带，根据指标计算结果绘制对应可视化图形。编写py代码和html来实现展示

4. 扩展了解还有其他哪些典型指标，选取一个进行介绍和计算，并用图形表示

【提交要求】
1. 在TASK2下提交pdf文档，命名为姓名+TASK2。
2. 宋体，五号字，1.5倍行距，0倍段间距，文字两端对齐。
3. 如有统计图表，每个统计图都要有标号和标题，需要有一定的解读。
4. 作业在提交后不能修改，请各位同学在提交前确认文档内容无误。

### 助手
创建任务清单（5个todo），逐步完成：

**任务一：数据诊断分析**
- 编写 `data_diagnosis.py` 脚本
- 加载 TASK1 的 CSV 数据（243条记录，11个字段）
- 缺失值检查：所有字段缺失值均为0，数据完整性良好
- 描述性统计量：计算计数、均值、标准差、最小值、四分位数、中位数、最大值、方差、偏度、峰度
  - 收盘价均值27.59元，标准差0.95元，范围25.65~30.61元
  - 日涨跌幅均值-0.033%，标准差0.758%，偏度0.05，峰度1.30
- 生成数据诊断可视化图 `data_diagnosis.png`（4个子图：缺失值检查、收盘价箱线图、日涨跌幅直方图、成交量分布）
- 保存统计结果到 `descriptive_stats.csv` 和 `diagnosis_summary.json`

**任务二：技术指标说明**
在PDF文档中详细描述三个指标：
- RSI（相对强弱指数）：RS = N日平均涨幅/N日平均跌幅，RSI = 100 - 100/(1+RS)，超买>70，超卖<30
- MACD（指数平滑异同移动平均线）：DIF = EMA(12) - EMA(26)，DEA = EMA(DIF, 9)，MACD柱 = (DIF-DEA)×2，金叉买入死叉卖出
- 布林带（Bollinger Bands）：中轨=SMA(20)，上轨=中轨+2σ，下轨=中轨-2σ，衡量波动率和超买超卖

**任务三：指标计算与可视化**
- 编写 `calculate_indicators.py` 脚本
- 加载 TASK1 股价数据
- 计算三个指标：
  - RSI(14)：最新值44.76，中性区间
  - MACD(12,26,9)：DIF=-0.1677，DEA=-0.1131，空头趋势
  - 布林带(20,2)：上轨28.26，中轨27.13，下轨26.04
- 生成4张可视化图表（chart_rsi.png, chart_macd.png, chart_boll.png, chart_kdj.png）
- 生成 HTML 报告 `report.html`（含所有图表、数据解读、指标汇总表）
- 保存含指标数据 `data_with_indicators.csv`

**任务四：扩展指标 KDJ**
选取 KDJ 随机指标进行介绍、计算和可视化：
- KDJ介绍：由George C. Lane创立，计算RSV、K、D、J三条线
- 计算方法：RSV=(Close-Low_n)/(High_n-Low_n)×100，K=2/3×prev_K+1/3×RSV，D=2/3×prev_D+1/3×K，J=3K-2D
- 计算结果：K=46.61，D=33.53，J=72.78
- 生成KDJ可视化图表 `chart_kdj.png`

**最终文档生成**
- 编写 `generate_task2.py` 脚本
- 生成 `林富强+TASK2.docx`（宋体五号，1.5倍行距，0段间距，两端对齐）
- docx2pdf转换失败，使用 PowerShell Word COM 对象成功转换为 `林富强+TASK2.pdf`
- PDF包含全部四个任务内容，8张图表均有标号和解读

最终 TASK2 文件夹包含14个文件。

---

### 用户
把这次的修改提交到github吧

### 助手
执行 git 操作：
- `git add TASK2/`：添加14个文件
- `git commit`：提交信息为"TASK2: 数据炼金术 - 数据诊断与构造交易指标"，14个文件，1590行新增
- `git push origin main`：成功推送到 https://github.com/lfq1234/quant-ai.git

---

### 用户
把咱俩的这次对话写成conversation_log文件里面，放到TASK2文件夹里面，上传到github

### 助手
创建 `conversation_log.md` 文件记录完整对话过程，添加到 TASK2 文件夹并推送到 GitHub。

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `林富强+TASK2.pdf` | 最终提交的作业 PDF |
| `林富强+TASK2.docx` | Word 源文件 |
| `report.html` | HTML 可视化报告 |
| `data_diagnosis.py` | 任务一：数据诊断脚本 |
| `calculate_indicators.py` | 任务三+四：指标计算与可视化脚本 |
| `generate_task2.py` | PDF 文档生成脚本 |
| `data_diagnosis.png` | 数据诊断可视化图 |
| `chart_rsi.png` | RSI 指标图表 |
| `chart_macd.png` | MACD 指标图表 |
| `chart_boll.png` | 布林带指标图表 |
| `chart_kdj.png` | KDJ 指标图表 |
| `data_with_indicators.csv` | 含全部指标的完整数据 |
| `descriptive_stats.csv` | 描述性统计量表 |
| `diagnosis_summary.json` | 诊断摘要 JSON |
| `conversation_log.md` | 本对话记录文件 |
