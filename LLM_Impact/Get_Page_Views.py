import requests
from urllib.parse import quote
import jsonlines  # type: ignore
import csv
from tqdm import tqdm
import time
import random
from datetime import datetime, timedelta

def fetch_url(url, params=None, max_retries=3, headers=None):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response
            else:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries - 1:
                print(f"Error fetching {url}. Retrying... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(random.uniform(1, 2))
            else:
                print(f"Failed to fetch {url} after {max_retries} attempts.")
                return None

def get_pageviews(session, title, start_date, end_date):

    encoded_title = quote(title)

    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{encoded_title}/monthly/{start_date}/{end_date}"

    headers = {
        "User-Agent": "MyWikiPageviewsApp/1.0 (https://example.com; myemail@example.com)"
    }

    response = fetch_url(url, headers=headers)

    if response is not None:
        return response.json()
    return None


def read_titles_from_jsonl(jsonl_file):
    titles = []
    with jsonlines.open(jsonl_file) as reader:
        for obj in reader:
            titles.append(obj['title'])
    return titles


def generate_months(start_date, end_date):
    start = datetime.strptime(start_date, "%Y%m01")
    end = datetime.strptime(end_date, "%Y%m01")
    current_month = start
    months = []

    while current_month <= end:
        months.append(current_month.strftime("%Y%m"))
        current_month += timedelta(days=32) 
        current_month = current_month.replace(day=1) 

    return months


def save_to_csv(data, csv_file, months):
    with open(csv_file, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            header = ['Title'] + months
            writer.writerow(header)

        for title, views in data.items():
            row = [title] + views
            writer.writerow(row)


categories = ["Phy", "Chem"]

start_date = "20200101"
end_date = "20250101"

for category in categories:
    jsonl_file = f'D:/WIKIPEDIA/Depth/add/{category}_titles.jsonl'  
    csv_file = f'D:/WIKIPEDIA/Depth/{category}_pageviews.csv' 

    titles = read_titles_from_jsonl(jsonl_file)


    months = generate_months(start_date, end_date)


    all_pageviews = {}
    for title in tqdm(titles, desc="Processing titles"):
        views_for_title = []
        pageviews = get_pageviews(None, title, start_date, end_date)
        if pageviews and 'items' in pageviews:

            pageview_dict = {entry['timestamp'][:6]: entry['views'] for entry in pageviews['items']}
            for month in months:
                views_for_title.append(pageview_dict.get(month, "N/A"))  
        else:
            print(f"Failed to fetch data for {title} between {start_date} and {end_date}")
            continue  
        
        all_pageviews[title] = views_for_title


        save_to_csv({title: views_for_title}, csv_file, months)

    print(f"Data saved to {csv_file}")
