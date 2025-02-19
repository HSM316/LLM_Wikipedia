import pandas as pd  
import json

def load_ground_csv(file_path, threshold):

    df = pd.read_csv(file_path)
    filtered_words = df[df['f_star'].apply(lambda x: x != 0 and 1/x < threshold)]['Word'].tolist()
    return filtered_words

def load_r_csv(file_path, threshold):

    df_r = pd.read_csv(file_path)
    df_r.columns = df_r.columns.str.strip()

    if 'r' not in df_r.columns or 'Word' not in df_r.columns:
        raise ValueError("wrong")

    def func(x):
        return (x + 1) / x**2 if x != 0 else float('inf')

    filtered_words = [row['Word'] for _, row in df_r.iterrows() if row['r'] != 0 and func(row['r']) < func(threshold)]
    return filtered_words

def get_intersection(filtered_words_1, filtered_words_2):

    return list(set(filtered_words_1).intersection(filtered_words_2))

def save_to_jsonl(results, output_file):

    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')

def main():
    ground_file = r'D:\WIKIPEDIA\new_Impact\f_simple_r_First.csv'
    r_file = ground_file
    output_file = r'D:\WIKIPEDIA\new_Impact\simple_First_eta\same\words_2.jsonl'


    ground_thresholds = [1000, 3000, 5000, 7000, 9000, 11000, 13000, 15000, 19000]  
    r_thresholds = [0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21, 0.23, 0.25, 0.27, 0.29]  

    results = []

    for ground_threshold in ground_thresholds:
        for r_threshold in r_thresholds:

            filtered_words_1 = load_ground_csv(ground_file, ground_threshold)

            filtered_words_2 = load_r_csv(r_file, r_threshold)

            intersection_words = get_intersection(filtered_words_1, filtered_words_2)

            results.append({
                "ground_threshold": ground_threshold,
                "r_threshold": r_threshold,
                "word_count": len(intersection_words),
                "words": intersection_words
            })

    save_to_jsonl(results, output_file)

    print(f"Results saved to {output_file}")

if __name__ == '__main__':
    main()