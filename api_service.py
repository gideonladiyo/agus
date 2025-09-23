from config import baseConfig
from models import PpcBoss
import requests

class ApiService:
    def __init__(self):
        self.baseUrl = "https://api.huaxu.app/servers/"

    def ppc_boss(self, server, type):
        response = requests.get(f"{self.baseUrl}{server}/ppc/current/{type}")
        data = response.json()["data"]
        bosses = []
        for boss in data["ppc"]["bosses"]:
            # print(PpcBoss.jsonParsing(boss))
            bosses.append(PpcBoss.jsonParsing(boss).to_dict())
        return bosses

api_service = ApiService()