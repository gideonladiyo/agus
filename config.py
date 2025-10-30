class BaseConfig:
    """Central configuration for the bot."""

    def __init__(self):
        # Base URLs
        self.baseImgUrl = "https://assets.huaxu.app/glb/"
        self.baseApiUrl = "https://api.huaxu.app/servers/"

        # Discord Configuration
        self.allowedServerIds = [1273463276847632405, 1010450041514754109]
        self.adminUserId = 533104933168480286

        # Google Sheets URLs for PPC data
        self.ultimateScoreUrl = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=ult"
        self.advancedScoreUrl = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=adv"
        self.bossStatUrl = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=ppc_boss"

        # User Agent for API requests
        self.userAgent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

baseConfig = BaseConfig()