# -*- coding: utf-8 -*-
"""ROC 曲线对比图"""

import matplotlib.pyplot as plt

import config


def plot_roc_curves(results, y_test, save_path, dataset_name=''):
    """
    绘制多模型 ROC 曲线对比图。
    每个模型一条曲线，标注 AUC 值。
    """
    from evaluation import get_roc_data

    fig, ax = plt.subplots(figsize=(8, 6))

    for name, res in results.items():
        fpr, tpr, _ = get_roc_data(y_test, res['y_proba'])
        auc_val = res['metrics']['auc']
        color = config.MODEL_COLORS.get(name, None)
        ax.plot(fpr, tpr, color=color, linewidth=2.5,
                label=f'{name} (AUC = {auc_val:.3f})')

    # 随机猜测基线
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1.5, label='随机猜测 (AUC = 0.500)')

    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_xlabel('假阳性率 (FPR = FP / (FP + TN))', fontsize=11)
    ax.set_ylabel('真阳性率 (TPR = TP / (TP + FN))', fontsize=11)

    title = 'ROC 曲线对比'
    if dataset_name:
        title += f' — {dataset_name}'
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)

    # 标注左上角"理想区域"
    ax.annotate('理想区域\n(AUC→1)', xy=(0.05, 0.95), fontsize=9,
                color='gray', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.5))

    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [图] 已保存: {save_path}")
