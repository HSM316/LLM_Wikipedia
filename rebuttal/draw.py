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
    'Featured': '#9467bd',
    'Math': '#8c564b',
    'Philosophy': '#e377c2',
    'Phy': '#7f7f7f',
    'simple': '#bcbd22',
    'Sports': '#17becf'
}

# === 类别名称映射 ===
legend_map = {
    'Philosophy': 'Philo',
    'Featured': 'FA',
    'simple': 'SA'
}

# === 1. 文件路径模式 ===
file_pattern = "Word_Frequency/Estimation_Result/Featured_First_eta/same/Full/GPT3.5/*_eta_Full.jsonl"

# === 2. 解析所有文件 ===
category_data = {}

for filepath in glob.glob(file_pattern):
    category = filepath.split("/")[-1].replace("_eta_Full.jsonl", "")
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

# === 3. 输出每个类别的 avg 和 std ===
for category, (avg, std) in category_data.items():
    print(f"Category: {category}")
    print("Yearly Averages:", {year: avg[year] for year in sorted(avg.keys())})
    print("Yearly Standard Deviations:", {year: std[year] for year in sorted(std.keys())})
    print("-" * 40)

# === 4. 绘制折线图 ===
plt.figure(figsize=(10, 6))

years = sorted({year for cat in category_data.values() for year in cat[0].keys()})

for category, (avg, std) in category_data.items():
    avg_vals = [avg.get(y, np.nan) for y in years]
    std_vals = [std.get(y, np.nan) for y in years]
    color = color_map.get(category, '#333333')  # 如果类别不在 color_map 中，使用默认颜色
    label = legend_map.get(category, category)  # 如果类别在 legend_map 中，替换为映射名称
    plt.errorbar(years, avg_vals, yerr=std_vals, marker='o', capsize=3, label=label, color=color)

plt.title("Full Texts of Wikipedia Pages", fontsize=14)
plt.xlabel("Year", fontsize=12)
plt.ylabel("LLM Impact (%)", fontsize=12)
plt.legend(ncol=2, fontsize=10)
plt.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.show()