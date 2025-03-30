import json
import os
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI  # DeepSeek 使用 openai 客户端

# 初始化 DeepSeek 客户端（替换为你的 API 密钥）
client = OpenAI(
    api_key="",
    base_url="https://api.deepseek.com"
)

def extract_answers_from_txt(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    extracted_info = {}
    pattern = r"\b([A-D])\)"

    for idx, line in enumerate(lines, 1):
        line = line.strip()
        match = re.search(pattern, line)
        if match:
            extracted_info[f"answer{idx}"] = match.group(1)
        else:
            extracted_info[f"answer{idx}"] = None

    json_file_path = f"{os.path.splitext(txt_file_path)[0]}.json"
    with open(json_file_path, "w", encoding="utf-8") as outfile:
        json.dump(extracted_info, outfile, indent=4)

def process_data(question, content):
    try:
        prompt = (
            f"Use context to answer user questions. "
            f"question: {question}"
            f"Reference context: {content}. "
            f"Only need to give the correct option without explanation. Don't miss ')' or option!! "
            f"If there is no answer in the content, just return None. Don't give a string!!"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None

def process_jsonl_file(input_file):
    output_file = f"{os.path.splitext(input_file)[0]}_skoutput.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_file, "w", encoding="utf-8") as out_f:
        for idx, entry in enumerate(tqdm(data, desc=f"Processing {os.path.basename(input_file)}"), start=1):
            question = entry.get("question", "")
            content = entry.get("content", "")
            op = process_data(question, content)
            out_f.write(f"answer{idx}: {op}\n")

    extract_answers_from_txt(output_file)
    return output_file

if __name__ == "__main__":
    years = list(range(2020, 2025))
    questions = ["gemini", "gpt"]
    revisions = ["", "Gemini_", "GPT_"]
    input_files = []

    for year in years:
        for q in questions:
            for r in revisions:
                if q == "gemini" and r == "":
                    continue  # 跳过组合 (gemini, "")
                file_path = f"rebuttal/LLM_Wikipedia/RAG/ds({q}_questions)/{year}/merged_{r}{year}.json"
                if os.path.exists(file_path):
                    input_files.append(file_path)

    if not input_files:
        print("[Warning] No input files found.")
    else:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_jsonl_file, file): file for file in input_files}
            for future in as_completed(futures):
                file = futures[future]
                try:
                    output_path = future.result()
                    print(f"[Done] Processed {file} → {output_path}")
                except Exception as e:
                    print(f"[Error] Failed to process {file}: {e}")
