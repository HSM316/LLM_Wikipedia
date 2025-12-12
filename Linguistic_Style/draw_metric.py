import matplotlib.pyplot as plt    
import pandas as pd
import os
from typing import Dict, Any

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
    'figure.figsize': (8, 10)
})

KIND = "First"  
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

# TITLE_MAPPING = {
#     'Flesch Reading Ease': 'Flesch Reading Ease',
#     'Flesch-Kincaid Grade Level': 'Flesch-Kincaid Grade Level',
#     'Automated Readability Index (ARI)':'Automated Readability Index',
#     'Coleman-Liau Index':'Coleman-Liau Index',
#     'Gunning Fog Index':'Gunning Fog Index',
#     'Dale-Chall Readability Score':'Dale-Chall Readability Score'
# }

def preprocess_data(base_folder: str) -> Dict[str, Dict[str, Any]]:
    category_data = {}
    for filename in os.listdir(base_folder):
        if filename.startswith("S_") and filename.endswith(f"_{KIND}.csv"):
            # Extract category from filename (S_{category}_{kind}.csv)
            category = filename[2:filename.rfind('_')]  # This will give you the category between S_ and _{kind}
            file_path = os.path.join(base_folder, filename)
            df = pd.read_csv(file_path)
            df['year'] = df['year'].astype(str).str.strip()
            metrics = [col.split('_mean')[0] for col in df.columns if col.endswith('_mean')]
            category_data[category] = {'df': df, 'metrics': metrics}
    return category_data

def plot_and_save_metrics(category_data: Dict[str, Dict[str, Any]], save_folder: str, kind: str) -> None:
    os.makedirs(save_folder, exist_ok=True)

    all_years = set()
    all_metrics = set()
    for data in category_data.values():
        numeric_years = data['df'][data['df']['year'].str.isdigit()]['year'].astype(int)
        all_years.update(numeric_years)
        all_metrics.update(data['metrics'])
    all_years = sorted(all_years)

    metrics_to_plot = all_metrics.intersection(TITLE_MAPPING.keys())

    for metric in metrics_to_plot:
        fig, ax = plt.subplots(figsize=(8, 6)) 

        color_idx = 0
        for category, data in category_data.items():
            if category in ['Featured', 'simple']:
                continue

            df = data['df']
            numeric_df = df[df['year'].str.isdigit()].copy()
            if numeric_df.empty:
                continue
            numeric_df['year_numeric'] = numeric_df['year'].astype(int)
            numeric_df = numeric_df.sort_values('year_numeric')

            mean_col = f'{metric}_mean'
            if mean_col not in numeric_df.columns:
                continue

            line = ax.plot(numeric_df['year_numeric'], numeric_df[mean_col],
                           linestyle='-', marker='x', linewidth=1.5, color=COLORS[color_idx % len(COLORS)],
                           label=category)[0]
            color_idx += 1  

        ax.set_xlabel('Year')
        ax.set_ylabel(f'{metric.replace("_", " ")}')

        metric_title = TITLE_MAPPING.get(metric, metric)  
        ax.set_title(f'{metric_title} Trend ({kind})', pad=20, x=0.5, y=0.87,  # 尝试提高 y 值，给标题更多空间
                    fontsize=16)  

        ax.set_xticks(all_years)
        ax.set_xticklabels(all_years)
        ax.set_axisbelow(True) 

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), 
                ncol=4, frameon=True, fontsize=12)

        plt.tight_layout(pad=2)  # 自动调整边距

        # 计算y轴范围并为标题留出空间
        ymin, ymax = ax.get_ylim()
        title_height = 0.1  # 假设标题占用的高度为 10% 
        ax.set_ylim(ymin, ymax + (ymax - ymin) * title_height)  # 增加标题所需空间

        save_path = os.path.join(save_folder, f'{metric}_{kind}.pdf')
        # plt.show()
        plt.savefig(save_path,dpi = 150,bbox_inches='tight')
        plt.close()

# 调用 preprocess_data 和 main 方法与原来一样

def main():
    category_data = preprocess_data(BASE_FOLDER)
    plot_and_save_metrics(category_data, SAVE_FOLDER, KIND)

if __name__ == "__main__":
    main()