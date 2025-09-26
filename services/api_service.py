from utils import ppc_type_parse
import requests


class ApiService:
    def __init__(self):
        self.baseUrl = "https://api.huaxu.app/servers/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        }

    def ppc_week(self, server, id, type):
        response = requests.get(
            f"{self.baseUrl}{server}/ppc/{id}/{ppc_type_parse(type)}",
            headers=self.headers,
        )
        return response.json()

    def warzone_week(self, server, id):
        response = requests.get(
            f"{self.baseUrl}{server}/warzone/{id}/16", headers=self.headers
        )
        return response.json()


api_service = ApiService()
