import json
with open('answers2024.json', 'r', encoding='utf-8') as f:
    correct_answers = json.load(f)
with open('merged_Gemini_2024_gptoutput.json', 'r', encoding='utf-8') as f:
    user_answers = json.load(f)
correct=0
total=0
for question_number, correct_answer in correct_answers.items():
    user_answer = user_answers.get(question_number, None)
    total+=1
    if correct_answer == user_answer:
        correct += 1
accuracy = (correct / total) * 100 if total > 0 else 0
