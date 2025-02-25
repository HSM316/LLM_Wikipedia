import json
import torch
from transformers import BertTokenizer, BertModel
import faiss
import numpy as np
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')
def load_knowledge_base(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line.strip()) for line in f]
    return data
def get_bert_embeddings(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)  
    return embeddings
def build_faiss_index(embeddings):
    embedding_array = embeddings.cpu().numpy().astype('float32')
    index = faiss.IndexFlatL2(embedding_array.shape[1])  
    index.add(embedding_array)
    return index
def query_faiss(query, index, knowledge_base, k=5):
    query_embedding = get_bert_embeddings([query]).cpu().numpy().astype('float32')
    _, indices = index.search(query_embedding, k)
    return [knowledge_base[i]['content'] for i in indices[0]]
def main():
    file_path = '2020_Gemini.jsonl'
    question_file = 'questions2020.json'
    output_file = "search_results_Gemini_2020.json"
    knowledge_base = load_knowledge_base(file_path)
    contents = [entry['content'] for entry in knowledge_base]
    content_embeddings = get_bert_embeddings(contents)
    faiss_index = build_faiss_index(content_embeddings)
    with open(question_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    search_results = []
    for key, question in questions.items():
        relevant_segments = query_faiss(question, faiss_index, knowledge_base, k=3)
        result = {
            "question": question,
            "top_3_answers": relevant_segments
        }
        search_results.append(result)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(search_results, f, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    main()
