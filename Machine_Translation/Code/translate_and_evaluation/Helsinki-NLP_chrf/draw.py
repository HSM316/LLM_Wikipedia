import csv
import matplotlib.pyplot as plt


def plot_bleu_scores(file_names, languages, language_names):
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

    plt.figure(figsize=(10, 6))
    plt.plot(sorted_languages, sorted_origin_bleu_scores, marker='o', label='Origin chrf Avg', color='blue')
    plt.plot(sorted_languages, sorted_gpt_bleu_scores, marker='o', label='GPT chrf Avg', color='green')

    plt.title('chrf Score Comparison for Helsinki-NLP Models', fontsize=16)
    plt.xlabel('Languages', fontsize=14)
    plt.ylabel('chrf Score', fontsize=14)

    ticks = range(len(sorted_languages))
    labels = [f"{lang} ({name})" for lang, name in zip(sorted_languages, sorted_language_names)]
    plt.xticks(ticks, labels, rotation=45)

    plt.grid(alpha=0.5)
    plt.legend(fontsize=12)

    plt.tight_layout()
    plt.savefig('chrf_scores_comparison_sorted.png')

    plt.show()


languages = ['ar', 'de', 'es', 'fr', 'hi', 'it', 'jap', 'ko', 'pt', 'ru', 'zh']
language_names = ['Arabic', 'German', 'Spanish', 'French', 'Hindi', 'Italian', 'Japanese', 'Korean', 'Portuguese',
                  'Russian', 'Chinese']
file_names = [f"chrf_scores_{lang}.csv" for lang in languages]

plot_bleu_scores(file_names, languages, language_names)


