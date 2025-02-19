import os
import re
from datetime import datetime
import requests
import json
import time
import random
import csv
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

headers = {
    'User-Agent': 'MyWikipediaScraper/1.0 (myemail@example.com)'
}

FAILED_TITLES_FILE = "INPUT YOUR PATH TO FAILED TITLES"
REVIDS_CSV_FILE = "INPUT YOUR PATH TO STORE REVID"
INPUT_JSONL_FILE = 'INPUT YOUR PATH TO STORE TITLES'
OUTPUT_FOLDER = "INPUT YOUR PATH TO STORE WIKIPEDIA PAGES"


def fetch_url(url, params, max_retries=3):
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

def save_failed_title(title):

    with open(FAILED_TITLES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"title": title}) + "\n")

def get_every_edition():

    titles = []
    with open(INPUT_JSONL_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            entry = json.loads(line.strip())
            titles.append(entry)


    request_times = [
        "2025-01-01T00:00:00Z",
        "2024-01-01T00:00:00Z",
        "2023-01-01T00:00:00Z",
        "2022-01-01T00:00:00Z",
        "2021-01-01T00:00:00Z",
        "2020-01-01T23:00:00Z"
    ]

    request_times_dt = [datetime.strptime(rt, "%Y-%m-%dT%H:%M:%SZ") for rt in request_times]


    total_titles = len(titles)


    with open(REVIDS_CSV_FILE, "w", newline='', encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)

        header = ["title"] + [f"revid_{dt.strftime('%Y-%m-%d')}" for dt in request_times_dt]
        csv_writer.writerow(header)

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeElapsedColumn(),
            "•",
            TimeRemainingColumn(),
            refresh_per_second=1,
        ) as progress:
            task = progress.add_task("Processing titles...", total=total_titles)
            for title_entry in titles:
                title = title_entry.get("title")

                try:
                    sanitized_title = title.replace(" ", "_").replace(":", "_")
                    sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", sanitized_title)

                    revids = [None] * len(request_times_dt)
                    contents = ["No revision found."] * len(request_times_dt)

                    url = "https://en.wikipedia.org/w/api.php"
                    params = {
                        "action": "query",
                        "prop": "revisions",
                        "titles": title,
                        "rvlimit": "max",
                        "rvdir": "older",  
                        "rvprop": "timestamp|ids|flags|content",
                        "format": "json"
                    }

                    continue_token = None

                    current_request_index = 0

                    while True:
                        if continue_token:
                            params["rvcontinue"] = continue_token
                        response = fetch_url(url, params=params)
                        if not response:
                            raise Exception("Failed to fetch revisions.")
                        data = response.json()
                        pages = data.get('query', {}).get('pages', {})
                        for page_id, page_data in pages.items():
                            if 'redirect' in page_data:

                                raise Exception("Redirect detected.")
                            page_revisions = page_data.get('revisions', [])
                            for revision in page_revisions:
                                revision_time = datetime.strptime(revision['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

                                while (current_request_index < len(request_times_dt) and
                                       revision_time <= request_times_dt[current_request_index]):
                                    if revids[current_request_index] is None:
                                        revids[current_request_index] = revision['revid']
                                        contents[current_request_index] = revision.get('*', 'No content available')
                                    current_request_index += 1
                                    if current_request_index >= len(request_times_dt):
                                        break
                                if current_request_index >= len(request_times_dt):
                                    break
                        if "continue" in data and current_request_index < len(request_times_dt):
                            continue_token = data["continue"].get("rvcontinue")
                        else:
                            break


                    if any(rid is None for rid in revids):
                        raise Exception(f"Failed to fetch all revisions for {title}.")


                    folder_path = os.path.join(OUTPUT_FOLDER, sanitized_title)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    for idx, request_time in enumerate(request_times_dt):
                        date_str = request_time.strftime("%Y-%m-%d")
                        filename = f"ver_{date_str}.txt"
                        file_path = os.path.join(folder_path, filename)
                        if not os.path.exists(file_path):
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(contents[idx])

                    csv_writer.writerow([title] + revids)

                except Exception as e:
                    save_failed_title(title)
                finally:
                    progress.advance(task, 1)

def main():
    start_time = datetime.now()
    get_every_edition()
    end_time = datetime.now()
    print(f"Total runtime: {end_time - start_time}")

if __name__ == "__main__":
    main()
