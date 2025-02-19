import requests 
import time
import random
import json
import os
headers = {
    'User-Agent': 'MyWikipediaScraper/1.0 (myemail@example.com)'
}

# General request function to handle redirects and retries
def fetch_url(url, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            else:
                print("Failed to fetch {}, status code: {}".format(url, response.status_code))
        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries - 1:
                print("Error fetching {}. Retrying... (Attempt {}/{})".format(url, attempt + 1, max_retries))
                time.sleep(random.uniform(1, 2)) 
            else:
                print("Failed to fetch {} after {} attempts.".format(url, max_retries))
                return None

# Count the pages in the given category and its subcategories up to the specified depth
def count_pages_in_category_and_subcategories(category_name, depth=1, output_file="titles.jsonl"):
    url = "https://en.wikipedia.org/w/api.php"
    total_pages = 0
    checked_titles = set()  # To keep track of already visited article titles
    visited_categories = set()  # To keep track of already visited categories

    # Open JSONL file to save results
    with open(output_file, "w", encoding="utf-8") as f:

        def save_title_to_file(title):
            """Save title to JSONL file"""
            json.dump({"title": title}, f, ensure_ascii=False)
            f.write("\n")

        def get_pages_in_category(category):
            nonlocal total_pages
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{category}",
                "cmlimit": "max",
                "format": "json"
            }

            response = fetch_url(url, params=params)
            if not response:
                return []

            data = response.json()
            subcategories = []

            for item in data.get("query", {}).get("categorymembers", []):
                if item["ns"] == 0:  # Page
                    if item["title"] not in checked_titles:
                        checked_titles.add(item["title"])
                        total_pages += 1
                        save_title_to_file(item["title"])  # Save title to file
                        if total_pages % 1000 == 0:
                            print(f"Already counted {total_pages} pages, the most recent one is {item['title']}")
                elif item["ns"] == 14:  # Subcategory
                    subcategories.append(item["title"].replace("Category:", ""))

            return subcategories

        def process_category(category, current_depth):
            if current_depth > depth:  # Stop recursion if the max depth is exceeded
                return
            if category in visited_categories:  # Skip already visited categories
                return
            visited_categories.add(category)  # Mark current category as visited
            subcategories = get_pages_in_category(category)
            for subcategory in subcategories:
                process_category(subcategory, current_depth + 1)

        # Start recursion from the main category
        process_category(category_name, 1)

    return total_pages

# Scrape multiple categories with different depths
def scrape_multiple_categories(categories, depths):
    for category_name, depth in zip(categories, depths):
        output_file = f"{category_name.replace(' ', '_')}_titles.jsonl"  # File name based on category
        print(f"\nStarting to scrape category: {category_name} with depth {depth}")
        total_pages = count_pages_in_category_and_subcategories(category_name, depth, output_file)
        print(f"Total pages in '{category_name}' and its subcategories up to depth {depth}: {total_pages}")
        print(f"Titles saved to {output_file}")

# Example usage
categories = ["Sports"]  # Specify multiple categories
scrape_depths = [5]  # Corresponding depths for each category
scrape_multiple_categories(categories, scrape_depths)