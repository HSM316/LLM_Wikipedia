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
def process_data(question, content):
    try:
        prompt = (
            f"Use context to answer user questions. "
            f"question: {question}"
            f"Reference context: {content}. "
            f"Only need to give the correct option without explanation. Don't miss ')' or option!! "
            f"If there is no answer in the content, just return None. Don't give a string!!"
        )
        response= client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[{"role": "user", "content": prompt}]
        )
        op = response.choices[0].message.content
        return op
    except Exception as e:
        return None
def process_jsonl_file(input_file):
    output_file = f"{os.path.splitext(input_file)[0]}_gptoutput.txt"
    with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out_f:
        data = json.load(f)  
        cnt = 1
        for entry in data:
            question = entry.get("question", "")
            content = entry.get("content", "")
            op = process_data(question, content)
            out_f.write(f"answer{cnt}: {op}\n")
            cnt += 1
    extract_answers_from_txt(output_file)
    return output_file  
if __name__ == "__main__":
    output_file = process_jsonl_file("merged_Gemini_2024.json")
