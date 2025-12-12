import os
import pandas as pd
import numpy as np

# 输入与输出目录
metrics_dir = "Wikipedia/Readability/Full"
summary_dir = "LLM_Wikipedia/Linguistic_Style/Metrics/Full"
os.makedirs(summary_dir, exist_ok=True)

# metrics 列（你可自行选择一套）
# metrics_cols = [
#     "Long_Sent_Rate","Avg_Sent_Length","CTTR","Passive_Voice_Rate","Clause_Ratio",
#     "Auxiliary_Verbs","ToBe_Verbs","Conjunctions","Prepositions","Pronouns",
#     "Nominalizations","Long_Words_Rate","OneSyllable_Rate","Syllables_Per_Word",
#     "Start_Pronoun","Start_Article","Avg_Parse_Tree_Depth"
# ]

metrics_cols = ["Flesch Reading Ease", "Flesch-Kincaid Grade Level", "Automated Readability Index (ARI)", "Coleman-Liau Index",  "Gunning Fog Index", "Dale-Chall Readability Score"]

categories = ["Art", "Bio", "Chem", "CS", "Phy", "Math", "Philosophy", "Sports"]

# 自动扫描所有年份
years = list(range(2018, 2026))


def compute_mean_std(csv_path):
    """读取 metrics 文件 → 返回 {col_mean:..., col_std:...}"""
    df = pd.read_csv(csv_path)

    row = {}
    for col in metrics_cols:
        if col not in df.columns:
            continue
        row[f"{col}_mean"] = df[col].mean()
        row[f"{col}_std"]  = df[col].std()
    return row


def build_summary(category):
    """直接生成 summary（不依赖已有文件）"""
    summary_rows = []

    for year in years:
        metrics_path = os.path.join(metrics_dir, f"R_{category}_{year}.csv")

        if not os.path.exists(metrics_path):
            print(f"⚠ Missing file: {metrics_path}")
            continue

        print(f"Processing {metrics_path} ...")
        stats = compute_mean_std(metrics_path)
        stats["year"] = year
        summary_rows.append(stats)

    if not summary_rows:
        print(f"❌ No data found for {category}")
        return

    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df.sort_values("year")

    out_path = os.path.join(summary_dir, f"R_{category}_Full.csv")
    summary_df.to_csv(out_path, index=False)

    print(f"✅ Saved summary → {out_path}")


# ============================
# 批量生成 summary
# ============================
for cat in categories:
    print(f"\n=== Building summary for: {cat} ===")
    build_summary(cat)
