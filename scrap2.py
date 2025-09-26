import json

output_file = "korea_warzone_buff_unique.json"
input_file = "korea_warzone_buff.json"
wz_unique = []
seen_ids = set()

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for d in data:
    if d["id"] not in seen_ids:
        seen_ids.add(d["id"])
        wz_unique.append(d)
        print(f"{d} telah ditambahkan")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(wz_unique, f, ensure_ascii=False, indent=2)
