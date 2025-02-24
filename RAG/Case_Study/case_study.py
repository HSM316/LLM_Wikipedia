import json

# 读取标准答案文件
def read_answers(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# 计算正确率
def calculate_accuracy(correct_answers, test_answers):
    correct = 0
    total = len(correct_answers)
    
    for key in correct_answers:
        if key in test_answers and correct_answers[key] == test_answers[key]:
            correct += 1
    
    return correct / total

# 找到所有RAG（Original）正确但RAG（Gemini）错误的问题序号
def find_mismatched_questions(rag_original_answers, rag_gemini_answers):
    mismatched_questions = []
    
    for question_id, correct_answer in rag_original_answers.items():
        if rag_gemini_answers.get(question_id) != correct_answer:
            mismatched_questions.append(question_id)
    
    return mismatched_questions

# 给每个文件命名并计算正确率
def process_files(file_paths, reference_file, file_names):
    reference_answers = read_answers(reference_file)
    rag_original_answers = read_answers(file_paths[5])  # 读取RAG(Original)的答案
    rag_gemini_answers = read_answers(file_paths[6])  # 读取RAG(Gemini)的答案
    results = {}

    mismatched_questions = find_mismatched_questions(rag_original_answers, rag_gemini_answers)

    for file_path, file_name in zip(file_paths, file_names):
        test_answers = read_answers(file_path)
        accuracy = calculate_accuracy(reference_answers, test_answers)
        results[file_name] = accuracy

    return results, mismatched_questions

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
reference_file = f"RAG/4omini(gpt_questions)/{year}/answers{year}.json"  # 以第一个文件作为标准答案

accuracy_results, mismatched_questions = process_files(file_paths, reference_file, file_names)

# 输出每个文件的正确率
for file_name, accuracy in accuracy_results.items():
    print(f"File: {file_name}, Accuracy: {accuracy:.4f}")

# 输出RAG(Original)正确但RAG(Gemini)错误的问题序号
print("Mismatched Question IDs (RAG(Original) correct, RAG(Gemini) incorrect):")
for idx in mismatched_questions:
    print(idx)
