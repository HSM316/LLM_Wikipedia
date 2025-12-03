import requests
import json

OUTPUT = "fr_featured_articles.jsonl"

URL = "https://fr.wikipedia.org/w/api.php"
headers = {
    "User-Agent": "MyWikipediaScraper/1.0 (hsm@example.com)"
}

params = {
    "action": "query",
    "list": "categorymembers",
    "cmtitle": "Catégorie:Article_de_qualité",
    "cmlimit": "max",
    "format": "json"
}

titles = []
count = 0

with open(OUTPUT, "w", encoding="utf-8") as fout:
    while True:
        r = requests.get(URL, params=params, headers=headers, timeout=10)

        # 检查返回是否为 JSON
        try:
            data = r.json()
        except Exception:
            print("Non-JSON response:")
            print(r.text[:500])
            raise

        for item in data["query"]["categorymembers"]:
            title = item["title"]
            fout.write(json.dumps({"title": title}, ensure_ascii=False) + "\n")
            count += 1

        if "continue" in data:
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break

print(f"Done! Extracted {count} titles.")
print(f"Saved to: {OUTPUT}")
