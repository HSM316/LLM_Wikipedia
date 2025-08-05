import pandas as pd

# 读取你的输出文件
df = pd.read_csv("Machine_Translation/Code/translate_and_evaluation/facebook_bertscore/result/zh_bertscore.csv")

# 找到所有以 bertscore_ 开头的列
bertscore_cols = [col for col in df.columns if col.startswith("bertscore")]

# 计算每个列的平均值
averages = df[bertscore_cols].mean()

# 打印结果
print("\n✅ 每个数值列的平均值：\n")
for col, avg in averages.items():
    print(f"{col}: {avg:.4f}")
