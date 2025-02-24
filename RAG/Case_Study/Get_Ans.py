import json

# 读取答案文件
def read_answers(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# 输出指定问题序号的答案
def output_answers_for_question(file_paths, file_names, question_number):
    answers = {}
    
    # 生成问题键（如 answer1, answer2）
    question_key = f"answer{question_number}"
    
    for file_path, file_name in zip(file_paths, file_names):
        answers[file_name] = None
        try:
            file_answers = read_answers(file_path)
            # 查找指定问题序号的答案
            if question_key in file_answers:
                answers[file_name] = file_answers[question_key]
        except Exception as e:
            print(f"Error reading file {file_name}: {e}")
    
    return answers

# 示例：文件路径列表和自定义的名称
year = "2024"
file_paths = [f"RAG/4omini(gpt_questions)/{year}/answers{year}.json", 
              f"RAG/4omini(gpt_questions)/{year}/questions{year}_gptoutput.json",
              f"RAG/4omini(gpt_questions)/{year}/merged_{year}_gptoutput.json", 
              f"D:/LLM_Wikipedia/RAG/4omini(gpt_questions)/{year}/merged_Gemini_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/merged_GPT_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/search_results_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/search_results_Gemini_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/search_results_GPT_{year}_gptoutput.json", 
              ]
file_names = ["Answers", "Direct Ask", "Full Content(Original)", "Full Content(Gemini)", "Full Content(GPT)", "RAG(Original)", "RAG(Gemini)", "RAG(GPT)"]  # 自定义文件名

# 输入问题序号
question_number = 4

# 获取指定问题序号的答案
answers = output_answers_for_question(file_paths, file_names, question_number)

# 输出结果
print(f"Answers for question {question_number}:")
for file_name, answer in answers.items():
    print(f"{file_name}: {answer}")
