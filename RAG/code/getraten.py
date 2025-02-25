import json
import os
import csv
def calculate_accuracy(correct_answers_file, user_answers_file):
    with open(correct_answers_file, 'r', encoding='utf-8') as f:
        correct_answers = json.load(f)
    with open(user_answers_file, 'r', encoding='utf-8') as f:
        user_answers = json.load(f)
    correct = 0
    total = 0
    for question_number, correct_answer in correct_answers.items():
        user_answer = user_answers.get(question_number, None)
        total += 1
        if correct_answer == user_answer:
            correct += 1
        elif user_answer == None:
            correct +=0.25
    accuracy = (correct / total) * 100 if total > 0 else 0
    return f"{accuracy:.2f}%"
def batch_calculate_accuracy(correct_files, user_files_grid):
    """
    correct_files: list of 5 correct answer file paths
    user_files_grid: list of 5 lists, each containing 7 user answer file paths
    """
    results = []
    for i, correct_file in enumerate(correct_files):
        row_results = []
        for user_file in user_files_grid[i]:
            accuracy = calculate_accuracy(correct_file, user_file)
            row_results.append(accuracy)
        results.append(row_results)
    return results
def write_results_to_csv(results, output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    for i, row in enumerate(results):
        rows[i + 1][1:] = row
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
correct_files = ['answers2020.json', 'answers2021.json', 'answers2022.json', 'answers2023.json', 'answers2024.json']
user_files_grid = [
    ['questions2020_gptoutput.json', 'search_results_2020_gptoutput.json', 'search_results_GPT_2020_gptoutput.json', 'search_results_Gemini_2020_gptoutput.json', 'merged_2020_gptoutput.json', 'merged_GPT_2020_gptoutput.json', 'merged_Gemini_2020_gptoutput.json'],
    ['questions2021_gptoutput.json', 'search_results_2021_gptoutput.json', 'search_results_GPT_2021_gptoutput.json', 'search_results_Gemini_2021_gptoutput.json', 'merged_2021_gptoutput.json', 'merged_GPT_2021_gptoutput.json', 'merged_Gemini_2021_gptoutput.json'],
    ['questions2022_gptoutput.json', 'search_results_2022_gptoutput.json', 'search_results_GPT_2022_gptoutput.json', 'search_results_Gemini_2022_gptoutput.json', 'merged_2022_gptoutput.json', 'merged_GPT_2022_gptoutput.json', 'merged_Gemini_2022_gptoutput.json'],
    ['questions2023_gptoutput.json', 'search_results_2023_gptoutput.json', 'search_results_GPT_2023_gptoutput.json', 'search_results_Gemini_2023_gptoutput.json', 'merged_2023_gptoutput.json', 'merged_GPT_2023_gptoutput.json', 'merged_Gemini_2023_gptoutput.json'],
    ['questions2024_gptoutput.json', 'search_results_2024_gptoutput.json', 'search_results_GPT_2024_gptoutput.json', 'search_results_Gemini_2024_gptoutput.json', 'merged_2024_gptoutput.json', 'merged_GPT_2024_gptoutput.json', 'merged_Gemini_2024_gptoutput.json']
]
results = batch_calculate_accuracy(correct_files, user_files_grid)
write_results_to_csv(results, 'raten.csv')
