import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms

selected_categories = ['Art', 'Bio', 'Chem', 'CS','Math', 'Philosophy', 'Phy', 'Sports']
use_ihs_transform = False

def inverse_hyperbolic_sine(x):
    return np.log(x + np.sqrt(x**2 + 1))

# 读取数据
df = pd.read_csv('Page_View/daily_avg_pageviews.csv')
df['Date'] = pd.to_datetime(df['Date'].astype(str).str.slice(0, 8), format='%Y%m%d')

# 配色
color_map = {
    'Art': '#1f77b4', 'Bio': '#ff7f0e', 'Chem': '#2ca02c', 'CS': '#d62728',
    'Featured': '#9467bd', 'Math': '#8c564b', 'Philosophy': '#e377c2',
    'Phy': '#7f7f7f', 'simple': '#bcbd22', 'Sports': '#17becf'
}

# 筛选类别列
category_cols = df.columns[1:]
if selected_categories:
    category_cols = [col for col in category_cols if col in selected_categories]

# 应用 IHS 变换
for col in category_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    if use_ihs_transform:
        df[col] = df[col].apply(lambda x: inverse_hyperbolic_sine(x) if pd.notna(x) else np.nan)

start_date = df['Date'].min()
end_date = df['Date'].max()

# 调整为单栏论文图像尺寸（3.5 英寸宽）
fig, ax = plt.subplots(figsize=(3.5, 3.2))  # 适合单栏图，约为 8.9cm × 5.1cm

ax.set_facecolor('white')
ax.yaxis.grid(True, linestyle='--', linewidth=0.3, color='gray')
ax.xaxis.grid(True, linestyle='--', linewidth=0.3, color='gray')

# 画图
for col in category_cols:
    ax.plot(df['Date'], df[col], label=col, linewidth=0.8, color=color_map.get(col, None))

title_type = "IHS-Transformed" if use_ihs_transform else "Average"
ax.set_title(f'{title_type} Pageviews', fontsize=8, pad=25)
ax.set_ylabel(f'{title_type} Pageviews', fontsize=7)

ax.tick_params(axis='both', labelsize=6)

# 控制x轴标签（每年一个，加终点）
years = pd.date_range(start='2020-01-01', end='2025-01-01', freq='YS')
xticks = list(years) + [end_date]
# xtick_labels = [d.strftime('%Y') for d in years] + [f'{end_date.strftime("%m-%d")}']
xtick_labels = [d.strftime('%Y%m%d') for d in years] + [f'{end_date.strftime("%Y%m%d")}']
ax.set_xticks(xticks)
ax.set_xticklabels(xtick_labels, fontsize=6)

# 调整最后一个标签位置
for label in ax.get_xticklabels():
    if label.get_text() == f'{end_date.strftime("%Y%m%d")}':
        label.set_transform(label.get_transform() +
                            transforms.ScaledTranslation(-0.25, 2, fig.dpi_scale_trans))

ax.axvline(x=end_date, color='red', linestyle='--', linewidth=0.6)

# 图例设置
ax.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.16),
    ncol=4,
    fontsize=5.5,
    handlelength=1.0,
    columnspacing=0.8
)

plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig("daily_views_avg_main.pdf", dpi=300, bbox_inches='tight')
plt.close()
