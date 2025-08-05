import pandas as pd
from pathlib import Path

# 1. 输入文件夹路径
input_folder = Path("Machine_Translation/Google-t5/bleu_scores")

# 2. 输出文件夹路径
output_folder = Path("Machine_Translation/Code/translate_and_evaluation/google_bertscore/dataset")
output_folder.mkdir(parents=True, exist_ok=True)

# 3. 找到所有CSV文件
csv_files = sorted(input_folder.glob("bleu_scores_*.csv"))

# 4. 逐个处理
for file in csv_files:
    print(f"\n处理文件: {file.name}")
    df = pd.read_csv(file)

    before_rows = len(df)

    # 5. 自动找出唯一的 translated* 列
    translated_cols = [col for col in df.columns if col.startswith("translated")]
    if not translated_cols:
        print("⚠️ 未找到以 'translated' 开头的列，跳过此文件。")
        continue
    if len(translated_cols) > 1:
        print("⚠️ 找到多个以 'translated' 开头的列，跳过此文件。")
        continue

    translated_col = translated_cols[0]
    print(f"✅ 检测到翻译列: {translated_col}")

    # 6. 保留所需列
    required_cols = ["id", translated_col, "origin_translation", "gpt_translation"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"⚠️ 缺少列 {missing_cols}，跳过此文件。")
        continue

    df_subset = df[required_cols]

    # 7. 删除含空值行
    df_clean = df_subset.dropna()

    after_rows = len(df_clean)

    # 8. 新文件名（只保留xx.csv）
    lang_code = file.stem.split("_")[-1]  # e.g., 'ar'
    output_file = output_folder / f"{lang_code}.csv"

    # 9. 保存新文件
    df_clean.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"✅ 删除了 {before_rows - after_rows} 行空值")
    print(f"✅ 新文件已保存: {output_file}")
