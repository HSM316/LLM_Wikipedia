import json
import os
import csv

def calculate_accuracy(correct_answers_file, user_answers_file, null_score=0.25):
    with open(correct_answers_file, 'r', encoding='utf-8') as f:
        correct_answers = json.load(f)
    with open(user_answers_file, 'r', encoding='utf-8') as f:
        user_answers = json.load(f)

    correct = 0
    total = len(correct_answers)

    for q_id, correct_ans in correct_answers.items():
        user_ans = user_answers.get(q_id)
        if user_ans is None:
            correct += null_score
        elif user_ans == correct_ans:
            correct += 1

    accuracy = (correct / total) * 100 if total > 0 else 0
    return f"{accuracy:.2f}%"


def batch_calculate_accuracy(years, user_files_grid, base_dir, null_score):
    results = []
    for year, user_files in zip(years, user_files_grid):
        correct_file = os.path.join(base_dir, f"4omini(gpt_questions)/{year}/answers{year}.json")
        row_results = []
        for filename in user_files:
            user_file = os.path.join(base_dir, f"ds(gpt_questions)/{year}/{filename}")
            accuracy = calculate_accuracy(correct_file, user_file, null_score)
            row_results.append(accuracy)
        results.append(row_results)
    return results


def write_results_to_csv(years, results, output_file):
    headers = ['Year'] + [f'File{i+1}' for i in range(len(results[0]))]
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for year, row in zip(years, results):
            writer.writerow([year] + row)


def generate_user_files_grid(years):
    prefixes = ['question', 'search_results', 'search_results_GPT', 'search_results_Gemini',
                'merged', 'merged_GPT', 'merged_Gemini']
    user_files_grid = []

    for year in years:
        files = []
        for prefix in prefixes:
            if prefix == 'question':
                filename = f"{prefix}{year}_skoutput.json"  # 无下划线
            else:
                filename = f"{prefix}_{year}_skoutput.json"
            files.append(filename)
        user_files_grid.append(files)
    
    return user_files_grid


# 主流程
if __name__ == "__main__":
    years = ['2020', '2021', '2022', '2023', '2024']
    base_dir = "rebuttal/LLM_Wikipedia/RAG"
    user_files_grid = generate_user_files_grid(years)

    # 模式 1：null = 0 分（strict）
    results_strict = batch_calculate_accuracy(years, user_files_grid, base_dir, null_score=0.0)
    output_csv_strict = os.path.join(base_dir, "ds(gpt_questions)/raten_strict.csv")
    write_results_to_csv(years, results_strict, output_csv_strict)

    # 模式 2：null = 0.25 分（lenient）
    results_lenient = batch_calculate_accuracy(years, user_files_grid, base_dir, null_score=0.25)
    output_csv_lenient = os.path.join(base_dir, "ds(gpt_questions)/raten_lenient.csv")
    write_results_to_csv(years, results_lenient, output_csv_lenient)
