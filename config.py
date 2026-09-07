import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    def __init__(self):
        self.baseImgUrl = "https://assets.huaxu.app/glb/"
        self.huaxuApiKey = os.getenv("HUAXU_API_KEY") 
        self.huaxuBaseUrl = os.getenv("HUAXU_BASE_URL")

baseConfig = BaseConfig()