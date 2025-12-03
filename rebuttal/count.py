import json
import re
import csv
from collections import defaultdict

# === 1. 加载 top words 词表（只取前10000个） ===
def load_top_words(word_list_file, top_n=10000):
    top_words = []
    with open(word_list_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == 0:  # 跳过表头
                continue
            if i > top_n:
                break
            word, _ = line.strip().split(",")
            top_words.append(word.lower())
    return top_words, set(top_words)

# === 2. 从 JSONL 文件中提取指定版本文本 ===
def load_versions(jsonl_file, versions_to_extract):
    version_texts = defaultdict(list)
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line.strip())
            for v in data.get("versions", []):
                date = v.get("date", "")
                if date in versions_to_extract:
                    version_texts[date].append(v.get("content", ""))
    return version_texts

# === 3. 计算词频 ===
def calculate_frequencies(version_texts, top_words_set):
    results = {}
    for version, texts in version_texts.items():
        word_counts = defaultdict(int)
        total_count = 0
        for text in texts:
            words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
            for w in words:
                if w in top_words_set:
                    word_counts[w] += 1
                    total_count += 1
        # 计算相对频率
        freq_dict = {w: (count / total_count if total_count > 0 else 0)
                     for w, count in word_counts.items()}
        results[version] = freq_dict
    return results

# === 4. 保存为 CSV 文件 ===
def save_to_csv(freqs, top_words_list, output_file, versions):
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        # 表头
        header = ["Word"] + versions + ["f_star", "r"]
        writer.writerow(header)
        # 每个词一行
        for word in top_words_list:
            row = [word]
            for v in versions:
                row.append(f"{freqs.get(v, {}).get(word, 0):.8f}")
            
            # === f_star: 2020 & 2021 的平均值 ===
            f2020 = freqs.get("2020-01-01", {}).get(word, 0)
            f2021 = freqs.get("2021-01-01", {}).get(word, 0)
            f_star = (f2020 + f2021) / 2

            # === r: (revised_3.5 - 2022) / 2022 ===
            f2022 = freqs.get("2022-01-01", {}).get(word, 0)
            frev = freqs.get("revised_3.5", {}).get(word, 0)
            r = (frev - f2022) / f2022 if f2022 > 0 else 0

            row.append(f"{f_star:.8f}")
            row.append(f"{r:.8f}")
            writer.writerow(row)

# === 主程序 ===
if __name__ == "__main__":
    jsonl_file = "/Users/hsm/Documents/Wikipedia_Pages/Featured_First_Revised.jsonl"
    word_list_file = "Word_Frequency/unigram_freq.csv"
    output_file = "rebuttal/Featured_First_2022_vs_Revised.csv"

    versions_to_extract = [
        "2020-01-01", "2021-01-01", "2022-01-01",
        "2023-01-01", "2024-01-01", "2025-01-01",
        "revised_3.5"
    ]

    # 加载词表
    top_words_list, top_words_set = load_top_words(word_list_file)

    # 加载 JSONL 指定版本文本
    version_texts = load_versions(jsonl_file, versions_to_extract)

    # 计算词频
    freqs = calculate_frequencies(version_texts, top_words_set)

    # 保存为 CSV
    save_to_csv(freqs, top_words_list, output_file, versions_to_extract)

    print(f"结果已保存到 {output_file} （已包含 f_star 和 r 列）")
