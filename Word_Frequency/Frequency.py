import os
import re
import json
from collections import defaultdict

# ============================================================
# 1. 加载 top words
# ============================================================

def load_top_words(file_path):
    top_words_set = set()
    top_words_list = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            if i > 10000:
                break
            word, _ = line.strip().split(',')
            top_words_list.append(word.lower())
            top_words_set.add(word.lower())
    return top_words_list, top_words_set


# ============================================================
# 2. 处理 JSONL 文件（替代旧 txt 逻辑）
# ============================================================

def process_jsonl(jsonl_path, time_point,
                  top_words_set, word_page_counts, total_words_per_time):

    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)

                title = data.get("title", "").lower()
                content = data.get("cleaned_content", "").lower()

                if not content:
                    continue

                words = re.findall(r'\b[a-zA-Z]+\b', content)

                word_counts = defaultdict(int)
                for w in words:
                    if w in top_words_set:
                        word_counts[w] += 1

                total_words_per_time[time_point] += sum(word_counts.values())

                for w, cnt in word_counts.items():
                    word_page_counts[w][time_point][title] = cnt

    except Exception as e:
        print(f"Error processing {jsonl_path}: {e}")


# ============================================================
# 3. 核心统计流程（纯 JSONL）
# ============================================================

def analyze_word_growth(category, pages_dir, output_file, total_words_file, word_list_file):

    # 2018-2025 年
    YEARS = list(range(2018, 2026))
    TIME_POINTS = [f"{year}-01-01" for year in YEARS]

    # 加载 top words
    top_words_list, top_words_set = load_top_words(word_list_file)

    # 初始化结构
    word_page_counts = {w: defaultdict(lambda: defaultdict(int)) for w in top_words_list}
    total_words_per_time = defaultdict(int)

    # ============================================================
    # 遍历 Wikipedia/Pages 下属于当前类别的所有年份 JSONL
    # 文件格式必须是：Category_YYYY_clean.jsonl
    # ============================================================

    for year in YEARS:
        filename = f"{category}_{year}.jsonl"
        file_path = os.path.join(pages_dir, filename)

        if os.path.isfile(file_path):
            print(f"[{category}] Processing {filename}")
            process_jsonl(file_path, f"{year}-01-01",
                          top_words_set, word_page_counts, total_words_per_time)
        else:
            print(f"[{category}] Missing: {filename}")

    # ============================================================
    # 计算频率
    # ============================================================

    word_frequencies = {}

    for w in top_words_list:
        word_frequencies[w] = {}
        for year in YEARS:
            tp = f"{year}-01-01"
            total = total_words_per_time[tp]
            count = sum(word_page_counts[w][tp].values())
            freq = count / total if total > 0 else 0
            word_frequencies[w][tp] = round(freq, 8)

        # f*
        f2018 = word_frequencies[w]["2018-01-01"]
        f2019 = word_frequencies[w]["2019-01-01"]
        word_frequencies[w]["f_star"] = round((f2018 + f2019) / 2, 8)

    # ============================================================
    # 输出 CSV
    # ============================================================

    with open(output_file, 'w', encoding='utf-8') as f:
        headers = ["Word"] + TIME_POINTS + ["f_star"]
        f.write(",".join(headers) + "\n")

        for w in top_words_list:
            row = [w] + [word_frequencies[w][tp] for tp in TIME_POINTS] + [word_frequencies[w]["f_star"]]
            f.write(",".join(map(str, row)) + "\n")

    # 输出 total words
    with open(total_words_file, 'w', encoding='utf-8') as f:
        f.write("Time Point,Total Words\n")
        for tp in TIME_POINTS:
            f.write(f"{tp},{total_words_per_time[tp]}\n")


# ============================================================
# 4. 多类别入口（统一入口）
# ============================================================

def process_all_categories(categories, pages_dir,
                           output_dir_template, total_words_template,
                           word_list_file):

    for category in categories:
        output_file = output_dir_template.format(category=category)
        total_words_file = total_words_template.format(category=category)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        os.makedirs(os.path.dirname(total_words_file), exist_ok=True)

        print(f"\n==== Category: {category} ====")
        analyze_word_growth(category, pages_dir,
                            output_file, total_words_file,
                            word_list_file)


# ============================================================
# 5. 主入口
# ============================================================

categories = ["Art", "Bio", "Chem", "CS", "Phy", "Math", "Philosophy", "Sports"]

pages_dir = "Wikipedia/clean_First"

output_dir_template = "LLM_Wikipedia/Word_Frequency/Frequency/First/f_{category}_First.csv"
total_words_template = "LLM_Impact/Word_Frequency/Total_Words/First/total_{category}_First_1.csv"

word_list_file = "LLM_Wikipedia/Word_Frequency/unigram_freq.csv"

process_all_categories(categories, pages_dir,
                       output_dir_template, total_words_template,
                       word_list_file)
