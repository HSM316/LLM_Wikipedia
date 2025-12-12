import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms

# === 配置 ===
selected_categories = ['Art', 'Bio', 'Chem', 'CS','Math', 'Philosophy', 'Phy', 'Sports']
# selected_categories = ['de', 'en', 'es', 'fr']
use_ihs_transform = False          # 平滑后再进行 IHS 变换
rolling_window_days = 7           # 滑动窗口大小

def inverse_hyperbolic_sine(x: np.ndarray) -> np.ndarray:
    return np.log(x + np.sqrt(x**2 + 1))

# 月份缩写 + 句点格式化
MON_ABBR = {
    'Jan': 'Jan.', 'Feb': 'Feb.', 'Mar': 'Mar.', 'Apr': 'Apr.',
    'May': 'May',  'Jun': 'Jun.', 'Jul': 'Jul.', 'Aug': 'Aug.',
    'Sep': 'Sep.', 'Oct': 'Oct.', 'Nov': 'Nov.', 'Dec': 'Dec.'
}
def fmt_long(dt):
    """返回 'Jan. 1, 2020' 这种格式"""
    mon = MON_ABBR[dt.strftime('%b')]
    return f"{mon} {dt.day}, {dt.year}"

# === 读取数据 ===
df = pd.read_csv('LLM_Wikipedia/Page_View/pageviews.csv')
df['Date'] = pd.to_datetime(df['Date'].astype(str).str.slice(0, 8), format='%Y%m%d')
df = df.sort_values('Date').reset_index(drop=True)

# === 配色 ===
color_map = {
    'Art': '#1f77b4', 'Bio': '#ff7f0e', 'Chem': '#2ca02c', 'CS': '#d62728',
    'Featured': '#9467bd', 'Math': '#8c564b', 'Philosophy': '#e377c2',
    'Phy': '#7f7f7f', 'simple': '#bcbd22', 'Sports': '#17becf'
}

# color_map = {
#     'de': '#1f77b4',  # 蓝
#     'en': '#ff7f0e',  # 橙
#     'es': '#2ca02c',  # 绿
#     'fr': '#d62728',  # 红
# }


# === 筛选类别列 ===
category_cols = [c for c in df.columns if c != 'Date']
if selected_categories:
    category_cols = [col for col in category_cols if col in selected_categories]

# 确保数值型
for col in category_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# === 7 天滑动均值（右对齐，min_periods=7 确保第 7 天才开始有值）===
smooth_df = df.copy()
smooth_df[category_cols] = df[category_cols].rolling(window=rolling_window_days, min_periods=rolling_window_days).mean()

# === 平滑后再做 IHS 变换（可选）===
plot_df = smooth_df.copy()
if use_ihs_transform:
    plot_df[category_cols] = inverse_hyperbolic_sine(plot_df[category_cols].to_numpy())

start_date = plot_df['Date'].min()
end_date = plot_df['Date'].max()

# === 画图（单栏尺寸）===
fig, ax = plt.subplots(figsize=(12, 4))
ax.set_facecolor('white')
ax.yaxis.grid(True, linestyle='--', linewidth=0.3, color='gray', alpha=0.8)
ax.xaxis.grid(True, linestyle='--', linewidth=0.3, color='gray', alpha=0.8)

# 画每个类别（平滑后/可选 IHS 后）
for col in category_cols:
    ax.plot(plot_df['Date'], plot_df[col], label=col, linewidth=1.3, color=color_map.get(col, None))

title_suffix = ' (IHS)' if use_ihs_transform else ' (Mean)'
# ax.set_title('Pageviews Across Different Categories in English Wikipedia', fontsize=10, pad=7)
# ax.set_title('Pageviews Across Wikipedia of Different Languages', fontsize=10, pad=7)
ax.set_ylabel(f'Pageviews{title_suffix}', fontsize=8)
ax.tick_params(axis='both', labelsize=6)

# ===== X轴刻度：每年1月1日 + 终点，统一格式为 'Jan. 1, 2020' =====
years = pd.date_range(start='2018-01-01', end='2025-01-01', freq='YS')
xticks = list(years) + [end_date]
xtick_labels = [fmt_long(d) for d in years] + [fmt_long(end_date)]
ax.set_xticks(xticks)
ax.set_xticklabels(xtick_labels, fontsize=8)

# 调整最后一个标签位置（保持你原来的视觉微调）
for label in ax.get_xticklabels():
    if label.get_text() == fmt_long(end_date):
        label.set_transform(label.get_transform() + transforms.ScaledTranslation(0, 0, fig.dpi_scale_trans))

# 终点辅助线
# ax.axvline(x=end_date, color='red', linestyle='--', linewidth=0.6)

# 图例
ax.legend(
    loc='upper center',
    bbox_to_anchor=(0.09, 1),
    ncol=2,
    fontsize=10,
    handlelength=1.0,
    columnspacing=0.8
)

plt.tight_layout(rect=[0, 0, 1, 0.92])

# 动态命名导出文件
suffix = '_ihs' if use_ihs_transform else ''
outname = f"LLM_Wikipedia/Page_View/daily_views_{suffix}.pdf"
plt.savefig(outname, dpi=300, bbox_inches='tight')
plt.close()
