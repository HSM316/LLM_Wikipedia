import json
import re

# 读取 txt 文件内容
with open("rebuttal/LLM_Wikipedia/RAG/ds(gemini_questions)/2020/search_results_Gemini_2020_skoutput.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 正则表达式：匹配 answer<number>: 后跟内容（支持跨多行）
pattern = re.compile(r"answer(\d+):\s*(.*?)(?=\nanswer\d+:|\Z)", re.DOTALL)

# 提取答案
answers = {}
for match in pattern.finditer(text):
    num = match.group(1)
    raw_answer = match.group(2).strip()
    
    # 查找是否有 A)/B)/C)/D) 开头
    option_match = re.match(r"([A-D])\)", raw_answer)
    if option_match:
        answer_letter = option_match.group(1)
    else:
        answer_letter = None  # 没有选项时设置为 null

    answers[f"answer{num}"] = answer_letter

# 写入 JSON 文件
with open("answers.json", "w", encoding="utf-8") as f:
    json.dump(answers, f, indent=2, ensure_ascii=False)

print("已保存为 answers.json")
