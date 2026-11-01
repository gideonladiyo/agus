"""
Script untuk melakukan scraping data Warzone Zones dari Huaxu API (https://api.huaxu.app)
dan melakukan agregasi data unik berdasarkan Zone ID.

Penggunaan:
    python scrape_zones.py --server ap --start 1 --end 465 --workers 10
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Setup encoding output konsol agar aman di Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def fetch_warzone_activity(server: str, activity: int, timeout: int = 10):
    """
    Fetch data warzone untuk activity tertentu.
    Returns (activity, zones_list_or_None, status_code_or_message).
    """
    url = f"https://api.huaxu.app/servers/{server}/warzone/{activity}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            if res.status == 200:
                body = res.read().decode("utf-8")
                payload = json.loads(body)
                zones = (
                    payload.get("data", {})
                    .get("warzone", {})
                    .get("area", {})
                    .get("zones", [])
                )
                return activity, zones, 200
    except urllib.error.HTTPError as e:
        return activity, None, e.code
    except Exception as e:
        return activity, None, str(e)

    return activity, None, "unknown"


def get_server_activity_range(server: str):
    """Cek min dan max activity yang tersedia pada server tertentu."""
    url = f"https://api.huaxu.app/servers/{server}/warzone/current"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            payload = json.loads(res.read().decode("utf-8"))
            activities = payload.get("data", {}).get("activities", {})
            return activities.get("min"), activities.get("max")
    except Exception:
        return None, None


def scrape_and_aggregate_zones(
    server: str = "ap",
    start_act: int = 1,
    end_act: int = 465,
    max_workers: int = 10,
    output_path: str = "data/pgr_warzone_zones.json",
):
    print("=" * 65)
    print(f" Memulai Scraping Warzone Zones dari Huaxu API")
    print(f" Server        : {server.upper()}")
    print(f" Rentang Target: Activity {start_act} s.d. {end_act}")
    print(f" Concurrency   : {max_workers} threads")
    print("=" * 65)

    # Cek metadata server untuk info rentang activity resmi
    db_min, db_max = get_server_activity_range(server)
    if db_min is not None and db_max is not None:
        print(f"[*] Info Server: Data {server.upper()} tersedia dari Activity {db_min} s.d. {db_max}")
        if start_act < db_min:
            print(f"    (Catatan: Activity {start_act} - {db_min - 1} akan mengembalikan 404 karena data belum mulai dicatat)")

    unique_zones = {}
    completed_count = 0
    not_found_count = 0
    total_acts = end_act - start_act + 1
    start_time = time.time()

    print(f"[*] Mengirim permintaan ke server...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_act = {
            executor.submit(fetch_warzone_activity, server, act): act
            for act in range(start_act, end_act + 1)
        }

        for future in as_completed(future_to_act):
            completed_count += 1
            act, zones, status = future.result()

            if completed_count % 25 == 0 or completed_count == total_acts:
                progress = (completed_count / total_acts) * 100
                print(
                    f"\r    Progress: {completed_count}/{total_acts} ({progress:.1f}%) | "
                    f"Unique Zones ditemukan: {len(unique_zones)}",
                    end="",
                    flush=True,
                )

            if zones is None:
                not_found_count += 1
                continue

            for z in zones:
                zid = z.get("id")
                if zid is None:
                    continue

                if zid not in unique_zones:
                    unique_zones[zid] = {
                        "id": zid,
                        "name": z.get("name"),
                        "description": z.get("description"),
                        "buffDescription": z.get("buffDescription"),
                        "element": z.get("element"),
                        "icon": z.get("icon"),
                        "buffs": z.get("buffs", []),
                        "total_appearances": 0,
                        "appearances": [],
                        "weathers": {},  # Disimpan by weather name agar cuaca juga unik
                    }

                # Update statistik kemunculan
                unique_zones[zid]["total_appearances"] += 1
                unique_zones[zid]["appearances"].append(act)

                # Agregasi cuaca (weathers) unik
                for w in z.get("weathers", []):
                    w_name = w.get("name")
                    if w_name and w_name not in unique_zones[zid]["weathers"]:
                        unique_zones[zid]["weathers"][w_name] = w

    print("\n" + "=" * 65)
    print(f"[*] Scraping Selesai dalam {time.time() - start_time:.2f} detik.")
    print(f"    Total Activity Berhasil di-scrape : {total_acts - not_found_count}")
    print(f"    Total Activity Kosong / 404       : {not_found_count}")
    print(f"    Total Unique Zones Ditemukan      : {len(unique_zones)}")

    # Format data untuk mempermudah pencarian dan pencocokan:
    # 1. 'by_id': Map key-value untuk lookup instan O(1) via ID
    # 2. 'by_name': Indeks Map nama zona -> list of Zone IDs
    # 3. 'by_element': Indeks Map element -> list of Zone IDs
    # 4. 'list': Array daftar semua zona terurut berdasarkan ID
    by_id = {}
    by_name = {}
    by_element = {}
    zones_list = []

    for zid in sorted(unique_zones.keys()):
        z_data = unique_zones[zid]
        # Ubah weathers dict menjadi list objek yang rapi
        z_data["weathers"] = list(z_data["weathers"].values())
        # Sort appearances terurut naik
        z_data["appearances"].sort()
        z_data["latest_activity"] = (
            z_data["appearances"][-1] if z_data["appearances"] else None
        )

        by_id[str(zid)] = z_data
        zones_list.append(z_data)

        # Index by Name
        name_key = z_data.get("name") or "Unknown"
        if name_key not in by_name:
            by_name[name_key] = []
        by_name[name_key].append(zid)

        # Index by Element
        elem_key = z_data.get("element") or "none"
        if elem_key not in by_element:
            by_element[elem_key] = []
        by_element[elem_key].append(zid)

    result_dataset = {
        "metadata": {
            "server": server,
            "target_range": [start_act, end_act],
            "valid_activities_found": total_acts - not_found_count,
            "total_unique_zones": len(unique_zones),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "usage_notes": {
                "by_id": "Gunakan untuk pencocokan instan O(1) berdasarkan zone_id (misal: data.by_id[str(zone_id)])",
                "by_name": "Gunakan untuk mencari zone_id berdasarkan nama zona (misal: data.by_name['Laser Alloy'])",
                "by_element": "Gunakan untuk filter zone_id berdasarkan element (misal: data.by_element['physical'])",
                "list": "Gunakan untuk iterasi langsung, filter array, atau binding ke tabel/dropdown UI",
            },
        },
        "by_id": by_id,
        "by_name": by_name,
        "by_element": by_element,
        "list": zones_list,
    }

    # Simpan ke file output
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result_dataset, f, ensure_ascii=False, indent=2)

    print(f"[*] Hasil berhasil disimpan ke: {out_file.resolve()}")
    print("=" * 65)

    return result_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scraper Warzone Zones dari Huaxu API dengan Agregasi Unik."
    )
    parser.add_argument(
        "--server",
        type=str,
        default="ap",
        help="Kode server Huaxu (default: ap. Pilihan lain: cn, eu, us, jp, kr)",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Nomor activity awal (default: 1)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=465,
        help="Nomor activity akhir (default: 465)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Jumlah thread concurrent scraping (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/pgr_warzone_zones.json",
        help="Path file output JSON (default: data/pgr_warzone_zones.json)",
    )

    args = parser.parse_args()
    scrape_and_aggregate_zones(
        server=args.server,
        start_act=args.start,
        end_act=args.end,
        max_workers=args.workers,
        output_path=args.output,
    )
