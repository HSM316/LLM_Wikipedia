import os
import re
import json
from collections import defaultdict

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

def read_file(file_path, encodings=("utf-8", "ISO-8859-1")):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except Exception:
            continue
    raise ValueError(f"{file_path}")

def load_jsonl(jsonl_file):
    folder_titles = set()
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                folder_titles.add(data.get("title", "").lower())
    except Exception as e:
        print(f"Error reading jsonl file {jsonl_file}: {e}")
    return folder_titles

def calculate_frequency(total_count, current_total_words):
    if current_total_words == 0:
        return 0
    return total_count / current_total_words

def analyze_word_growth(root_dir, output_file, word_list_file, total_words_file, process_revised=False, jsonl_file=None):
    TIME_POINTS = [
        ("2020", "01-01"), 
        ("2021", "01-01"), 
        ("2022", "01-01"), 
        ("2023", "01-01"), 
        ("2024", "01-01"), 
        ("2025", "01-01")
    ]
    top_words_list, top_words_set = load_top_words(word_list_file)

    if jsonl_file:
        folder_titles_to_process = load_jsonl(jsonl_file)
    else:
        folder_titles_to_process = None

    word_page_counts = {word: defaultdict(lambda: defaultdict(int)) for word in top_words_list}
    total_words_per_time_point = defaultdict(int) 

    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)

        if os.path.isdir(folder_path):
            if folder_titles_to_process and folder_name.lower() not in folder_titles_to_process:
                continue

            for year, date in TIME_POINTS:
                time_point = f"{year}-{date}"
                file_name = f"ver_{time_point}.txt"
                file_path = os.path.join(folder_path, file_name)

                if os.path.isfile(file_path):
                    try:
                        content = read_file(file_path).lower() 

                        words_in_file = re.findall(r'\b[a-zA-Z]+\b', content)

                        word_counts = defaultdict(int)
                        for word in words_in_file:
                            if word in top_words_set:
                                word_counts[word] += 1
                        total_words_per_time_point[time_point] += sum(word_counts.values())

                        for word, count in word_counts.items():
                            word_page_counts[word][time_point][folder_name] = count

                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
            
            if process_revised:
                revised_file_name = "ver_revised.txt"
                revised_file_path = os.path.join(folder_path, revised_file_name)
                if os.path.isfile(revised_file_path):
                    try:

                        content = read_file(revised_file_path).lower() 
                        words_in_file = re.findall(r'\b[a-zA-Z]+\b', content)

                        word_counts = defaultdict(int)
                        for word in words_in_file:
                            if word in top_words_set: 
                                word_counts[word] += 1
                        total_words_per_time_point["revised"] += sum(word_counts.values())

                        for word, count in word_counts.items():
                            word_page_counts[word]["revised"][folder_name] = count

                    except Exception as e:
                        print(f"Error reading {revised_file_path}: {e}")
        else:
            print("error: " + folder_path)
    
    word_frequencies = {}
    for word in top_words_set:
        word_frequencies[word] = {}

        for year, date in TIME_POINTS:
            time_point = f"{year}-{date}"
            current_total_words = total_words_per_time_point[time_point] if time_point != "revised" else total_words_per_time_point["revised"]

            total_count = sum(word_page_counts[word][time_point].values())
            frequency = calculate_frequency(total_count, current_total_words)
            word_frequencies[word][time_point] = round(frequency, 8)
        
        if process_revised:
            total_count = sum(word_page_counts[word]["revised"].values())
            frequency = calculate_frequency(total_count, total_words_per_time_point["revised"])
            word_frequencies[word]["revised"] = round(frequency, 8)
    
    for word in word_frequencies:
        freq_2020 = word_frequencies[word].get("2020-01-01", 0)
        freq_2021 = word_frequencies[word].get("2021-01-01", 0)
        f_star = (freq_2020 + freq_2021) / 2  
        word_frequencies[word]["f_star"] = round(f_star, 8)

    with open(output_file, 'w', encoding='utf-8') as f:
        headers = ["Word"] + [f"{year}-{date}" for year, date in TIME_POINTS] + (["revised"] if process_revised else []) + ["f_star"]
        f.write(",".join(headers) + "\n")

        for word in top_words_list:
            row = [word] + [word_frequencies[word].get(f"{year}-{date}", 0) for year, date in TIME_POINTS]
            if process_revised:
                row.append(word_frequencies[word].get("revised", 0))
            row.append(word_frequencies[word].get("f_star", 0))
            row = [str(value) for value in row]
            f.write(",".join(row) + "\n")

    with open(total_words_file, 'w', encoding='utf-8') as f:
        f.write("Time Point,Total Words\n")
        for time_point, total_words in total_words_per_time_point.items():
            f.write(f"{time_point},{total_words}\n")

def process_multiple_categories(categories, root_dir_template, output_dir_template, word_list_file, total_words_dir_template, process_revised=False, jsonl_file=None):
    for category in categories:
        root_directory = root_dir_template.format(category=category)
        output_file_path = output_dir_template.format(category=category)
        total_words_file_path = total_words_dir_template.format(category=category)
        
        print(f"Processing category: {category}")
        analyze_word_growth(root_directory, output_file_path, word_list_file, total_words_file_path, process_revised, jsonl_file)

categories = ['Featured']  
root_dir_template = "D:/Category/{category}/{category}_Full"
output_dir_template = "D:/WIKIPEDIA/Impact/f_Full/f_{category}_Full.csv"
total_words_dir_template = "D:/WIKIPEDIA/Impact/total_words/Full/total_{category}_Full.csv"
word_list_file = "D:/WIKIPEDIA/unigram_freq.csv"

process_revised = False  
jsonl_file = "D:\WIKIPEDIA\dataset\Featured_impact_titles.jsonl"
process_multiple_categories(categories, root_dir_template, output_dir_template, word_list_file, total_words_dir_template, process_revised, jsonl_file)
