from models import PpcBoss
from utils import ppc_type_parse
import requests

class ApiService:
    def __init__(self):
        self.baseUrl = "https://api.huaxu.app/servers/"

    def ppc_week(self, server, id, type):
        response = requests.get(f"{self.baseUrl}{server}/ppc/{id}/{ppc_type_parse(type)}")
        return response.json()
    
    def warzone_week(self, server, id):
        response = requests.get(f"{self.baseUrl}{server}/warzone/{id}/16")
        return response.json()

api_service = ApiService()
