import pandas as pd
import os

# List of input CSV filenames with their respective reference names
file_names_with_refs = [
    (r"D:\LLM_Wikipedia\RAG\4omini(gpt_questions)\rate.csv", "Qustion GPT-4o-mini with GPT Questions"),
    (r"D:\LLM_Wikipedia\RAG\4omini(gemini_questions)\rate.csv", "Qustion GPT-4o-mini with Gemini Questions"),
    (r"D:\LLM_Wikipedia\RAG\3.5(gpt_questions)\rate.csv", "Qustion GPT-3.5 with GPT Questions"),
    (r"D:\LLM_Wikipedia\RAG\3.5(gemini_questions)\rate.csv", "Qustion GPT-3.5 with Gemini Questions")
]

# Initialize an empty list to store results
results = []

# Process each file
for file_path, ref_name in file_names_with_refs:
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Remove the 'Quesion number' column
    df = df.drop(columns=['Quesion number', 'Year'])
    
    # Convert percentage values to numeric by removing '%' and dividing by 100
    for column in df.columns:
        if df[column].dtype == 'object':  # Check if the column contains string values
            df[column] = df[column].str.replace('%', '').astype(float) / 100
    
    # Calculate the average of each column for the years 2020 to 2024
    avg_accuracy = df.mean(axis=0)
    
    # Store the results (reference name and average accuracy for each column)
    result_row = [ref_name] + avg_accuracy.tolist()  # Use reference name instead of file path
    results.append(result_row)

# Convert the results into a DataFrame
columns = ['Questioning'] + df.columns.tolist()  # First column is the reference name, rest are accuracy columns
result_df = pd.DataFrame(results, columns=columns)

# Save the result to a new CSV file
result_df.to_csv(r"D:\LLM_Wikipedia\RAG\Case_Study\average_accuracy.csv", index=False)

print("Average accuracy CSV file has been created successfully.")
