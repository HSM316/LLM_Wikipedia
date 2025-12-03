import json

input_file = "/Users/hsm/Documents/Wikipedia_Pages/Featured_First_Revised.jsonl"
output_file = "/Users/hsm/Documents/Wikipedia_Pages/Revised_3.5_only.jsonl"

results = []

with open(input_file, "r", encoding="utf-8") as infile:
    for line in infile:
        entry = json.loads(line.strip())
        for version in entry.get("versions", []):
            if version["date"] == "revised_3.5":
                results.append({
                    "title": entry["title"],
                    "content": version["content"]
                })

# 保存提取结果
with open(output_file, "w", encoding="utf-8") as outfile:
    for item in results:
        outfile.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"✅ 提取完成！共找到 {len(results)} 条 revised_3.5，结果已保存到 {output_file}")
