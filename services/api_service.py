from utils import ppc_type_parse
import requests
from config import baseConfig
from logger import setup_logger

logger = setup_logger(__name__)


class ApiService:
    def __init__(self):
        self.baseUrl = baseConfig.baseApiUrl
        self.headers = {"User-Agent": baseConfig.userAgent}

    def ppc_week(self, server, id, type):
        """Fetch PPC week data from API with proper error handling."""
        try:
            url = f"{self.baseUrl}{server}/ppc/{id}/{ppc_type_parse(type)}"
            logger.info(f"Fetching PPC week data: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching PPC week data: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching PPC week data: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise

    def warzone_week(self, server, id):
        """Fetch warzone week data from API with proper error handling."""
        try:
            url = f"{self.baseUrl}{server}/warzone/{id}/16"
            logger.info(f"Fetching warzone week data: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching warzone week data: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching warzone week data: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise


api_service = ApiService()
