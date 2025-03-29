import json
import os
import re
from openai import OpenAI  # 使用 deepseek 的客户端库

# 初始化 DeepSeek 客户端（替换为你的 API key）
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

def process_questions_with_gpt(year):
    input_path = f"rebuttal/LLM_Wikipedia/RAG/4omini(gemini_questions)/{year}/questions{year}.json"
    with open(input_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"Processing year {year}, total questions: {len(data)}")
    text = str(data)
    prompt = (
        f"Answer following questions. The format should be as per 1. C)... "
        f"Need answer all questions and mark the question number. "
        f"Only need to give each answer, without explanation. Questions: {text} "
        f"The format should be as per 1. C)...\n2. C)... "
        f"All questions are required to be answered!! Don't skip any."
    )

    # 使用 DeepSeek API 调用
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )

    answers = response.choices[0].message.content
    output_path = f"rebuttal/LLM_Wikipedia/RAG/ds(gemini_questions)/question{year}_dsoutput.txt"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(answers)

    extract_answers_from_txt(output_path)

if __name__ == "__main__":
    for year in range(2020, 2025):  
        process_questions_with_gpt(year)
