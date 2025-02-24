import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to load and extract data from the CSV file
def load_and_extract_data(file_path):
    df = pd.read_csv(file_path)
    
    # Extract the 'Questioning' column as row labels
    questioning = df['Questioning'].values
    
    # Extract the percentage columns and convert to float
    data = df.iloc[:, 1:].values * 100  # Convert to percentage if needed
    
    return questioning, data

# File path for the single CSV file
file_path = r'RAG\Case_Study\average_accuracy.csv'

# Custom title for this file
custom_title = "Accuracy Heatmap of Different Questioning Pairs"

# Load and extract data
questioning, data = load_and_extract_data(file_path)

# Plotting
plt.figure(figsize=(12, 7))
cax = plt.imshow(data, aspect='auto', cmap='RdYlGn', interpolation='nearest', origin='lower')

# Adjust the ticks and labels
plt.xticks(np.arange(data.shape[1]), [
    "Direct Ask", 
    "RAG (Original)", 
    "RAG (GPT)", 
    "RAG (Gemini)", 
    "Full (Original)", 
    "Full (GPT)", 
    "Full (Gemini)"
], fontsize=17, rotation = 45)

plt.yticks(np.arange(len(questioning)), questioning, fontsize=17)

# Title for the plot
plt.title(custom_title, fontsize=20, pad=17)

# Add colorbar
cbar = plt.colorbar(cax)
cbar.ax.tick_params(labelsize=17)
cbar.set_label('Percentage (%)', fontsize=17, labelpad=17)

# Annotate the heatmap with the data values
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        text_color = 'black' if 70 < data[i, j] < 89 else 'white'  # Adjust text color based on value
        plt.text(j, i, f"{data[i, j]:.2f}", ha='center', va='center', color=text_color, fontsize=18)

plt.tight_layout()
plt.show()
