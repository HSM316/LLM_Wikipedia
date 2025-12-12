import json
import csv
import os
import textstat
from tqdm import tqdm
from glob import glob

def calculate_metrics(text):
    if not text.strip():
        return None
    
    metrics = {}
    try:
        metrics = {
            'Flesch Reading Ease': textstat.flesch_reading_ease(text),
            'Flesch-Kincaid Grade Level': textstat.flesch_kincaid_grade(text),
            'Automated Readability Index (ARI)': textstat.automated_readability_index(text),
            'Coleman-Liau Index': textstat.coleman_liau_index(text),
            'Gunning Fog Index': textstat.gunning_fog(text),
            'Dale-Chall Readability Score': textstat.dale_chall_readability_score(text),
        }

    except Exception as e:
        print(f"{str(e)}")
        return None

    return metrics


def process_jsonl_file(jsonl_path, output_dir):
    results = []
    os.makedirs(output_dir, exist_ok=True)

    with open(jsonl_path, 'r', encoding='utf-8') as infile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)

        for line in tqdm(infile, total=total_lines,
                         desc=f"Processing {os.path.basename(jsonl_path)}", unit="line"):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            title = obj.get("title", "")
            content = obj.get("cleaned_content", "")  # ← 使用 cleaned_content

            metrics = calculate_metrics(content)
            if metrics:
                metrics["title"] = title
                results.append(metrics)

    if not results:
        print(f"No valid records in {jsonl_path}")
        return

    base = os.path.splitext(os.path.basename(jsonl_path))[0]
    output_csv_path = os.path.join(output_dir, f"R_{base}.csv")

    fieldnames = list(results[0].keys())
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved → {output_csv_path}")


# ============================================================
# 批量处理 Wikipedia/clean_First 下所有 JSONL
# ============================================================

input_dir = "Wikipedia/Extracted_Full"
output_dir = "Wikipedia/Readability/Full"
os.makedirs(output_dir, exist_ok=True)

jsonl_files = glob(os.path.join(input_dir, "*.jsonl"))
print(f"Found {len(jsonl_files)} JSONL files.")

for jsonl_path in jsonl_files:
    process_jsonl_file(jsonl_path, output_dir)
