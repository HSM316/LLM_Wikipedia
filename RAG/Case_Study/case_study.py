import json

def read_answers(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def calculate_accuracy(correct_answers, test_answers):
    correct = 0
    total = len(correct_answers)
    
    for key in correct_answers:
        if key in test_answers and correct_answers[key] == test_answers[key]:
            correct += 1
    
    return correct / total


def find_mismatched_questions(answers, rag_original_answers, rag_gemini_answers):
    mismatched_questions = []
    
    for question_id, correct_answer in answers.items():
        if rag_original_answers.get(question_id) == correct_answer and rag_gemini_answers.get(question_id) != correct_answer and rag_gemini_answers.get(question_id) != None:
            mismatched_questions.append(question_id)
    
    return mismatched_questions

def process_files(file_paths):
    answers = read_answers(file_paths[0])
    rag_original_answers = read_answers(file_paths[3])  
    rag_gemini_answers = read_answers(file_paths[4])  

    mismatched_questions = find_mismatched_questions(answers, rag_original_answers, rag_gemini_answers)

    return mismatched_questions


year = "2024"
file_paths = [f"RAG/4omini(gpt_questions)/{year}/answers{year}.json", 
              f"RAG/4omini(gpt_questions)/{year}/questions{year}_gptoutput.json",
              f"RAG/4omini(gpt_questions)/{year}/merged_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/merged_Gemini_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/merged_GPT_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/search_results_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/search_results_Gemini_{year}_gptoutput.json", 
              f"RAG/4omini(gpt_questions)/{year}/search_results_GPT_{year}_gptoutput.json", 
              ]
file_names = ["Answers", "Direct Ask", "Full Content(Original)", "Full Content(Gemini)", "Full Content(GPT)", "RAG(Original)", "RAG(Gemini)", "RAG(GPT)"]
reference_file = f"RAG/4omini(gpt_questions)/{year}/answers{year}.json"  

mismatched_questions = process_files(file_paths)

print("Mismatched Question IDs (RAG(Original) correct, RAG(Gemini) incorrect):")
for idx in mismatched_questions:
    print(idx)
