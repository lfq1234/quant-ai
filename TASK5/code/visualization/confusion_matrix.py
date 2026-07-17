# -*- coding: utf-8 -*-
"""混淆矩阵热力图"""

import matplotlib.pyplot as plt


def plot_confusion_matrix(cm, model_name, save_path, dataset_name=''):
    """绘制单个模型的混淆矩阵热力图"""
    fig, ax = plt.subplots(figsize=(5, 4))

    # 自定义颜色：对角线绿色（正确），非对角线红色（错误）
    im = ax.imshow(cm, cmap='RdYlGn', vmin=0, vmax=cm.max())

    # 标注数值
    labels = [['TN', 'FP'], ['FN', 'TP']]
    for i in range(2):
        for j in range(2):
            text_color = 'white' if cm[i, j] > cm.max() * 0.6 else 'black'
            ax.text(j, i, f'{labels[i][j]}={cm[i, j]}',
                    ha='center', va='center',
                    fontsize=14, fontweight='bold', color=text_color)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['预测跌(0)', '预测涨(1)'])
    ax.set_yticklabels(['实际跌(0)', '实际涨(1)'])
    title = f'{model_name} 混淆矩阵'
    if dataset_name:
        title += f'（{dataset_name}）'
    ax.set_title(title, fontsize=13, fontweight='bold')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [图] 已保存: {save_path}")
