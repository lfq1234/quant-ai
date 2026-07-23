# -*- coding: utf-8 -*-
"""生成 TASK8 报告用图表（全部中文、风格统一、红涨绿跌配色）。
使用系统 Python（anaconda3），不安装任何依赖。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

# ---------- 全局字体与风格 ----------
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
if os.path.exists(FONT_PATH):
    font_manager.fontManager.addfont(FONT_PATH)
    FONT_NAME = font_manager.FontProperties(fname=FONT_PATH).get_name()
else:
    FONT_NAME = "SimHei"

plt.rcParams["font.family"] = FONT_NAME
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["legend.fontsize"] = 10

# 统一配色（A股习惯：红涨绿跌）
RED = "#C0392B"
GREEN = "#27AE60"
BLUE = "#2C3E50"
GREY = "#7F8C8D"
LIGHT_RED = "#E8A0A0"
LIGHT_GREEN = "#A9DFBF"

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
os.makedirs(OUT, exist_ok=True)


def _style_ax(ax):
    """统一坐标轴线与网格风格"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GREY)
    ax.spines["bottom"].set_color(GREY)
    ax.tick_params(colors=BLUE)
    ax.yaxis.label.set_color(BLUE)
    ax.xaxis.label.set_color(BLUE)
    ax.title.set_color(BLUE)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.5, color=GREY)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("已生成:", path)


# ============ 图1：学习路径与技术演进路线图 ============
def chart_roadmap():
    steps = [
        ("任务一", "量化交易\n初体验", "搭建数据引擎\n理解基本流程"),
        ("任务二", "数据炼金术", "诊断数据\n构造技术指标"),
        ("任务三", "策略实战", "均线交叉回测\n工程化重构"),
        ("任务四", "海龟策略", "唐奇安通道\n多参数寻优"),
        ("任务五", "AI交易引擎", "机器学习分类\n两场景对比"),
        ("任务六", "智能决策者", "截面选股\n多模型比较"),
        ("任务七", "实战推演", "平台部署\n多因子策略"),
    ]
    n = len(steps)
    xs = list(range(1, n + 1))
    ys = [0] * n
    fig, ax = plt.subplots(figsize=(9.2, 3.6))
    # 连接线
    ax.plot(xs, ys, color=GREY, linewidth=2, zorder=1)
    for x, (tag, title, desc) in zip(xs, steps):
        ax.scatter([x], [0], s=420, color=BLUE, zorder=3, edgecolors="white", linewidths=2)
        ax.text(x, 0, tag.replace("任务", ""), color="white", ha="center", va="center",
                fontsize=12, fontweight="bold", zorder=4)
        ax.text(x, 0.85, title, color=BLUE, ha="center", va="bottom", fontsize=11, fontweight="bold")
        ax.text(x, -0.85, desc, color=GREY, ha="center", va="top", fontsize=9)
    ax.set_xlim(0.3, n + 0.7)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([])
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("图1  七次任务学习路径与技术演进路线", fontweight="bold", pad=12)
    save(fig, "fig1_roadmap.png")


# ============ 图2：均线交叉策略——不同均线周期配置的年化收益对比 ============
def chart_ma_periods():
    # 长江电力，凯利仓位，5种均线周期（数据来自 TASK3 backtest_results.json）
    periods = ["5/10", "5/15", "5/20", "10/20", "10/30"]
    annual = [-1.3, -2.39, -1.0, -0.85, -0.83]   # 年化收益(%)
    excess = [4.95, 3.98, 5.21, 5.35, 2.21]       # 超额收益(%)
    x = np.arange(len(periods))
    width = 0.38
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    b1 = ax.bar(x - width / 2, annual, width, label="策略年化收益", color=GREEN)
    b2 = ax.bar(x + width / 2, excess, width, label="相对买入持有超额收益", color=RED)
    ax.axhline(0, color=GREY, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["MA" + p for p in periods])
    ax.set_ylabel("收益率(%)")
    ax.set_title("图2  均线交叉策略不同周期配置的表现对比", fontweight="bold", pad=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.annotate(f"{h:.2f}", (b.get_x() + b.get_width() / 2, h),
                    ha="center", va="bottom" if h >= 0 else "top",
                    fontsize=9, color=BLUE,
                    xytext=(0, 3 if h >= 0 else -3), textcoords="offset points")
    _style_ax(ax)
    ax.legend(loc="upper right", frameon=False)
    save(fig, "fig2_ma_periods.png")


# ============ 图3：海龟策略 24组参数×3股 超额收益热力图（红涨绿跌）============
def chart_turtle_heatmap():
    params = ["5/3", "5/5", "10/5", "10/10", "15/7", "20/10", "30/15", "55/20"]
    stocks = ["长江电力", "贵州茅台", "中国平安"]
    # excess_return(%) 来自 TASK4 multi_param_results.json
    data = np.array([
        [0.92, 0.74, 8.48, 4.07, 5.25, -0.33, -1.89, -2.00],   # 长江电力
        [1.80, -1.06, 10.62, 7.90, 9.53, 9.81, 10.34, 12.38],  # 贵州茅台
        [8.69, 13.60, 13.53, 13.48, 15.50, 18.40, 15.11, 11.46],  # 中国平安
    ])
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    # 红涨绿跌：正超额=红，负超额=绿 -> 反转 RdYlGn
    im = ax.imshow(data, cmap="RdYlGn_r", aspect="auto")
    ax.set_xticks(range(len(params)))
    ax.set_xticklabels(params)
    ax.set_yticks(range(len(stocks)))
    ax.set_yticklabels(stocks)
    ax.set_xlabel("入场/出场窗口（交易日）")
    ax.set_title("图3  海龟策略各参数组合相对买入持有的超额收益", fontweight="bold", pad=10)
    for i in range(len(stocks)):
        for j in range(len(params)):
            v = data[i, j]
            txt_color = "white" if (v < 0 or v > 12) else BLUE
            ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                    fontsize=10, color=txt_color, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
    cbar.set_label("超额收益(%)  红=跑赢  绿=跑输", fontsize=10)
    cbar.ax.tick_params(labelsize=9)
    save(fig, "fig3_turtle_heatmap.png")


# ============ 图4：机器学习模型在两个场景下的分类性能（AUC）============
def chart_ml_auc():
    models = ["线性回归", "逻辑回归", "决策树", "随机森林", "最近邻"]
    auc_medical = [0.9924, 0.9954, 0.9163, 0.9939, 0.9788]
    auc_stock = [0.3439, 0.3458, 0.4585, 0.3913, 0.3597]
    x = np.arange(len(models))
    width = 0.38
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    b1 = ax.bar(x - width / 2, auc_medical, width, label="医学数据（强信号）", color=BLUE)
    b2 = ax.bar(x + width / 2, auc_stock, width, label="股票数据（弱信号）", color=RED)
    ax.axhline(0.5, color=GREY, linewidth=1, linestyle="--")
    ax.text(len(models) - 0.5, 0.51, "随机基准 0.5", color=GREY, fontsize=9, va="bottom")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15)
    ax.set_ylabel("AUC 值")
    ax.set_ylim(0, 1.08)
    ax.set_title("图4  机器学习模型在两类数据上的分类性能对比", fontweight="bold", pad=10)
    _style_ax(ax)
    ax.legend(loc="upper right", frameon=False)
    save(fig, "fig4_ml_auc.png")


# ============ 图5：截面选股（TASK6）四类模型风险收益对比 ============
def chart_cross_section():
    models = ["线性回归", "决策树", "随机森林", "XGBoost"]
    annual = [-3.83, 2.40, -1.30, 3.10]      # 年化收益(%)
    sharpe = [-0.2234, 0.1386, -0.0668, 0.1676]  # 夏普比率
    x = np.arange(len(models))
    width = 0.38
    fig, ax1 = plt.subplots(figsize=(6.8, 3.9))
    colors = [GREEN if v < 0 else RED for v in annual]
    b1 = ax1.bar(x - width / 2, annual, width, label="年化收益(%)", color=colors)
    ax1.axhline(0, color=GREY, linewidth=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models)
    ax1.set_ylabel("年化收益(%)", color=BLUE)
    for b in b1:
        h = b.get_height()
        ax1.annotate(f"{h:.2f}", (b.get_x() + b.get_width() / 2, h),
                     ha="center", va="bottom" if h >= 0 else "top",
                     fontsize=9, color=BLUE, xytext=(0, 3 if h >= 0 else -3), textcoords="offset points")
    ax2 = ax1.twinx()
    b2 = ax2.bar(x + width / 2, sharpe, width, label="夏普比率", color="#E67E22", alpha=0.85)
    ax2.axhline(0, color=GREY, linewidth=0.8)
    ax2.set_ylabel("夏普比率", color="#E67E22")
    ax2.tick_params(axis="y", colors="#E67E22")
    ax1.set_title("图5  截面选股策略四类模型风险收益对比", fontweight="bold", pad=10)
    for b in b2:
        h = b.get_height()
        ax2.annotate(f"{h:.3f}", (b.get_x() + b.get_width() / 2, h),
                     ha="center", va="bottom" if h >= 0 else "top",
                     fontsize=9, color="#E67E22", xytext=(0, 3 if h >= 0 else -3), textcoords="offset points")
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=9)
    save(fig, "fig5_cross_section.png")


# ============ 图6：多因子选股（TASK7）样本内与样本外表现对比 ============
def chart_factor_oos():
    scenes = ["样本内(2020-2026)", "样本外(2019上半年)"]
    annual = [2.97, -8.44]
    drawdown = [-24.28, -12.66]
    sharpe = [-0.080, -0.701]
    win = [52.4, 17.4]
    bench = [19.58, 27.07]   # 基准区间总收益
    x = np.arange(len(scenes))
    width = 0.18
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.bar(x - 1.5 * width, annual, width, label="策略年化收益", color=RED)
    ax.bar(x - 0.5 * width, drawdown, width, label="最大回撤", color=GREEN)
    ax.bar(x + 0.5 * width, [s * 100 for s in sharpe], width, label="夏普比率(×100)", color=BLUE)
    ax.bar(x + 1.5 * width, bench, width, label="基准区间收益", color=GREY)
    ax.axhline(0, color=GREY, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(scenes)
    ax.set_ylabel("数值(%)")
    ax.set_title("图6  多因子选股策略样本内与样本外表现对比", fontweight="bold", pad=10)
    _style_ax(ax)
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    save(fig, "fig6_factor_oos.png")


if __name__ == "__main__":
    chart_roadmap()
    chart_ma_periods()
    chart_turtle_heatmap()
    chart_ml_auc()
    chart_cross_section()
    chart_factor_oos()
    print("全部图表生成完毕。")
