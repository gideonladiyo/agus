import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    def __init__(self):
        self.baseImgUrl = "https://assets.huaxu.app/glb/"
        self.huaxuApiKey = os.getenv("HUAXU_API_KEY")
        self.huaxuBaseUrl = os.getenv("HUAXU_BASE_URL")
        self.environment = os.getenv("APP_ENV", "local").lower()
        defaultPrefix = "/" if self.environment == "local" else "!"
        self.commandPrefix = os.getenv("COMMAND_PREFIX", defaultPrefix)
        self.adminIds = [533104933168480286]
        self.teamSpreadsheetId = os.getenv(
            "TEAM_SPREADSHEET_ID",
            "1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA",
        )
        self.teamImageSpreadsheetId = os.getenv(
            "TEAM_IMAGE_SPREADSHEET_ID",
            "1peDlYCz_dPPtuGQJ6PpfB3wh8QLpWeDg8Vm7-zU6_gA",
        )
        self.teamSheetGid = os.getenv("TEAM_SHEET_GID", "0")
        raw_wz_channels = os.getenv(
            "WZ_PREDICT_CHANNEL_ID",
            os.getenv("WZ_PREDICT_CHANNEL_IDS", "1238807704877793372"),
        )
        self.wzPredictTargets = []
        for entry in raw_wz_channels.replace(";", ",").split(","):
            entry = entry.strip()
            if not entry:
                continue
            if ":" in entry:
                ch_part, role_part = entry.split(":", 1)
                ch_clean = ch_part.strip().removeprefix("<#").removesuffix(">").strip()
                role_clean = (
                    role_part.strip().removeprefix("<@&").removesuffix(">").strip()
                )
                if ch_clean.isdigit():
                    role_id = int(role_clean) if role_clean.isdigit() else None
                    self.wzPredictTargets.append(
                        {"channel_id": int(ch_clean), "role_id": role_id}
                    )
            else:
                ch_clean = entry.removeprefix("<#").removesuffix(">").strip()
                if ch_clean.isdigit():
                    self.wzPredictTargets.append(
                        {"channel_id": int(ch_clean), "role_id": None}
                    )
        self.wzPredictChannelIds = [t["channel_id"] for t in self.wzPredictTargets]
        self.wzPredictChannelId = (
            self.wzPredictChannelIds[0]
            if self.wzPredictChannelIds
            else 1238807704877793372
        )
        self.wzPredictTimeWib = os.getenv("WZ_PREDICT_TIME_WIB", "04:00")
        self.wzPredictServer = os.getenv("WZ_PREDICT_SERVER", "jp").lower()
        self.ppcPredictServer = os.getenv("PPC_PREDICT_SERVER", "jp").lower()
        self.wzPredictZonesPath = os.getenv(
            "WZ_PREDICT_ZONES_PATH", "data/pgr_warzone_zones.json"
        )
        self.wzSheetId = os.getenv(
            "WZ_SHEET_ID",
            "1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA",
        )
        self.wzSheetGid = os.getenv("WZ_SHEET_GID", "501567643")
        self.wzRenderArea = os.getenv("WZ_RENDER_AREA", "A1:O22")
        self.wzLogoMapPath = os.getenv("WZ_LOGO_MAP_PATH", "data/wz_logo_map.json")
        self.wzWeatherMapPath = os.getenv(
            "WZ_WEATHER_MAP_PATH", "data/wz_weather_map.json"
        )
        self.wzElementMapPath = os.getenv(
            "WZ_ELEMENT_MAP_PATH", "data/wz_element_map.json"
        )
        self.ppcBossMapPath = os.getenv(
            "PPC_BOSS_MAP_PATH", "data/ppc_boss_map.json"
        )
        self.googleServiceAccountFile = os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/gsheet-sa.json"
        )
        self.wzAppsScriptUrl = os.getenv("WZ_APPS_SCRIPT_URL", "")
        self.wzRenderDelaySec = float(os.getenv("WZ_RENDER_DELAY_SEC", "2.5"))

baseConfig = BaseConfig()
