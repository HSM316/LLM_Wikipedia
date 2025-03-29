import json
import os
import re
from tqdm import tqdm
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# 初始化 DeepSeek 客户端（请替换为你的真实 API 密钥）
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

def generate_answer(question, topkans):
    try:
        prompt = (
            f"Use context to answer user questions. "
            f"Question: {question}\n"
            f"Reference context: {topkans}\n"
            f"Only need to give the correct option without explanation."
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error] {str(e)}"

def process_search_results(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        search_results = json.load(f)

    output_file = f"{os.path.splitext(input_file)[0]}_skoutput.txt"

    with open(output_file, 'w', encoding='utf-8') as out_f:
        for idx, result in enumerate(tqdm(search_results, desc=f"Processing {os.path.basename(input_file)}"), start=1):
            question = result["question"]
            top_3_answers = result["top_3_answers"]
            op = generate_answer(question, top_3_answers)
            out_f.write(f"answer{idx}: {op}\n")

    extract_answers_from_txt(output_file)

if __name__ == "__main__":
    input_files = []
    for year in range(2020, 2025):
        file_path = f"rebuttal/LLM_Wikipedia/RAG/ds(gemini_questions)/{year}/search_results_{year}.json"
        if os.path.exists(file_path):
            input_files.append(file_path)
        else:
            print(f"[Warning] File not found: {file_path}")

    # 使用线程池并发处理每一个 input_file
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_search_results, file): file for file in input_files}
        for future in as_completed(futures):
            file = futures[future]
            try:
                future.result()
                print(f"[Done] Finished processing: {file}")
            except Exception as exc:
                print(f"[Error] Failed to process {file}: {exc}")
