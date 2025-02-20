import pandas as pd   
import json

# First limitation: The Frequency of the selected words should be relatively higher
def load_ground_csv(file_path, threshold):
    df = pd.read_csv(file_path)
    filtered_words = df[df['f_star'].apply(lambda x: x != 0 and 1/x < threshold)]['Word'].tolist()
    return filtered_words

# Second limitation: The change rate of the selected words should be relatively higher
def load_r_csv(file_path, threshold):
    df_r = pd.read_csv(file_path)
    df_r.columns = df_r.columns.str.strip() 

    if 'r' not in df_r.columns or 'Word' not in df_r.columns:
        raise ValueError("wrong")

    def func(x):
        return (x + 1) / x**2 if x != 0 else float('inf')

    filtered_words = [row['Word'] for _, row in df_r.iterrows() if row['r'] != 0 and func(row['r']) < func(threshold)]
    return filtered_words

# Get the intersection of two word sets
def get_intersection(*lists):
    if not lists:
        return []
    return list(set(lists[0]).intersection(*lists[1:]))

def save_to_jsonl(results, output_file):

    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')

def main():
    r_file = 'LLM_Impact/Word_Frequency/Simulation/f_simple_r_First.csv'
    # The kind of pages you want to analyze: First or Full
    kind = 'First'

    categories = ['Art', 'Bio', 'Chem', 'CS', 'Math', 'Phy','Philosophy', 'Sports', 'simple', 'Featured']

    f_thresholds = [2000, 2500, 3000, 3500, 4000, 4500, 5000] 
    r_thresholds = [0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21, 0.23, 0.25, 0.27] 

    # Get different word combination
    output_dir = f'LLM_Impact/Estimation_Result/simple_First_eta/different/{kind}/words/'

    for category in categories:
        f_file = f'LLM_Impact/Word_Frequency/f_{kind}/f_{category}_{kind}.csv'
        output_file = f'{output_dir}{category}_{kind}_words.jsonl'

        results = []

        for ground_threshold in f_thresholds:
            for r_threshold in r_thresholds:
                filtered_words_f = load_ground_csv(f_file, ground_threshold)

                filtered_words_r = load_r_csv(r_file, r_threshold)

                intersection_words = get_intersection(filtered_words_f, filtered_words_r)

                results.append({
                    "category": category,
                    "ground_threshold": ground_threshold,
                    "r_threshold": r_threshold,
                    "word_count": len(intersection_words),
                    "words": intersection_words
                })
                if (len(intersection_words)) > 1000 or len(intersection_words) < 100:
                    print(category + " error")

        save_to_jsonl(results, output_file)
        print(f"Results for category {category} saved to {output_file}")


if __name__ == '__main__':
    main()
