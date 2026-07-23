# TASK7 · 实战推演：策略实盘部署与交易实战

> 量化交易工作坊第七个任务 · 作者：林富强 / 北京大学
> 策略方向：**多因子截面选股**（承接 TASK6，落地到 JoinQuant 平台）

---

## 一、任务要求速览

1. 在 [JoinQuant 官网](https://www.joinquant.com) 注册个人账号并完成认证。
2. 熟悉平台界面、数据获取、策略编辑、回测功能与文档资源。
3. 在平台上实现策略：**用模板自行设计 → 按回测调参 → 实盘模拟 → 评估表现与风险暴露 → 总结教训**。
4. 提交 `林富强+TASK7.pdf`：**宋体、五号字、1.5 倍行距、0 段距、两端对齐**；统计图须有标号+标题+解读；提交后不可修改。

---

## 二、本目录已准备好的内容（无需平台即可用）

| 文件 | 作用 |
|---|---|
| `code/jq_strategy.py` | **可直接粘贴进 JoinQuant 的策略代码**（多因子截面选股，参数集中在 `init_parameters()`，含风控过滤）。已在本地通过语法校验。 |
| `code/build_report.py` | 报告生成器，输出 `林富强+TASK7.docx`。排版严格按任务要求（宋体/五号/1.5 倍/两端对齐/0 段距），章节与图表框架已写好。 |
| `code/config.py` | 路径配置。 |
| `code/results_template.json` | **回测/实盘/风险指标占位文件**，跑完平台后把 `【待填写】` 替换为真实数值与图片路径。 |
| `images/` | 放平台导出的图表（按下方命名）。 |

---

## 三、你的操作流程（平台相关，需本人执行）

### 步骤 1 · 注册与认证
登录 https://www.joinquant.com → 注册 → 完成手机号 / 实名认证。记下账号与认证类型，回填 `results_template.json` 的 `account` 字段。

### 步骤 2 · 粘贴并运行策略
1. 「我的策略」→ 新建策略 → 把 `code/jq_strategy.py` 全文粘贴（替换默认模板）。
2. 设置回测：区间建议 **2014-01-01 ~ 2025-12-31**（保证 252 日动量有数据）；初始资金 **1,000,000**；撮合=真实价格。
3. 点「运行回测」，查看收益/回撤/风险指标。

### 步骤 3 · 参数调优
修改 `init_parameters()` 中的参数（如 `stock_num`、`rebalance_month`、`universe`、`factor_weights`），再次回测，对比前后表现。
- 把**调整前**结果填入 `backtest_base` + `param_before`
- 把**调整后**结果填入 `backtest_tuned` + `param_after`

### 步骤 4 · 实盘模拟
回测满意后点「开启实盘模拟」，观察模拟期表现，结果填入 `live_sim`。

### 步骤 5 · 导出图表
在回测/模拟结果页导出以下图表，按**命名**放入 `TASK7/images/`：

| 文件名 | 对应图 | 说明 |
|---|---|---|
| `fig1_backtest_equity.png` | 图 1（报告中编号图1为调优前后对比，见下方注意） | 回测累计净值 |
| `fig2_backtest_drawdown.png` | 回撤曲线 | 回测回撤 |
| `fig3_param_compare.png` | **报告图 1** | 参数调优前后净值对比（必放） |
| `fig4_live_sim_equity.png` | **报告图 2** | 实盘模拟净值（必放） |
| `fig5_risk_drawdown.png` | **报告图 3** | 实盘模拟回撤（必放） |
| `fig6_factor_importance.png` | **报告图 4** | 因子重要性/收益贡献（选放） |

> 注：报告内图表编号为「图 1~图 4」（调优对比 / 实盘净值 / 实盘回撤 / 因子贡献）。`results_template.json` 的 `images` 已映射好，文件名务必对应，缺失时报告会显示占位提示而不报错。

### 步骤 6 · 填写指标并生成文档
1. 编辑 `code/results_template.json`，把 `【待填写】` 替换为真实数值。
2. 生成 Word：
   ```bash
   cd TASK7/code
   python build_report.py        # 需要 python-docx（pip install python-docx）
   ```
   生成 `TASK7/林富强+TASK7.docx`。
3. 转 PDF：用 Word 打开后「文件 → 另存为 → PDF」；或在装有 Word 的机器上 `python -c "from docx2pdf import convert; convert('林富强+TASK7.docx')"`。

### 步骤 7 · 提交前检查
- [ ] 宋体、五号、1.5 倍行距、0 段距、两端对齐 已满足（生成器已固化）
- [ ] 每个统计图都有「图 N + 标题 + 解读」
- [ ] `【待填写】` 已全部替换
- [ ] 账号认证、平台熟悉、参数调优、实盘模拟、风险暴露、经验教训六部分齐全
- [ ] 核对无误后再提交（提交后不可修改）

---

## 四、本地校验记录

- `jq_strategy.py`：`python -m py_compile` 通过。
- `build_report.py`：用占位数据成功生成 `林富强+TASK7.docx`（77 段、4 表、图片缺失优雅跳过）。
- 注意：本机无 Word，**PDF 需在你的 Windows + Word 环境导出**。
