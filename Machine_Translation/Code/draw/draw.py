import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -----------------------------
# 数据输入
# -----------------------------
# data = {
#     "Lang": ["PT","FR","DE","ZH","IT","ES","RU","AR","HI","JA","KO"],
#     "BLEU_O": [69.59,87.04,72.39,72.14,58.6,59.25,51.4,71.86,58.49,62.05,54.75],
#     "BLEU_G": [87.71,96.75,93.38,78.61,62.14,84.44,63.33,78.73,67.29,64.21,78.35],
#     "ChrF_O": [79.41,94.62,77.98,67.06,67.31,73.7,73.97,83.89,75.25,56.86,52.5],
#     "ChrF_G": [92.02,99.31,96.1,78.19,78.22,90.7,84.29,88.61,80.64,58.03,69.23],
#     "COMET_O": [88.93,90.45,84.7,82.4,85.22,85.03,84.75,83.19,59.53,62.61,25.94],
#     "COMET_G": [90.45,87.79,86.37,83.91,88.72,89.49,86.37,84.04,60.16,62.87,25.98],
# }

data = {
    "Lang": ["PT","FR","DE","ZH","IT","ES","RU","AR","HI","JA","KO"],
    "BLEU_O": [69.74, 88.39, 68.07, 70.34, 56.14, 60.00, 44.99, 67.52, 46.85, 49.48, 45.28],
    "BLEU_G": [85.99, 89.40, 90.68, 75.32, 69.32, 84.07, 69.18, 70.99, 49.37, 45.28, 57.53],

    "ChrF_O": [81.12, 91.18, 77.17, 59.08, 67.97, 74.45, 70.15, 80.70, 58.20, 49.43, 58.36],
    "ChrF_G": [91.60, 91.32, 94.83, 65.10, 82.04, 91.26, 81.81, 87.20, 57.06, 46.40, 68.94],

    "COMET_O": [90.71, 88.39, 86.35, 84.19, 87.53, 86.91, 86.12, 85.24, 62.31, 64.15, 29.34],
    "COMET_G": [92.31, 89.91, 87.98, 85.73, 90.11, 91.24, 87.83, 86.14, 63.18, 64.37, 29.48],
}

df = pd.DataFrame(data)


df = pd.DataFrame(data)

# -----------------------------
# 绘制单指标对比图（O vs G + Δ标签）
# -----------------------------

def plot_metric(metric_name, ylabel, filename):
    O = df[f"{metric_name}_O"]
    G = df[f"{metric_name}_G"]
    diff = G - O

    x = np.arange(len(df))
    width = 0.35

    plt.figure(figsize=(12,4))
    
    # Bars
    plt.bar(x - width/2, O, width, label="Original", color="#4B3F72")
    plt.bar(x + width/2, G, width, label="LLM-Processed", color="#C9C7D1")

    # Δ 标注
    for i in range(len(df)):
        d = diff[i]
        gx = x[i] + width/2
        gy = G[i]

        if d >= 0:
            plt.annotate(f"+{d:.2f}",
                          xy=(gx, gy),
                          xytext=(0, 9),
                          textcoords="offset points",
                          ha="center",
                          color="#1b7f5f",
                          fontsize=11,
                          fontweight="bold")
        else:
            # plt.annotate(f"{d:.2f}",
            #               xy=(gx, gy),
            #               xytext=(0, -25),
            #               textcoords="offset points",
            #               ha="center",
            #               color="#8b0000",
            #               fontsize=11,
            #               fontweight="bold")
            plt.annotate(f"{d:.2f}",
              xy=(gx, gy),
              xytext=(0, 25),
              textcoords="offset points",
              ha="center",
              color="#8b0000",
              fontsize=11,
              fontweight="bold")

    plt.xticks(x, df["Lang"], fontsize=12)
    plt.ylim(0, max(df["BLEU_G"]) * 1.12)   # 上限提高 12%

    plt.ylabel(ylabel, fontsize=14)

    # plt.title(f"Facebook-NLLB {metric_name} Performance on Original vs LLM-Influenced Benchmarks", fontsize=16)
    plt.title(f"Helsinki-NLP {metric_name} Performance on Original vs LLM-Influenced Benchmarks", fontsize=16)

    plt.legend(fontsize=12)
    plt.tight_layout()
    # plt.show()
    plt.savefig(filename, dpi=300)


# 调用函数绘制三张图
# plot_metric("BLEU", "BLEU Score", "Facebook_BLEU.pdf")
# plot_metric("ChrF", "ChrF Score", "Facebook_ChrF.pdf")
# plot_metric("COMET", "COMET Score", "Facebook_COMET.pdf")

plot_metric("BLEU", "BLEU Score", "Helsinki_BLEU.pdf")
plot_metric("ChrF", "ChrF Score", "Helsinki_ChrF.pdf")
plot_metric("COMET", "COMET Score", "Helsinki_COMET.pdf")

