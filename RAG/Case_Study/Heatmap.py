import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_and_extract_data(file_path):
    df = pd.read_csv(file_path)
    
    questioning = df['Questioning'].values
    
    questioning = [q.replace("A:", "\nA:") for q in questioning]
    
    data = df.iloc[:, 1:].values * 100  
    
    return questioning, data

file_path = 'RAG/Case_Study/average_accuracy.csv'

custom_title = "Accuracy Heatmap of Different Questioning Pairs"

questioning, data = load_and_extract_data(file_path)

plt.figure(figsize=(12, 7))
cax = plt.imshow(data, aspect='auto', cmap='RdYlGn', interpolation='nearest', origin='lower')

plt.xticks(np.arange(data.shape[1]), [
    "Direct Ask", 
    "RAG (Original)", 
    "RAG (GPT)", 
    "RAG (Gemini)", 
    "Full (Original)", 
    "Full (GPT)", 
    "Full (Gemini)"
], fontsize=17, rotation=45, ha='right') 


plt.gca().tick_params(axis='x') 

plt.yticks(np.arange(len(questioning)), questioning, fontsize=17)
plt.gca().tick_params(axis='y', pad=13)

plt.title(custom_title, fontsize=20, pad=17)


cbar = plt.colorbar(cax)
cbar.ax.tick_params(labelsize=17)
cbar.set_label('Percentage (%)', fontsize=17, labelpad=17)

for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        text_color = 'black' if 70 < data[i, j] < 89 else 'white' 
        plt.text(j, i, f"{data[i, j]:.2f}", ha='center', va='center', color=text_color, fontsize=18)

plt.tight_layout()
plt.show()
