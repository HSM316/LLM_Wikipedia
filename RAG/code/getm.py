import json
with open('Q_2024_Gemini.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
title_content = {}
with open('2024_Gemini.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        entry = json.loads(line)
        title_content[entry["title"]] = entry["content"]
final_data = []
for item in data:
    title = item["title"]
    content = title_content.get(title, "")  
    for q_index, question_item in enumerate(item["questions"]):
        question_key = f"question{q_index + 1}"
        answer_key = f"answer{q_index + 1}"
        question_text = question_item["question"]
        options_text = "\n".join([f"{chr(65 + i)}) {option}" for i, option in enumerate(question_item["options"])])
        question_str = f'{question_text}  \n{options_text}'
        correct_answer = chr(65 + question_item["options"].index(question_item["answer"]))
        question_data = {
            "title": title,
            "content": content,
            "question": question_str,
            "correct_answer": correct_answer
        }
        final_data.append(question_data)
with open('merged_Gemini_2024.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)
