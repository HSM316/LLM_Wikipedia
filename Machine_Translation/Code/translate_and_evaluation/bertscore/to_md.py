import pandas as pd

# 1. 读取CSV
input_csv = "bertscore_google.csv"  # 改成你的文件
df = pd.read_csv(input_csv)

# 2. 去掉前缀
new_columns = []
for col in df.columns:
    if col.startswith("bertscore_vs_"):
        new_col = col.replace("bertscore_vs_", "")
    else:
        new_col = col
    new_columns.append(new_col)

df.columns = new_columns

# 3. 排列列顺序：按 precision, recall, f1 分组
cols = df.columns.tolist()
fixed = ["language"]
precision_cols = [c for c in cols if "precision" in c]
recall_cols = [c for c in cols if "recall" in c]
f1_cols = [c for c in cols if "f1" in c]
new_order = fixed + precision_cols + recall_cols + f1_cols
df = df[new_order]

# 4. 格式化数值列为两位小数字符串（保留末尾0）
for col in df.columns:
    if col != "language":
        df[col] = df[col].map(lambda x: f"{x:.3f}")

# 5. 转Markdown
markdown_table = df.to_markdown(index=False, tablefmt="github")

# 6. 保存Markdown文件
output_md = "bertscore_google.md"
with open(output_md, "w", encoding="utf-8") as f:
    f.write(markdown_table)

print(f"\n✅ 已生成Markdown文件: {output_md}")
