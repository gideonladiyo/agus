from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from config import baseConfig
from models import WarzoneWeek
from services.api_service import api_service
from utils import server_map

WIB_TZ = timezone(timedelta(hours=7), name="WIB")


class WarzoneService:
    def __init__(self):
        self.api_service = api_service
        self.zones_path = Path(baseConfig.wzPredictZonesPath)
        self.logo_map_path = Path(baseConfig.wzLogoMapPath)
        self.weather_map_path = Path(baseConfig.wzWeatherMapPath)
        self.element_map_path = Path(baseConfig.wzElementMapPath)
        self.zones_by_id = {}
        self.logo_by_buff_id = {}
        self.logo_by_name = {}
        self.weather_map = {}
        self.elem_by_buff_id = {}
        self.elem_by_name = {}
        self.type_by_desc = {}
        self.type_by_prefix = {}
        self._load_zones_db()
        self._load_logo_and_weather_maps()

    def _load_zones_db(self):
        if not self.zones_path.exists():
            print(f"[WARN] Zones dataset not found at {self.zones_path}")
            return

        with open(self.zones_path, "r", encoding="utf-8") as f:
            db = json.load(f)

        self.zones_by_id = db.get("by_id", {})

    def _load_logo_and_weather_maps(self):
        if self.logo_map_path.exists():
            with open(self.logo_map_path, "r", encoding="utf-8") as f:
                logo_data = json.load(f)
            self.logo_by_buff_id = logo_data.get("by_buff_id", {})
            self.logo_by_name = logo_data.get("by_name", {})

        if self.weather_map_path.exists():
            with open(self.weather_map_path, "r", encoding="utf-8") as f:
                self.weather_map = json.load(f)

        if self.element_map_path.exists():
            with open(self.element_map_path, "r", encoding="utf-8") as f:
                elem_data = json.load(f)
            self.elem_by_buff_id = elem_data.get("by_buff_id", {})
            self.elem_by_name = elem_data.get("by_name", {})
            self.type_by_desc = elem_data.get("type_by_description", {})
            self.type_by_prefix = elem_data.get("type_by_prefix", {})

    def get_logo_url(self, buff_id=None, buff_name: str = "") -> str:
        if buff_id is not None and str(buff_id) in self.logo_by_buff_id:
            return self.logo_by_buff_id[str(buff_id)]
        if buff_name and buff_name in self.logo_by_name:
            return self.logo_by_name[buff_name]
        return ""

    def get_element_name(self, buff_id=None, buff_name: str = "") -> str:
        if buff_id is not None and str(buff_id) in self.elem_by_buff_id:
            return self.elem_by_buff_id[str(buff_id)]
        if buff_name and buff_name in self.elem_by_name:
            return self.elem_by_name[buff_name]
        return buff_name or "Unknown"

    def get_zone_type(self, description: str) -> str:
        if not description:
            return "Unknown"
        desc_clean = description.strip()
        if desc_clean in self.type_by_desc:
            return self.type_by_desc[desc_clean]
        # Match by prefix before ':' or '：'
        prefix = desc_clean.replace("：", ":").split(":", 1)[0].strip().lower()
        if prefix in self.type_by_prefix:
            return self.type_by_prefix[prefix]
        return "Unknown"

    def get_current_warzone(self, server, id):
        return self.api_service.warzone_week(server=server_map(server), id=id)

    def get_wz_map(self, server, id="current"):
        data = self.get_current_warzone(server, id)
        return WarzoneWeek.parsing_json(data["data"]["warzone"]).to_json()

    @staticmethod
    def combine_buff_descriptions(buff_descriptions: list[str]) -> str:
        cleaned = [d.strip() for d in buff_descriptions if d and d.strip()]
        if not cleaned:
            return "No buff data"
        if len(cleaned) == 1:
            return cleaned[0]
        parts = [d.rstrip(".") for d in cleaned[:-1]] + [cleaned[-1]]
        return " and ".join(parts)

    @staticmethod
    def _extract_zone_fields(zone_obj: dict) -> tuple[str, str, list[str]]:
        zone_name = zone_obj.get("name", "Unknown Zone")
        zone_desc = zone_obj.get("description", "No description")
        buff_descs = [
            b.get("description", "")
            for b in zone_obj.get("buffs", [])
            if b.get("description")
        ]
        if not buff_descs and zone_obj.get("buffDescription"):
            buff_descs = [zone_obj["buffDescription"]]
        return zone_name, zone_desc, buff_descs

    @staticmethod
    def format_cycle_dates_wib(start_iso: str, end_iso: str) -> tuple[str, str]:
        start_dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00")).astimezone(
            WIB_TZ
        )
        end_dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00")).astimezone(
            WIB_TZ
        )
        monday_date = start_dt.date() - timedelta(days=start_dt.weekday())
        sunday_date = monday_date + timedelta(days=6)
        if end_dt.date() > sunday_date:
            sunday_date = end_dt.date()
        return monday_date.strftime("%d %b %Y"), sunday_date.strftime("%d %b %Y")

    def get_warzone_predict(self, server="jp", id="current") -> dict:
        if not self.zones_by_id:
            self._load_zones_db()

        response = self.api_service.warzone_current(server=server, id=id)
        wz = response["data"]["warzone"]

        monday_str, sunday_str = self.format_cycle_dates_wib(wz["start"], wz["end"])
        translated_zones = []
        untranslated_ids = []

        for z in wz.get("area", {}).get("zones", []):
            zid = z.get("id")
            try:
                mapped_zone = self.zones_by_id[str(zid)]
                zone_name, zone_desc, buff_descs = self._extract_zone_fields(mapped_zone)
            except KeyError:
                untranslated_ids.append(zid)
                zone_name, zone_desc, buff_descs = self._extract_zone_fields(z)

            buff_text = self.combine_buff_descriptions(buff_descs)
            translated_zones.append(
                {
                    "id": zid,
                    "name": zone_name,
                    "description": zone_desc,
                    "buff_text": buff_text,
                }
            )

        return {
            "activity": wz.get("activity"),
            "start": wz.get("start"),
            "end": wz.get("end"),
            "monday_str": monday_str,
            "sunday_str": sunday_str,
            "cycle_text": f"{monday_str} ~ {sunday_str}",
            "zones": translated_zones,
            "untranslated_ids": untranslated_ids,
        }

    def get_cn_warzone_predict(self, id="current") -> dict:
        return self.get_warzone_predict(server="cn", id=id)

    def get_warzone_sheet_data(self, server="jp", id="current") -> dict:
        """
        Ambil data warzone berdasarkan server ('jp' atau 'cn') dan activity id ('current' atau angka),
        terjemahkan zone, buffs (Environment), weathers (Buff), elemen, tipe, dan logo URL.
        """
        if not self.zones_by_id:
            self._load_zones_db()
        if not self.logo_by_buff_id or not self.weather_map or not self.elem_by_buff_id:
            self._load_logo_and_weather_maps()

        response = self.api_service.warzone_current(server=server, id=id)
        wz = response["data"]["warzone"]
        activities_range = response["data"].get("activities", {})

        monday_str, sunday_str = self.format_cycle_dates_wib(wz["start"], wz["end"])
        sheet_zones = []
        untranslated_zone_ids = []
        untranslated_weathers = []

        for raw_zone in wz.get("area", {}).get("zones", []):
            zid = raw_zone.get("id")
            try:
                mapped_zone = self.zones_by_id[str(zid)]
                zone_name = mapped_zone.get("name", "Unknown Zone")
                zone_desc = mapped_zone.get("description", "No description")
                raw_buffs = mapped_zone.get("buffs", [])
            except KeyError:
                untranslated_zone_ids.append(zid)
                zone_name = raw_zone.get("name", "Unknown Zone")
                zone_desc = raw_zone.get("description", "No description")
                raw_buffs = raw_zone.get("buffs", [])

            parts_env = []
            elem_names = []
            for b in raw_buffs:
                bid = b.get("id")
                bname = b.get("name", zone_name)
                if bname == "Loop of Fire":
                    bname = "Cycle of Fire"
                bdesc = b.get("description", "")
                logo_url = self.get_logo_url(buff_id=bid, buff_name=bname)
                elem = self.get_element_name(buff_id=bid, buff_name=bname)
                elem_names.append(elem)
                parts_env.append(
                    {
                        "id": bid,
                        "name": bname,
                        "description": bdesc,
                        "logo_url": logo_url,
                        "element": elem,
                    }
                )

            element_label = "/".join(elem_names) if elem_names else "Unknown"
            zone_type = self.get_zone_type(zone_desc)

            parts_weather = []
            for w in raw_zone.get("weathers", []):
                w_raw_name = w.get("name", "")
                try:
                    mapped_w = self.weather_map[w_raw_name]
                    w_name = mapped_w["name"]
                    w_desc = mapped_w["description"]
                except KeyError:
                    untranslated_weathers.append(w_raw_name)
                    w_name = w_raw_name
                    w_desc = w.get("description", "")
                parts_weather.append({"name": w_name, "description": w_desc})

            sheet_zones.append(
                {
                    "id": zid,
                    "name": zone_name,
                    "description": zone_desc,
                    "element_label": element_label,
                    "zone_type": zone_type,
                    "summary_line": f"{element_label} ({zone_type})",
                    "environments": parts_env,
                    "weathers": parts_weather,
                }
            )

        return {
            "activity": wz.get("activity"),
            "activities_range": activities_range,
            "start": wz.get("start"),
            "end": wz.get("end"),
            "monday_str": monday_str,
            "sunday_str": sunday_str,
            "cycle_text": f"{monday_str} ~ {sunday_str}",
            "zones": sheet_zones,
            "untranslated_zone_ids": untranslated_zone_ids,
            "untranslated_weathers": untranslated_weathers,
        }

    def get_cn_warzone_sheet_data(self, id="current") -> dict:
        return self.get_warzone_sheet_data(server="cn", id=id)


warzone_service = WarzoneService()
