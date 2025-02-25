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
def generate_answer(question, topkans):
    try:
        prompt = (
            f"Use context to answer user questions. "
            f"Question: {question}\n"
            f"Reference context: {topkans}\n"
            f"Only need to give the correct option without explanation."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return None
def process_search_results(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        search_results = json.load(f)
    output_file = f"{os.path.splitext(input_file)[0]}_gptoutput.txt"
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for idx, result in enumerate(search_results, start=1):
            question = result["question"]
            top_3_answers = result["top_3_answers"]
            op = generate_answer(question, top_3_answers)
            out_f.write(f"answer{idx}: {op}\n")
    extract_answers_from_txt(output_file)
if __name__ == "__main__":
    process_search_results("search_results_Gemini_2024.json")
