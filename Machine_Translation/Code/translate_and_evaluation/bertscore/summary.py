import pandas as pd
from pathlib import Path

# 1. 输入文件夹
folder = Path("Machine_Translation/Code/translate_and_evaluation/Helsinki_bertscore/result")

# 2. 列出所有 *_bertscore.csv 文件
csv_files = sorted(folder.glob("*_helsinki.csv"))

# 3. 初始化列表，存放每种语言的平均值
all_averages = []

# 4. 逐个处理
for file in csv_files:
    print(f"处理文件: {file.name}")
    df = pd.read_csv(file)

    # 提取语言代码
    lang = file.name.split("_")[0]

    # 找出所有bertscore列
    bert_cols = [col for col in df.columns if col.startswith("bertscore")]

    # 计算平均值
    averages = df[bert_cols].mean()

    # 把结果放到一个字典里
    result = {"language": lang}
    for col in bert_cols:
        result[col] = averages[col]

    all_averages.append(result)

# 5. 汇总到一个DataFrame
summary_df = pd.DataFrame(all_averages)

# 6. 保存到CSV
output_file = "bertscore_helsinki.csv"
summary_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"\n✅ 已生成汇总文件: {output_file}")
