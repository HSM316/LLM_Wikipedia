import os
import json
from openai import AzureOpenAI
from tqdm import tqdm

client = AzureOpenAI(
    api_key="INPUT YOUR API_KEY", 
    api_version="INPUT YOUR API_VERSION", 
    azure_endpoint="INPUT YOUR AZURE_ENDPOINT"
)

root_folder = "INPUT YOUR ROOT_FOLDER"
output_root_folder = root_folder

error_log_path = "INPUT YOUR PATH"

if not os.path.exists(output_root_folder):
    os.makedirs(output_root_folder)


error_folders = []

folder_list = os.listdir(root_folder)
for folder_name in tqdm(folder_list, desc="Processing Folders", unit="folder"): 
    folder_path = os.path.join(root_folder, folder_name)
    

    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, "ver_2022-01-01.txt")
        
        if os.path.exists(file_path):
            try:

                with open(file_path, 'r', encoding='utf-8') as file:
                    article_content = file.read()


                response = client.chat.completions.create(
                    model="",  
                    messages=[ 
                        {"role": "user", "content": f"Revise the following sentences:\n{article_content}"}
                    ]
                )
                
                revised_article = response.choices[0].message.content

                output_folder_path = os.path.join(output_root_folder, folder_name)
                if not os.path.exists(output_folder_path):
                    os.makedirs(output_folder_path)

                output_file_path = os.path.join(output_folder_path, f"ver_revised.txt")
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(revised_article)

                print(f"Revised article from folder '{folder_name}' saved to: {output_file_path}")

            except Exception as e:
                print(f"Error processing folder '{folder_name}': {e}")
                error_folders.append({"folder_name": folder_name, "error": str(e)})
                
                continue

if error_folders:
    with open(error_log_path, 'a', encoding='utf-8') as error_log_file:
        for error_entry in error_folders:
            error_log_file.write(json.dumps(error_entry) + "\n")
