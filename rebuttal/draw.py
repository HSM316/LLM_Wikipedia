import json
import glob
import numpy as np
import matplotlib.pyplot as plt

# === 配色 ===
color_map = {
    'Art': '#1f77b4',
    'Bio': '#ff7f0e',
    'Chem': '#2ca02c',
    'CS': '#d62728',
    'Math': '#8c564b',
    'Philosophy': '#e377c2',
    'Phy': '#7f7f7f',
    'Sports': '#17becf'
}

# === 类别名称映射 ===
legend_map = {
    'Philosophy': 'Philo',
}

kind = "First"
strategy = "diff"
simulation="simple"

# === 1. 文件路径模式 ===
file_pattern = f"LLM_Wikipedia/Word_Frequency/Estimation_Result/{simulation}_eta/{strategy}/{kind}/*_eta_{kind}.jsonl"

# 排除 Featured 和 simple
excluded = {"Featured", "simple"}

# === 2. 解析所有文件 ===
category_data = {}

for filepath in glob.glob(file_pattern):
    category = filepath.split("/")[-1].replace(f"_eta_{kind}.jsonl", "")

    # 跳过不需要的类别
    if category in excluded:
        continue

    yearly_values = {}

    with open(filepath, "r") as f:
        for line in f:
            record = json.loads(line)
            for eta in record["eta_results"]:
                year = int(eta["Year"].split("-")[0])
                yearly_values.setdefault(year, []).append(eta["Eta"])

    # 每年计算平均值和标准差
    yearly_avg = {year: round(np.mean(values) * 100, 2) for year, values in yearly_values.items()}
    yearly_std = {year: round(np.std(values) * 100, 2) for year, values in yearly_values.items()}

    category_data[category] = (yearly_avg, yearly_std)


# === 4. 绘图：美化后的版本 ===
plt.figure(figsize=(8, 6), dpi=150)

# 使用更现代的样式
# plt.style.use("seaborn-v0_8-whitegrid")

years = sorted({year for cat in category_data.values() for year in cat[0].keys()})

for category, (avg, std) in category_data.items():
    avg_vals = [avg.get(y, np.nan) for y in years]
    std_vals = [std.get(y, np.nan) for y in years]

    color = color_map.get(category, '#333333')
    label = legend_map.get(category, category)

    plt.errorbar(
        years, avg_vals, yerr=std_vals,
        marker='o', markersize=5, capsize=3,
        linewidth=2, elinewidth=1,
        color=color, label=label, alpha=0.9
    )

# === 标题 ===
if kind == 'First':
    plt.title("LLM Impact on the First Sections of Wikipedia Articles",
              fontsize=15, pad = 10)
else:
    plt.title("LLM Impact on the Full Texts of Wikipedia Articles",
              fontsize=15, pad=10)

# === 坐标轴字体 ===
# plt.xlabel("Year", fontsize=12)
plt.ylabel("LLM Impact (%)", fontsize=12)
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)

# === 图例：更加美观 ===
plt.legend(
    fontsize=11,
    title_fontsize=12,
    frameon=True,
    fancybox=True,
    framealpha=0.8,
    ncol=2
)

# 轻微网格
plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig(f"impact/{simulation}_{strategy}_{kind}.pdf")
plt.show()
