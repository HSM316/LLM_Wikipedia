import matplotlib.pyplot as plt    
import pandas as pd
import os
from typing import Dict, Any

color_map = {
    'Art': '#1f77b4',
    'Bio': '#ff7f0e',
    'Chem': '#2ca02c',
    'CS': '#d62728',
    'Math': '#8c564b',
    'Philosophy': '#e377c2',
    'Phy': '#7f7f7f',
    'Sports': '#17becf'
}


plt.rcParams.update({
    'font.size': 20, 
    'axes.titlesize': 16,
    'axes.labelsize': 16,
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'grid.color': 'gray',
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'figure.dpi': 150, 
    'figure.figsize': (12, 10)
})

KIND = "Full"  
BASE_FOLDER = f'LLM_Wikipedia/Linguistic_Style/Metrics/{KIND}'
SAVE_FOLDER = f'LLM_Wikipedia/Linguistic_Style/Figures/{KIND}'

COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#8c564b', '#e377c2', '#7f7f7f', '#17becf']

TITLE_MAPPING = {
    'Long_Sent_Rate': 'Long Sentence Rate',
    'Avg_Sent_Length': 'Average Sentence Length',
    'CTTR': 'Corrected Lexical Diversity (CTTR)',
    'Passive_Voice_Rate': 'Passive Voice Proportion',
    'Clause_Ratio': 'Clause Proportion',
    'Auxiliary_Verbs': 'Auxiliary Verbs Proportion',
    'ToBe_Verbs': "'To Be' Verbs Proportion",
    'Conjunctions': 'Conjunctions Proportion',
    'Prepositions': 'Prepositions Proportion',
    'Pronouns': 'Pronouns Proportion',
    'Nominalizations': 'Nouns Proportion',
    'Long_Words_Rate': 'Long Words Proportion',
    'OneSyllable_Rate': 'One-Syllable Words Proportion',
    'Syllables_Per_Word': 'Average Syllables per Word',
    'Start_Pronoun': 'Sentences Starting with Pronoun',
    'Start_Article': 'Sentences Starting with Article',
    'Avg_Parse_Tree_Depth': 'Average Parse Tree Depth',
}

PERCENT_METRICS = {
    "Long_Sent_Rate",
    "Passive_Voice_Rate",
    "Clause_Ratio",
    "Auxiliary_Verbs",
    "ToBe_Verbs",
    "Conjunctions",
    "Prepositions",
    "Pronouns",
    "Nominalizations",
    "Long_Words_Rate",
    "OneSyllable_Rate",
    "Start_Pronoun",
    "Start_Article"
}

def preprocess_data(base_folder: str) -> Dict[str, Dict[str, Any]]: 
    category_data = {}
    for filename in os.listdir(base_folder):
        if filename.startswith("S_") and filename.endswith(f"_{KIND}.csv"):
            category = filename[2:filename.rfind('_')]
            file_path = os.path.join(base_folder, filename)
            df = pd.read_csv(file_path)

            df['year'] = df['year'].astype(str).str.strip()
            df = df[df['year'].str.isdigit()]  # 仅保留数字年份
            df['year'] = df['year'].astype(int)

            metrics = [col.split('_mean')[0] for col in df.columns if col.endswith('_mean')]

            # 提取 2018 年的基准数据
            base_2018 = df[df['year'] == 2018].set_index('year')
            base_2019 = df[df['year'] == 2019].set_index('year')

            if not base_2018.empty and not base_2019.empty:
                for metric in metrics:
                    mean_col = f'{metric}_mean'
                    if mean_col in df.columns:
                        base_value = (base_2018[mean_col].values[0] + base_2019[mean_col].values[0]) / 2 # 2018 年的值
                        df[mean_col] = df[mean_col] - base_value  # 每年数据减去 2018 年的值

            category_data[category] = {'df': df, 'metrics': metrics}
    
    return category_data


def plot_and_save_metrics(category_data, save_folder, kind):
    os.makedirs(save_folder, exist_ok=True)

    all_years = sorted({
        year
        for data in category_data.values()
        for year in data['df']['year'].tolist()
    })

    metrics_to_plot = set(TITLE_MAPPING.keys())

    for metric in metrics_to_plot:
        fig, ax = plt.subplots(figsize=(8, 6))

        for category, data in category_data.items():
            if category in ['Featured', 'simple']:
                continue

            df = data['df'].copy().sort_values('year')
            mean_col = f"{metric}_mean"

            if mean_col not in df.columns:
                continue

            # 是否是百分比指标
            if metric in PERCENT_METRICS:
                df[mean_col] = df[mean_col] * 100
                ylabel = "Relative Value (%)"
            else:
                ylabel = "Relative Value"

            # 🔥 使用颜色映射
            color = color_map.get(category, '#000000')  # 若无匹配，用黑色兜底

            ax.plot(
                df['year'], df[mean_col],
                linestyle='--', marker='|',
                linewidth=1.5,
                color=color,
                label=category
            )

        ax.set_ylabel(ylabel)

        metric_title = TITLE_MAPPING.get(metric, metric)
        ax.set_title(f"{metric_title} Trend ({kind})", pad=20, x=0.5, y=0.87)

        ax.set_xticks(all_years)
        ax.set_xticklabels(all_years)

        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, 1.17),
            ncol=4,
            fontsize=12
        )

        plt.tight_layout(pad=2)

        save_path = os.path.join(save_folder, f"{metric}_{kind}.pdf")
        plt.savefig(save_path, dpi=150, bbox_inches='tight')



def main():
    category_data = preprocess_data(BASE_FOLDER)
    plot_and_save_metrics(category_data, SAVE_FOLDER, KIND)

if __name__ == "__main__":
    main()
