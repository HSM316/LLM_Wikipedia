import os
import pandas as pd
import numpy as np

# input_dir = "Data_Collection/page_view_new"
input_dir = "Wikipedia/PageViews"
output_csv = "LLM_Wikipedia/Page_View/page_view/pageviews.csv"

desired_cols = ['Art','Bio','Chem','CS','Phy','Math','Philosophy','Sports']
# desired_cols = ['de', 'en', 'es', 'fr']
csv_files = [f for f in os.listdir(input_dir) if f.endswith("_pageviews.csv")]

cat_series = {}  # {category: Series(index=Date(str), values=mean)}

for file in csv_files:
    category = file.replace("_pageviews_daily.csv", "")
    file_path = os.path.join(input_dir, file)

    df = pd.read_csv(file_path)

    # 1) 删 Title，避免参与缺失判断与均值
    if 'Title' in df.columns:
        df = df.drop(columns=['Title'])

    # 2) 把所有列尽可能转为数值（无法转的变 NaN）
    df = df.apply(pd.to_numeric, errors='coerce')

    # 3) **复刻旧逻辑**：按行 dropna（行内任一列缺失则整行丢弃）
    df = df.dropna(how='any')

    if df.empty:
        continue

    # 4) 对每一列（每个时间戳）取均值
    mean_series = df.mean(axis=0, skipna=False)  # 行已dropna，无需 skipna
    mean_series.index = mean_series.index.map(str)
    cat_series[category] = mean_series

# 没有数据就不写
if not cat_series:
    print("No category mean data found. Nothing to append.")
else:
    new_df = pd.DataFrame(cat_series)
    new_df.index.name = 'Date'

    # 与已有文件“按日期对齐后合并”：旧值保留 or 新值覆盖？看你的需求：
    # 若要“以新计算为准覆盖旧值”，用下面覆盖逻辑（多数场景更直观）：
    if os.path.exists(output_csv):
        exist_df = pd.read_csv(output_csv, dtype={'Date': str}).set_index('Date')
        # 以索引对齐，把 new_df 的值覆盖到 exist_df 对应位置
        combined = exist_df.combine(new_df, lambda old, new: new, overwrite=True)
    else:
        combined = new_df

    # 列顺序：期望列在前，其他在后
    front = [c for c in desired_cols if c in combined.columns]
    tail = [c for c in combined.columns if c not in front]
    combined = combined[front + tail]

    combined = combined.sort_index()
    combined.reset_index().to_csv(output_csv, index=False)

    print(f"Wrote daily means (strict row-wise dropna) into: {output_csv}")
