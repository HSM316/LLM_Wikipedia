import csv
import matplotlib.pyplot as plt


def plot_bleu_table(file_names, languages, language_names):
    origin_bleu_scores = []
    gpt_bleu_scores = []

    for file_name in file_names:
        with open(file_name, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            origin_bleu_avg = float(rows[-2][1])
            gpt_bleu_avg = float(rows[-1][1])
            origin_bleu_scores.append(origin_bleu_avg)
            gpt_bleu_scores.append(gpt_bleu_avg)

    language_data = [
        (languages[i], origin_bleu_scores[i], gpt_bleu_scores[i], language_names[i])
        for i in range(len(languages))
    ]

    language_data.sort(key=lambda x: x[1], reverse=True)

    sorted_languages = [item[0] for item in language_data]
    sorted_origin_bleu_scores = [item[1] for item in language_data]
    sorted_gpt_bleu_scores = [item[2] for item in language_data]
    sorted_language_names = [item[3] for item in language_data]

    table_data = [["Language", "Origin chrf Avg", "GPT chrf Avg"]]
    for lang, origin, gpt, name in language_data:
        table_data.append([f"{lang} ({name})", f"{origin:.2f}", f"{gpt:.2f}"])

    fig, ax = plt.subplots(figsize=(8, len(table_data) * 0.6))  # 动态调整表格高度

    ax.axis('off')
    ax.axis('tight')

    table = ax.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(table_data[0]))))

    plt.title("chrf Scores for Google-t5 Models", fontsize=14)

    plt.tight_layout()
    plt.savefig("chrf_scores_table.png")
    plt.show()


languages = ['de', 'fr']
language_names = ['German', 'French']
file_names = [f"chrf_scores_{lang}.csv" for lang in languages]

plot_bleu_table(file_names, languages, language_names)
