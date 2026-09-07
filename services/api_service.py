import os
from dotenv import load_dotenv
import requests
from config import baseConfig
from utils import ppc_type_parse

load_dotenv()


class ApiService:
    def __init__(self):
        self.baseUrl = baseConfig.huaxuBaseUrl
        self.apiKey = baseConfig.huaxuApiKey
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        }
        if self.apiKey:
            self.headers["x-api-key"] = self.apiKey
            self.headers["Authorization"] = f"Bearer {self.apiKey}"

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
    
    def get_memory(self, slug):
        response = requests.get(
            f"{self.baseUrl}ap/memories/{slug}", headers=self.headers
        )
        return response.json()

    def get_memories(self):
        response = requests.get(
            f"{self.baseUrl}ap/memories", headers=self.headers
        )
        return response.json()


api_service = ApiService()