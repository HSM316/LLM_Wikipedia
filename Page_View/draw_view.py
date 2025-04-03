import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms

selected_categories = ['Art', 'Bio', 'Chem', 'CS', 'Featured', 'Math', 'Philosophy', 'Phy', 'simple', 'Sports'] 

use_ihs_transform = True

def inverse_hyperbolic_sine(x):
    return np.log(x + np.sqrt(x**2 + 1))

df = pd.read_csv('Page_View/daily_avg_pageviews.csv')

df['Date'] = pd.to_datetime(df['Date'].astype(str).str.slice(0, 8), format='%Y%m%d')


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

category_cols = df.columns[1:]
if selected_categories:
    category_cols = [col for col in category_cols if col in selected_categories]

for col in category_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    if use_ihs_transform:
        df[col] = df[col].apply(lambda x: inverse_hyperbolic_sine(x) if pd.notna(x) else np.nan)

start_date = df['Date'].min()
end_date = df['Date'].max()

fig, ax = plt.subplots(figsize=(14, 6))

ax.set_facecolor('white')
ax.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
ax.xaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')

for col in category_cols:
    ax.plot(df['Date'], df[col], label=col, color=color_map.get(col, None))

title_type = "IHS-Transformed" if use_ihs_transform else "Average"
plt.title(f'{title_type} Daily Pageviews', pad=45, fontsize=16)

ax.set_ylabel(f'{title_type} Daily Pageviews', fontsize=14)

ax.tick_params(axis='y', labelsize=12)

years = pd.date_range(start='2020-01-01', end='2025-01-01', freq='YS')
xticks = list(years) + [end_date]
xtick_labels = [d.strftime('%Y-%m-%d') for d in years] + [f'{end_date.strftime("%m-%d")}']
ax.set_xticks(xticks)
ax.set_xticklabels(xtick_labels, fontsize=12)

for label in ax.get_xticklabels():
    if label.get_text() == end_date.strftime('%m-%d'):
        label.set_transform(label.get_transform() +
                            transforms.ScaledTranslation(0.25, 0, fig.dpi_scale_trans))

ax.axvline(x=end_date, color='black', linestyle='--', linewidth=1)

ax.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.14),
    ncol=5,
    frameon=True,
)

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.show()
