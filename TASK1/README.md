# TASK1 - 量化交易初体验：从零搭建数据引擎

## 任务内容

1. 量化交易相较于传统手工操作交易的优势
2. 基本概念解释：K线、基本面、技术面
3. 使用 Tushare 获取股票数据、绘制收盘价曲线图、导出 CSV

## 文件说明

| 文件 | 说明 |
|------|------|
| `林富强+TASK1.pdf` | 最终提交的作业 PDF（含任务1、2、3） |
| `林富强+TASK1.docx` | Word 源文件，可编辑后重新导出 PDF |
| `generate_task1.py` | 生成 docx/pdf 文档的 Python 脚本（python-docx + docx2pdf） |
| `fetch_cjdl.py` | Tushare 数据获取 + 绘图 + CSV 导出脚本 |
| `cjdl_600900_2025-2026.csv` | 长江电力（600900.SH）近一年日线数据 |
| `cjdl_close_price.png` | 收盘价曲线图 |
| `report.html` | 任务三可视化报告（含图表、数据样例、代码） |

## 数据概况

- **标的**：600900.SH 长江电力
- **时间区间**：2025-07-02 至 2026-07-02（243 个交易日）
- **数据来源**：Tushare Pro（pro.daily 接口）

## 运行环境

```
Python 3.x
tushare >= 1.4.24
matplotlib >= 3.10.0
pandas >= 2.2.0
python-docx
docx2pdf
```
