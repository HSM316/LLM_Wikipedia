import json
import google.generativeai as genai

genai.configure(api_key="INPUT YOUR API_KEY")

def generate_questions(content):
    model = genai.GenerativeModel("INPUT YOUR MODEL")
    try:
        prompt = f"""
        You are to generate three self-contained multiple-choice questions based on the facts mentioned in the following content. Each question should include all relevant context and directly name any referenced items, avoiding pronouns like "it," "the game," or "the person." Do not include phrases that reference the source or context, such as "mentioned in the article" or "according to the text." Present the result in the following format:
        {{
          "questions": [
            {{
              "question": "QUESTION_1_TEXT",
              "options": ["OPTION_1", "OPTION_2", "OPTION_3", "OPTION_4"],
              "answer": "CORRECT_ANSWER_1"
            }},
            {{
              "question": "QUESTION_2_TEXT",
              "options": ["OPTION_1", "OPTION_2", "OPTION_3", "OPTION_4"],
              "answer": "CORRECT_ANSWER_2"
            }}
          ]
        }}
        Content: {content}
        """
        
        response = model.generate_content(contents=prompt)
        
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[len("```json"):].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-len("```")].strip()
        return cleaned_response
    
    except Exception as e:
        print(f"Error processing article\nError: {str(e)}\n\n")
        return None


def process_jsonl(input_file, output_file):
    output_data = []  
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            data = json.loads(line)
            title = data.get('title', '')
            content = data.get('content', '')
            
            generated_questions = generate_questions(content)
            
            if generated_questions:

                result = json.loads(generated_questions)
                result['title'] = title  
                output_data.append(result) 

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(output_data, outfile, ensure_ascii=False, indent=2)

# Example usage
year = "2020"
input_file = f'RAG/Plain_news/news_{year}.jsonl'  
output_file = f'RAG/Q_Gemini/Q_{year}_Gemini.json' 
process_jsonl(input_file, output_file)
