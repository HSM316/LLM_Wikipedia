import os
import pandas as pd
import numpy as np

base_dir = "Page_View/standard"
output_file = "pageviews_mean.csv"
ihs_output_file = "pageviews_ihs.csv"

def inverse_hyperbolic_sine(x):
    return np.log(x + np.sqrt(x**2 + 1))

csv_files = [f for f in os.listdir(base_dir) if f.endswith("_pageviews.csv")]

category_means = {}

for file in csv_files:
    category = file.replace("_pageviews.csv", "")
    file_path = os.path.join(base_dir, file)
    
    df = pd.read_csv(file_path)
    
    df = df.dropna()
    
    if 'Title' in df.columns:
        df = df.drop(columns=['Title'])
    
    mean_values = df.mean()
    
    category_means[category] = mean_values

result_df = pd.DataFrame.from_dict(category_means, orient='index')

result_df.index.name = 'Category'
result_df.reset_index(inplace=True)

result_df.to_csv(output_file, index=False)

ih_transformed_df = result_df.copy()
for col in ih_transformed_df.columns[1:]:  
    ih_transformed_df[col] = ih_transformed_df[col].apply(inverse_hyperbolic_sine)

ih_transformed_df.to_csv(ihs_output_file, index=False)

