from services.warzone_service import warzone_service
import json
import os

output_file = "korea_warzone_weathers.json"

if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = []

for i in range(343, 409):
    # get data
    warzone_data = warzone_service.get_wz_map("korea", i)
    for area in warzone_data["area"]:
        for buff in area["weathers"]:
            all_data.append(buff)
            print(f"buff {buff['name']} telah ditambahkan")

    # tambah data ke json
    # all_data.append(warzone_data)
    # print(f"id {i} selesai")

# json menyimpan semua data
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"✅ Data berhasil disimpan ke {output_file}")
