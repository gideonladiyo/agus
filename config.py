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

baseConfig = BaseConfig()
