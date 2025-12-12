import os
import json
import time
import random
import argparse
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

import requests
from rich.progress import (
    Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
)

HEADERS = {
    'User-Agent': 'MyWikipediaScraper/1.0 (email@example.com)'
}


# ------------------------------- #
#   单标题爬取函数（子进程执行）
# ------------------------------- #
def fetch_single_title(args):
    title, target_dt = args

    url = "https://en.wikipedia.org/w/api.php"

    # 关键优化：使用 rvstart / rvend 直接缩小时间窗口
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvslots": "main",
        "rvprop": "ids|timestamp|content",
        "rvdir": "older",
        "rvstart": target_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rvlimit": 1,
        "format": "json"
    }

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if resp.status_code != 200:
            return {"title": title, "error": "API failed"}

        data = resp.json()
        pages = data.get("query", {}).get("pages", {})

        for pid, page in pages.items():
            if "missing" in page:
                return {"title": title, "error": "Missing page"}

            if "revisions" not in page:
                return {"title": title, "error": "No revision found"}

            r = page["revisions"][0]
            return {
                "title": title,
                "revid": r["revid"],
                "content": r["slots"]["main"].get("*", "")
            }

    except Exception as e:
        return {"title": title, "error": str(e)}




# ------------------------------- #
#   单类别爬取（内部使用）
# ------------------------------- #
def crawl_single_category(category_file, year, workers=8):
    category = category_file.replace("_titles.jsonl", "")

    titles_path = f"Wikipedia/Titles1/{category_file}"
    output_file = f"Wikipedia/Pages/{category}_{year}.jsonl"
    failed_file = f"Wikipedia/Pages/{category}_failed_{year}.jsonl"

    target_dt = datetime.strptime(f"{year}-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")

    titles = [
        json.loads(line)["title"]
        for line in open(titles_path, "r", encoding="utf-8")
    ]

    done = set()
    if os.path.exists(output_file):
        done = {
            json.loads(line)["title"]
            for line in open(output_file, "r", encoding="utf-8")
        }

    pending = [t for t in titles if t not in done]

    fout = open(output_file, "a", encoding="utf-8")
    ffail = open(failed_file, "a", encoding="utf-8")

    with Progress(
        TextColumn(f"[progress.description]{category} ({year})"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        TimeElapsedColumn(),
        "•",
        TimeRemainingColumn(),
        refresh_per_second=2,
    ) as progress:

        task = progress.add_task("Crawling...", total=len(titles))
        progress.update(task, advance=len(done))

        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(fetch_single_title, (title, target_dt)): title
                for title in pending
            }

            for future in as_completed(future_map):
                result = future.result()
                title = result["title"]

                if "error" in result:
                    ffail.write(json.dumps(result, ensure_ascii=False) + "\n")
                else:
                    fout.write(json.dumps(result, ensure_ascii=False) + "\n")

                progress.advance(task)

    fout.close()
    ffail.close()



# ------------------------------- #
#   主函数：自动读取所有标题文件
# ------------------------------- #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    titles_dir = "Wikipedia/Titles1"
    title_files = [f for f in os.listdir(titles_dir) if f.endswith("_titles.jsonl")]

    print(f"Detected categories: {title_files}")

    for file in title_files:
        crawl_single_category(file, args.year, args.workers)
