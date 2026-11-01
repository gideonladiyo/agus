import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode("utf-8"))


def build_ppc_boss_map(output_path: str = "data/ppc_boss_map.json"):
    cur = fetch_json("https://api.huaxu.app/servers/ap/ppc/current/4")["data"]
    act_min = cur["activities"]["min"]
    act_max = cur["activities"]["max"]
    print(f"Scraping AP PPC bosses from activity {act_min} to {act_max}...")

    by_boss_id = {}
    by_monster_id = {}
    by_icon = {}

    def fetch_act(act):
        bosses_found = []
        for level in (4, 3):
            try:
                d = fetch_json(f"https://api.huaxu.app/servers/ap/ppc/{act}/{level}")
                bosses_found.extend(d["data"]["ppc"].get("bosses", []))
            except Exception:
                pass
        return bosses_found

    with ThreadPoolExecutor(max_workers=12) as ex:
        for bosses in ex.map(fetch_act, range(act_min, act_max + 1)):
            for b in bosses:
                bid = b.get("id")
                bname = b.get("name")
                bicon = b.get("icon")
                mid = (b.get("monster") or {}).get("id")
                if bid and bname:
                    by_boss_id[str(bid)] = bname
                if mid and bname:
                    by_monster_id[str(mid)] = bname
                if bicon and bname:
                    by_icon[bicon] = bname

    out = {
        "by_boss_id": dict(sorted(by_boss_id.items(), key=lambda x: int(x[0]))),
        "by_monster_id": dict(sorted(by_monster_id.items(), key=lambda x: int(x[0]))),
        "by_icon": dict(sorted(by_icon.items())),
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(
        f"Saved {len(by_boss_id)} boss IDs, {len(by_monster_id)} monster IDs, {len(by_icon)} icons to {output_path}"
    )


if __name__ == "__main__":
    build_ppc_boss_map()
