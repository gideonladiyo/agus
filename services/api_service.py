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

    def _get(self, path):
        response = requests.get(
            f"{self.baseUrl}{path}", headers=self.headers, timeout=60
        )
        response.raise_for_status()
        return response.json()

    def ppc_week(self, server, id, type):
        return self._get(f"{server}/ppc/{id}/{ppc_type_parse(type)}")

    def warzone_week(self, server, id):
        return self._get(f"{server}/warzone/{id}/16")
    
    def get_memory(self, slug):
        return self._get(f"ap/memories/{slug}")

    def get_memories(self):
        return self._get("ap/memories")

    def get_characters(self):
        return self._get("ap/characters")

    def get_character(self, slug):
        return self._get(f"ap/characters/{slug}")

    def get_character_skills(self, slug):
        return self._get(f"ap/characters/{slug}/skills")

    def get_character_voices(self, slug):
        return self._get(f"ap/characters/{slug}/voices")

    def get_movies(self):
        return self._get("ap/movies")

    def get_movie_chapters(self, group_id):
        return self._get(f"ap/movies/{group_id}")

    def get_movie_chapter(self, group_id, chapter_id):
        return self._get(f"ap/movies/{group_id}/{chapter_id}")

    def get_full_story(self, code):
        return self._get(f"ap/movies/full/{code}")


api_service = ApiService()
