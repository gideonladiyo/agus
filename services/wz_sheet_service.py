import asyncio
import io
from pathlib import Path
import time
import gspread
from PIL import Image, ImageDraw
import requests
from config import baseConfig
from services.ppc_service import ppc_service
from services.team_service import team_service
from services.warzone_service import warzone_service
from utils import merge_images_horizontal


class WzSheetWriteError(RuntimeError):
    pass


class WzSheetService:
    LOGO_ROW_BOXES = [
        (179, 278),  # C5:C8 (Zone 1)
        (282, 381),  # C9:C12 (Zone 2)
        (384, 483),  # C13:C16 (Zone 3 Bagian 1)
        (487, 586),  # C17:C20 (Zone 3 Bagian 2)
    ]
    LOGO_X_RANGE = (171, 268)

    def __init__(self):
        self._lock = asyncio.Lock()
        self._logo_cache: dict[str, Image.Image] = {}

    def _get_logo_image(self, url: str) -> Image.Image | None:
        if not url:
            return None
        if url in self._logo_cache:
            return self._logo_cache[url].copy()

        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            if resp.status_code == 200:
                icon = Image.open(io.BytesIO(resp.content)).convert("RGBA")
                self._logo_cache[url] = icon
                return icon.copy()
        except Exception as e:
            print(f"[WARN] Gagal mengunduh logo {url}: {e}", flush=True)
        return None

    @classmethod
    def build_cell_updates(cls, sheet_data: dict) -> dict[str, str]:
        """
        Susun mapping cell -> value berdasarkan urutan zone (0, 1, 2):
        - Zone 1: C5:C8 (logo), D5:G6 (name), D7:G8 (buffdesc), H5:K6 (weather name), H7:K8 (weather desc), L5:N8 (desc)
        - Zone 2: C9:C12 (logo), D9:G10 (name), D11:G12 (buffdesc), H9:K10 (weather name), H11:K12 (weather desc), L9:N12 (desc)
        - Zone 3 Bagian 1: C13:C16, D13:G14, D15:G16, H13:K14, H15:K16
        - Zone 3 Bagian 2: C17:C20, D17:G18, D19:G20, H17:K18, H19:K20
        - Zone 3 Description: L13:N20
        """
        zones = sheet_data.get("zones", [])
        updates = {}

        def _get_item(lst, idx):
            return lst[idx] if idx < len(lst) else {}

        # --- ZONE 1 (index 0) ---
        z1 = _get_item(zones, 0)
        z1_env = _get_item(z1.get("environments", []), 0)
        z1_w = _get_item(z1.get("weathers", []), 0)
        updates["C5"] = ""
        updates["D5"] = z1_env.get("name", "")
        updates["D7"] = z1_env.get("description", "")
        updates["H5"] = z1_w.get("name", "")
        updates["H7"] = z1_w.get("description", "")
        updates["L5"] = z1.get("description", "")

        # --- ZONE 2 (index 1) ---
        z2 = _get_item(zones, 1)
        z2_env = _get_item(z2.get("environments", []), 0)
        z2_w = _get_item(z2.get("weathers", []), 0)
        updates["C9"] = ""
        updates["D9"] = z2_env.get("name", "")
        updates["D11"] = z2_env.get("description", "")
        updates["H9"] = z2_w.get("name", "")
        updates["H11"] = z2_w.get("description", "")
        updates["L9"] = z2.get("description", "")

        # --- ZONE 3 (index 2) ---
        z3 = _get_item(zones, 2)
        z3_envs = z3.get("environments", [])
        z3_weathers = z3.get("weathers", [])

        # Bagian 1
        z3_env1 = _get_item(z3_envs, 0)
        z3_w1 = _get_item(z3_weathers, 0)
        updates["C13"] = ""
        updates["D13"] = z3_env1.get("name", "")
        updates["D15"] = z3_env1.get("description", "")
        updates["H13"] = z3_w1.get("name", "")
        updates["H15"] = z3_w1.get("description", "")

        # Bagian 2
        z3_env2 = _get_item(z3_envs, 1)
        z3_w2 = _get_item(z3_weathers, 1)
        updates["C17"] = ""
        updates["D17"] = z3_env2.get("name", "")
        updates["D19"] = z3_env2.get("description", "")
        updates["H17"] = z3_w2.get("name", "")
        updates["H19"] = z3_w2.get("description", "")

        # Description untuk Zone 3 (L13:N20)
        updates["L13"] = z3.get("description", "")

        return updates

    def _detect_logo_row_boxes(self, base_img: Image.Image) -> list[tuple[int, int]]:
        gray = base_img.convert("L")
        raw_ys = [
            y
            for y in range(gray.height - 5)
            if sum(gray.getpixel((x, y)) for x in range(180, 260)) / 80 > 100
        ]
        clustered: list[int] = []
        for y in raw_ys:
            if not clustered or y - clustered[-1] > 8:
                clustered.append(y)
        if len(clustered) >= 6:
            return [
                (clustered[i] + 2, clustered[i + 1] - 2) for i in range(1, 5)
            ]
        return self.LOGO_ROW_BOXES

    def _composite_logos(self, image_bytes: bytes, sheet_data: dict) -> bytes:
        base_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        draw = ImageDraw.Draw(base_img)

        zones = sheet_data.get("zones", [])
        logo_urls = [
            zones[0]["environments"][0].get("logo_url", "")
            if len(zones) > 0 and zones[0].get("environments")
            else "",
            zones[1]["environments"][0].get("logo_url", "")
            if len(zones) > 1 and zones[1].get("environments")
            else "",
            zones[2]["environments"][0].get("logo_url", "")
            if len(zones) > 2 and len(zones[2].get("environments", [])) > 0
            else "",
            zones[2]["environments"][1].get("logo_url", "")
            if len(zones) > 2 and len(zones[2].get("environments", [])) > 1
            else "",
        ]

        row_boxes = self._detect_logo_row_boxes(base_img)
        x1, x2 = self.LOGO_X_RANGE
        for (y1, y2), url in zip(row_boxes, logo_urls):
            # Bersihkan area cell logo dari teks error (#ERROR! / #REF!) jika ada
            draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0, 255))
            icon = self._get_logo_image(url)
            if icon is not None:
                box_size = min(86, max(40, (y2 - y1) - 10))
                icon.thumbnail((box_size, box_size), Image.Resampling.LANCZOS)
                ix = x1 + (x2 - x1 - icon.width) // 2
                iy = y1 + (y2 - y1 - icon.height) // 2
                base_img.paste(icon, (ix, iy), icon)

        # Pangkas garis putih tipis di tepi bawah/kanan PDF jika ada
        if base_img.width > 10 and base_img.height > 10:
            base_img = base_img.crop((0, 0, base_img.width - 2, base_img.height - 2))

        out = io.BytesIO()
        base_img.convert("RGB").save(out, format="PNG", optimize=True)
        return out.getvalue()

    def write_updates_to_sheet(self, updates: dict[str, str]):
        """
        Update cell di Google Sheet menggunakan:
        1. Google Apps Script Web App (WZ_APPS_SCRIPT_URL) jika diset di .env, atau
        2. Google Service Account JSON (GOOGLE_SERVICE_ACCOUNT_FILE) via gspread.
        """
        apps_script_url = (baseConfig.wzAppsScriptUrl or "").strip()
        sa_file = Path(baseConfig.googleServiceAccountFile)

        if apps_script_url:
            resp = requests.post(
                apps_script_url,
                json={
                    "spreadsheet_id": baseConfig.wzSheetId,
                    "gid": int(baseConfig.wzSheetGid),
                    "updates": updates,
                },
                timeout=30,
            )
            resp.raise_for_status()
            res_json = resp.json()
            if res_json.get("status") != "ok":
                raise WzSheetWriteError(
                    f"Apps Script gagal mengupdate sheet: {res_json.get('message', resp.text)}"
                )
            return

        if sa_file.exists():
            gc = gspread.service_account(filename=str(sa_file))
            sh = gc.open_by_key(baseConfig.wzSheetId)
            worksheet = sh.get_worksheet_by_id(int(baseConfig.wzSheetGid))
            if worksheet is None:
                raise WzSheetWriteError(
                    f"Worksheet dengan gid={baseConfig.wzSheetGid} tidak ditemukan."
                )
            batch_data = [
                {"range": cell, "values": [[val]]} for cell, val in updates.items()
            ]
            worksheet.batch_update(batch_data, value_input_option="USER_ENTERED")
            return

        raise WzSheetWriteError(
            "Kredensial tulis Google Sheet belum dikonfigurasi. "
            f"Pasang file Service Account di `{baseConfig.googleServiceAccountFile}` "
            "atau isi `WZ_APPS_SCRIPT_URL` di `.env`."
        )

    def _update_and_render_sync(self, activity_id="current") -> tuple[dict, bytes]:
        sheet_data = warzone_service.get_cn_warzone_sheet_data(id=activity_id)
        updates = self.build_cell_updates(sheet_data)
        self.write_updates_to_sheet(updates)

        if baseConfig.wzRenderDelaySec > 0:
            time.sleep(min(baseConfig.wzRenderDelaySec, 1.0))

        raw_image_bytes = team_service.render_sheet_area(
            baseConfig.wzRenderArea,
            spreadsheet_id=baseConfig.wzSheetId,
            gid=baseConfig.wzSheetGid,
            padding=0,
        )
        final_image_bytes = self._composite_logos(raw_image_bytes, sheet_data)
        return sheet_data, final_image_bytes

    async def update_and_render(self, activity_id="current") -> tuple[dict, bytes]:
        async with self._lock:
            return await asyncio.to_thread(self._update_and_render_sync, activity_id)

    @staticmethod
    def build_prediction_text(sheet_data: dict, ppc_bosses: list[dict]) -> str:
        cycle_text = sheet_data.get("cycle_text", "")
        zones = sheet_data.get("zones", [])
        wz_lines = "\n".join(f"- {z.get('summary_line', '')}" for z in zones)
        ppc_lines = "\n".join(f"- {b.get('name', '')}" for b in ppc_bosses)
        return (
            f"# Warzone & PPC Prediction Cycle {cycle_text}\n"
            f"Warzone:\n"
            f"{wz_lines}\n\n"
            f"PPC:\n"
            f"{ppc_lines}"
        )

    async def generate_wz_ppc_prediction(
        self, activity_id="current"
    ) -> tuple[str, bytes, io.BytesIO | None, dict, list[dict]]:
        sheet_data, wz_image_bytes = await self.update_and_render(
            activity_id=activity_id
        )
        ppc_bosses = await asyncio.to_thread(
            ppc_service.get_cn_ppc_predict_bosses, "ultimate"
        )
        ppc_img = await merge_images_horizontal(b["imgUrl"] for b in ppc_bosses)
        text_msg = self.build_prediction_text(sheet_data, ppc_bosses)
        return text_msg, wz_image_bytes, ppc_img, sheet_data, ppc_bosses


wz_sheet_service = WzSheetService()
