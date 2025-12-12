import os
import pandas as pd
import matplotlib.pyplot as plt

# === 配置 ===
base_dir = "LLM_Wikipedia/Word_Frequency/Frequency/f_First"   # 根目录
categories = ["Art", "Bio", "Chem", "CS", "Math", "Philosophy", "Phy", "Sports"]
target_word = "capabilities"                          # 想要画的单词
per_k = 1000                                     # 转为每千词

# （可选）自定义学科显示名，保持图例顺序
display_name = {
    "Art": "Art", "Bio": "Bio", "Chem": "Chem", "CS": "CS",
    "Math": "Math", "Philosophy": "Philosophy", "Phy": "Phy", "Sports": "Sports"
}

# === 全局字体设置 ===
plt.rcParams.update({
    'font.size': 16,          # 默认字体大小
    'axes.titlesize': 18,     # 标题字体
    'axes.labelsize': 16,     # 坐标轴标签字体
    'xtick.labelsize': 14,    # x轴刻度字体
    'ytick.labelsize': 14,    # y轴刻度字体
    'legend.fontsize': 13,    # 图例字体
})

# === 读取并绘图（用面向对象接口，方便把标题移到框内） ===
fig, ax = plt.subplots(figsize=(8, 6))

year_cols = ["2018-01-01", "2019-01-01", "2020-01-01", "2021-01-01", "2022-01-01",
             "2023-01-01", "2024-01-01", "2025-01-01"]
x_years = [c[:4] for c in year_cols]

for i, cat in enumerate(categories):
    csv_path = os.path.join(base_dir, f"f_{cat}_First.csv")
    if not os.path.exists(csv_path):
        print(f"[WARN] 文件不存在：{csv_path}，已跳过。")
        continue

    df = pd.read_csv(csv_path)
    if "Word" not in df.columns:
        print(f"[WARN] 文件缺少 Word 列：{csv_path}，已跳过。")
        continue

    row = df.loc[df["Word"].str.lower() == target_word.lower()]
    if row.empty:
        print(f"[WARN] 未找到单词 `{target_word}` 于 {csv_path}，已跳过。")
        continue

    y = (row[year_cols].values.flatten().astype(float)) * per_k

    ax.plot(
        x_years, y,
        marker='x',
        linewidth=2,
        label=display_name.get(cat, cat)
    )

# —— 把标题往下移到坐标框内（y<1 即在框内）——
ax.set_title(
    f"Frequency Trend of '{target_word}'",
    y=0.92,                 # 0~1 之间，越小越往下；1 是轴顶边
    pad=2,                  # 与顶边的内边距
    fontsize=16
)

ax.set_xlabel("Year")
ax.set_ylabel("Frequency (per 1000 words)")
ax.legend(ncol=4, frameon=True, loc="upper left", bbox_to_anchor=(0.05, 1.20))
ax.grid(alpha=0.3, linestyle='--', linewidth=0.7)

fig.tight_layout()
fig.savefig(f"LLM_Wikipedia/Word_Frequency/{target_word}.pdf", bbox_inches='tight')
plt.show()
