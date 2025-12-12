import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 分类 & 数据路径
categories = ['Art', 'Bio', 'Chem', 'CS', 'Math', 'Philosophy', 'Phy', 'Sports']
category_short = ['Art', 'Bio', 'Chem', 'CS', 'Math', 'Philo', 'Phy', 'Sports']  # 用于x轴
data_dir = "LLM_Wikipedia/Linguistic_Style/Metrics/Full"
years = list(range(2018, 2026))

# 要绘制的 metrics
# metrics = [
#     "Flesch Reading Ease",
#     "Flesch-Kincaid Grade Level",
#     "Automated Readability Index (ARI)",
#     "Coleman-Liau Index",
#     "Gunning Fog Index",
#     "Dale-Chall Readability Score"
# ]

metrics =[
    # 'Passive_Voice_Rate',
    # 'Auxiliary_Verbs'
    "Flesch-Kincaid Grade Level",
]

def load_metric_matrix(metric_name):
    z = []
    for cat in categories:
        path = os.path.join(data_dir, f"R_{cat}_Full.csv")
        df = pd.read_csv(path)
        df = df[df['year'].isin(years)]

        mean_col = f"{metric_name}_mean"
        if mean_col not in df.columns:
            raise ValueError(f"{mean_col} not found in {path}")

        # 排序并取出数据（年份对齐）
        z_row = df.sort_values("year")[mean_col].values
        z.append(z_row)
    return np.array(z)

def line_3d(x, y_labels, z, metric_name):
    ...
    y_num = len(y_labels)
    X, Y = np.meshgrid(x, np.arange(1, y_num + 1))
    z_diff = (z - z[:, [0]]) 

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # ✅ 为每个 metric 选择不同 colormap
    metric_cmaps = {
        # "Dale-Chall Readability Score": "inferno",
        # "Automated Readability Index (ARI)": "plasma",
        # "Flesch Reading Ease": "viridis",
        # "Coleman-Liau Index": "cividis",
        # "Gunning Fog Index": "coolwarm",
        "Flesch-Kincaid Grade Level": "cividis"
        # 'Passive_Voice_Rate':"plasma",
        # 'Auxiliary_Verbs':"viridis"

    }

    cmap = plt.get_cmap(metric_cmaps.get(metric_name, "viridis"))
    norm = plt.Normalize(vmin=0, vmax=y_num)

    z_base = np.min(z_diff) - abs(np.min(z_diff)) * 0.01

    for i in range(y_num):
        color = cmap(norm(i))

        ax.plot(Y[i], X[i], z_diff[i], color=color,
                linestyle='-', linewidth=1.5, marker='o', markersize=3, alpha=0.6)

        polygon = [
            [Y[i, 0], X[i, 0], z_base],
            [Y[i, -1], X[i, -1], z_base],
        ] + [[Y[i, j], X[i, j], z_diff[i, j]] for j in reversed(range(len(x)))]

        ax.add_collection3d(Poly3DCollection([polygon], color=color, alpha=0.25))

    # ax.set_ylabel('Year', labelpad=14)
    ax.set_zlabel('Relative Value', labelpad=16)
    ax.set_xticks(np.arange(1, y_num + 1))
    ax.set_xticklabels(category_short, rotation=45)
    # ax.set_title(f"Change in {metric_name}", fontsize=18)

    ax.grid(False)
    # plt.tight_layout()
    os.makedirs("3d_figures", exist_ok=True)
    plt.savefig(f"3d_figures/{metric_name.replace(' ', '_').replace('/', '')}.pdf")
    plt.close()


def main():
    time = np.array(years)
    for metric in metrics:
        z = load_metric_matrix(metric)
        line_3d(time, categories, z, metric)

if __name__ == '__main__':
    main()
