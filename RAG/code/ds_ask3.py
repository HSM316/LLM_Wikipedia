import json
import os
import re
from openai import OpenAI  # 引入 DeepSeek 客户端库

# 初始化 DeepSeek 客户端（请替换为你的真实 API 密钥）
client = OpenAI(
    api_key="sk-16c010f6026d4fc390d16d07bc0d767f",
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
            f"Use the context below to answer the user's multiple-choice question.\n\n"
            f"Question: {question}\n\n"
            f"Reference Context:\n{topkans}\n\n"
            f"Only respond with the correct option letter (e.g., A, B, C, or D). Do not explain."
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
        for idx, result in enumerate(search_results, start=1):
            question = result["question"]
            top_3_answers = result["top_3_answers"]
            op = generate_answer(question, top_3_answers)
            out_f.write(f"answer{idx}: {op}\n")

    extract_answers_from_txt(output_file)

if __name__ == "__main__":
    process_search_results("rebuttal/LLM_Wikipedia/RAG/ds(gemini_questions)/2020/search_results_2020.json")
