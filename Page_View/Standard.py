import pandas as pd
import calendar

category = "Sports"
input_file = f"{category}_pageviews.csv"
output_file = f"Standard/{category}_pageviews.csv"

df = pd.read_csv(input_file)

months = df.columns[1:]

days_in_month = {str(y) + str(m).zfill(2): calendar.monthrange(y, m)[1]
                 for y in range(2020, 2026) for m in range(1, 13)}

for month in months:
    if month in days_in_month:
        df[month] = df[month] / days_in_month[month] * 30

df.to_csv(output_file, index=False)
