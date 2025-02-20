import json
import pandas as pd
import os

categories = ["Art", "Bio", "Chem", "CS", "Phy", "Math", "Philosophy", "Sports", "simple", "Featured"]

kind = "First"

# change rate after LLM Simulation
r_values_file = "LLM_Impact/Word_Frequency/Simulation/f_simple_r_First.csv"
# estimation result
output_dir = f"LLM_Impact/Estimation_Result/simple_First_eta/different/{kind}/" 

def load_r_values(filepath):
    df = pd.read_csv(filepath)
    r_dict = dict(zip(df["Word"], df["r"]))
    return r_dict

def load_f_values(filepath):
    df = pd.read_csv(filepath)
    f_dict = {}
    for _, row in df.iterrows():
        word = row["Word"]
        f_dict[word] = {
            "f_values": {year: row[year] for year in df.columns if year not in ["Word", "f_star"]},
            "f_star": row["f_star"]
        }
    return f_dict

def calculate_eta(I, r_dict, f_dict, years):
    results = []
    for year in years:
        numerator, denominator = 0.0, 0.0
        for word in I:
            if word in r_dict and word in f_dict:
                # f_d represents the frequency of word in the current corpus
                f_d = f_dict[word]["f_values"].get(year, 0.0)
                # f_star represents the one if LLMs do not affect Wikipedia pages
                f_star = f_dict[word]["f_star"]
                # r_i represents the frequency change rate
                r_i = r_dict[word]

                numerator += (f_d - f_star) * f_star * r_i
                denominator += (f_star * r_i) ** 2

        eta = numerator / denominator if denominator != 0 else 0.0
        results.append({"Year": year, "Eta": round(eta, 8)})

    return results


def append_result_to_jsonl(result, filepath):
    with open(filepath, 'a', encoding='utf-8') as file:
        file.write(json.dumps(result) + '\n')


def main():
    r_dict = load_r_values(r_values_file)
    years = ["2020-01-01", "2021-01-01", "2022-01-01", "2023-01-01", "2024-01-01", "2025-01-01"]


    for category in categories:
        # # word combination used to estimate LLM impact, different categories have different words
        words_file = f"LLM_Impact/Estimation_Result/simple_First_eta/different/{kind}/words/{category}_{kind}_words.jsonl"
        # the frequency of word in target corpus
        f_values_file = f"D:/WIKIPEDIA/Impact/f_{kind}/f_{category}_{kind}.csv"
        output_file = f"{output_dir}{category}_eta_{kind}.jsonl"
    
        f_dict = load_f_values(f_values_file)

        if os.path.exists(output_file):
            os.remove(output_file)

        with open(words_file, 'r', encoding='utf-8') as file:
            for line in file:
                data = json.loads(line)
                word_list = data.get("words", [])
                ground_threshold = data.get("ground_threshold", 0)
                r_threshold = data.get("r_threshold", 0.0)
                word_count = data.get("word_count", 0)

                eta_results = calculate_eta(word_list, r_dict, f_dict, years)

                result_entry = {
                    "ground_threshold": ground_threshold,
                    "r_threshold": r_threshold,
                    "word_count": word_count,
                    "eta_results": eta_results
                }
                append_result_to_jsonl(result_entry, output_file)

if __name__ == "__main__":
    main()
