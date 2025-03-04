import pandas as pd

file_names_with_refs = [
    ("RAG/4omini(gpt_questions)/rate.csv", "Qustion GPT-4o-mini with GPT Questions"),
    ("RAG/4omini(gemini_questions)/rate.csv", "Qustion GPT-4o-mini with Gemini Questions"),
    ("RAG/3.5(gpt_questions)/rate.csv", "Qustion GPT-3.5 with GPT Questions"),
    ("RAG/3.5(gemini_questions)/rate.csv", "Qustion GPT-3.5 with Gemini Questions")
]

results = []


for file_path, ref_name in file_names_with_refs:

    df = pd.read_csv(file_path)
    
    df = df.drop(columns=['Quesion number', 'Year'])
    
    for column in df.columns:
        if df[column].dtype == 'object': 
            df[column] = df[column].str.replace('%', '').astype(float) / 100
    

    avg_accuracy = df.mean(axis=0)
    
    result_row = [ref_name] + avg_accuracy.tolist() 
    results.append(result_row)


columns = ['Questioning'] + df.columns.tolist()  
result_df = pd.DataFrame(results, columns=columns)

result_df.to_csv("RAG/Case_Study/average_accuracy.csv", index=False)

print("Average accuracy CSV file has been created successfully.")
