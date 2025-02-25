import json
import os
import re
import openai
client = openai.OpenAI(api_key="client = openai.OpenAI(api_key="<input_your_token>") ")
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
def process_questions_with_gpt(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    print(len(data))
    text = str(data)
    prompt = (
        f"Answer following questions. The format should be as per 1. C)..."
        f"Need answer all questions and mark the question number."
        f"Only need to give each answer, without explanation. Questions: {text}"
        f"The format should be as per 1. C)...\n2. C)..."
        f"All questions are required to be answered!! Don't skip any. "
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    answers = response.choices[0].message.content
    output_file_path = f"{os.path.splitext(json_file_path)[0]}_gptoutput.txt"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(answers)
    extract_answers_from_txt(output_file_path)
if __name__ == "__main__":
    process_questions_with_gpt("questions2021.json")
