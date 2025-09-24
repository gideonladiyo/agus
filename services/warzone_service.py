from services.api_service import api_service
from models import WarzoneWeek
from utils import server_map

class WarzoneService:
    def __init__(self):
        self.api_service = api_service
    
    def get_current_warzone(self, server, id):
        return self.api_service.warzone_week(server=server_map(server), id=id)
    
    def get_current_wz(self, server):
        data = self.get_current_warzone(server, "current")
        return WarzoneWeek.parsing_json(data["data"]["warzone"]).to_json()
    
warzone_service = WarzoneService()