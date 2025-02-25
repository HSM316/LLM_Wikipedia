import json
with open('Q_2024_Gemini.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
questions_dict = {}
answers_dict = {}
for index, item in enumerate(data):
    for q_index, question_item in enumerate(item["questions"]):
        question_key = f"question{index*len(item['questions']) + q_index + 1}"
        answer_key = f"answer{index*len(item['questions']) + q_index + 1}"
        question_text = question_item["question"]
        options_text = "\n".join([f"{chr(65 + i)}) {option}" for i, option in enumerate(question_item["options"])])
        question_str = f'{question_text}  \n{options_text}'
        questions_dict[question_key] = question_str
        answers_dict[answer_key] = chr(65 + question_item["options"].index(question_item["answer"]))
with open('questions2024.json', 'w', encoding='utf-8') as f:
    json.dump(questions_dict, f, ensure_ascii=False, indent=4)
with open('answers2024.json', 'w', encoding='utf-8') as f:
    json.dump(answers_dict, f, ensure_ascii=False, indent=4)
