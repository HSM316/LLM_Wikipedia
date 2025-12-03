import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------
# 读取数据
# ------------------------------
df = pd.read_csv("Word_Frequency/Frequency/Simulation/f_Featured_r_First.csv")

# 只取 crucial 和 additionally
words = ["crucial", "additionally"]
df = df[df["Word"].isin(words)]

# 提取数值 ×1000
O = df["2022-01-01"].values * 1000
G = df["revised"].values * 1000
x = np.arange(len(words))

# ------------------------------
# 绘图
# ------------------------------
plt.figure(figsize=(8, 6))

width = 0.35

# 原先的柱状图配色（保持不变）
color_O = "#7699D4"   # 蓝色
color_G = "#E5B88F"   # 杏色

# 新的文字标注颜色
label_red = "#C64747"   # 红色
label_green = "#3A8F3A" # 绿色

plt.bar(x - width/2, O, width, label="Original", color=color_O)
plt.bar(x + width/2, G, width, label="LLM-Revised", color=color_G)

# ------------------------------
# 标注原始数值（红色）与改写数值（绿色）
# ------------------------------
for i in range(len(words)):
    # Original 标注（红色）
    plt.annotate(
        f"{O[i]:.4f}",
        xy=(x[i] - width/2, O[i]),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=label_red
    )
    
    # Revised 标注（绿色）
    plt.annotate(
        f"{G[i]:.4f}",
        xy=(x[i] + width/2, G[i]),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=label_green
    )

# 坐标轴标签
plt.xticks(x, words, fontsize=18)
plt.ylim(0, 0.65)

plt.ylabel("Frequency (per 1000 words)", fontsize=16)
plt.title("Word Frequency: Original vs LLM-Revised Wikipedia Pages", fontsize=18)

plt.legend(fontsize=16)
plt.tight_layout()
plt.savefig("compare.pdf")
plt.show()
