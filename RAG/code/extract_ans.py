import os
import re
import json
from glob import glob

# q类型和年份
q_list = ['gpt', 'gemini']
years = [str(y) for y in range(2020, 2025)]

# 正则匹配 answer<number>: 的答案内容（支持多行）
pattern = re.compile(r"answer(\d+):\s*(.*?)(?=\nanswer\d+:|\Z)", re.DOTALL)

for q in q_list:
    for year in years:
        folder_path = f"rebuttal/LLM_Wikipedia/RAG/ds({q}_questions)/{year}"
        txt_files = glob(os.path.join(folder_path, "*skoutput.txt"))

        for txt_file in txt_files:
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()

            answers = {}
            for match in pattern.finditer(text):
                num = match.group(1)
                raw_answer = match.group(2).strip()

                # 判断是否以 A)/B)/C)/D) 开头
                option_match = re.match(r"([A-D])\)", raw_answer)
                answer_letter = option_match.group(1) if option_match else None

                answers[f"answer{num}"] = answer_letter

            # 保存为 JSON 文件（同名，后缀变为 .json）
            json_path = txt_file.replace(".txt", ".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(answers, f, indent=2, ensure_ascii=False)

            print(f"处理文件: {txt_file}，提取答案数量: {len(answers)}")
