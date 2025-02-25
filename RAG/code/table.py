import pandas as pd
import matplotlib.pyplot as plt
import re
csv_file = 'rate.csv'  
df = pd.read_csv(csv_file)
def split_column_name(col_name):
    return re.sub(r'((?:[^\s]*\s){3})', r'\1\n', col_name)
new_columns = [split_column_name(col) for col in df.columns]
df.columns = new_columns
fig, ax = plt.subplots(figsize=(len(df.columns) * 2, len(df) * 0.5 + 2))  
ax.axis('off')  
table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
plt.title('RAG result/gpt-3.5 (Gemini questions)', fontsize=16, pad=20)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.8)  
plt.show()
