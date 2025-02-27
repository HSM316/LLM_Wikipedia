import json

def read_answers(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def output_answers_for_question(file_paths, file_names, question_number):
    answers = {}
    
    question_key = f"answer{question_number}"
    
    for file_path, file_name in zip(file_paths, file_names):
        answers[file_name] = None
        try:
            file_answers = read_answers(file_path)

            if question_key in file_answers:
                answers[file_name] = file_answers[question_key]
        except Exception as e:
            print(f"Error reading file {file_name}: {e}")
    
    return answers

year = "2024"
question = "gpt"
file_paths = [f"RAG/4omini({question}_questions)/{year}/answers{year}.json", 
              f"RAG/4omini({question}_questions)/{year}/questions{year}_gptoutput.json",
              f"RAG/4omini({question}_questions)/{year}/merged_{year}_gptoutput.json", 
              f"RAG/4omini({question}_questions)/{year}/merged_Gemini_{year}_gptoutput.json", 
              f"RAG/4omini({question}_questions)/{year}/merged_GPT_{year}_gptoutput.json", 
              f"RAG/4omini({question}_questions)/{year}/search_results_{year}_gptoutput.json", 
              f"RAG/4omini({question}_questions)/{year}/search_results_Gemini_{year}_gptoutput.json", 
              f"RAG/4omini({question}_questions)/{year}/search_results_GPT_{year}_gptoutput.json", 
              ]
file_names = ["Answers", "Direct Ask", "Full Content(Original)", "Full Content(Gemini)", "Full Content(GPT)", "RAG(Original)", "RAG(Gemini)", "RAG(GPT)"]

question_number = 122

answers = output_answers_for_question(file_paths, file_names, question_number)

print(f"Answers for question {question_number}:")
for file_name, answer in answers.items():
    print(f"{file_name}: {answer}")
