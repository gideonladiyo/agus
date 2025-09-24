from models import PpcBoss, PpcModel
from services.api_service import api_service

class PpcService:
    def __init__(self):
        self.api_service = api_service

    def get_current_ppc(self, server, type):
        return self.api_service.ppc_week(server, "current", type)

    def get_current_ppc_bosses(self, server, type):
        data = self.get_current_ppc(server, type)
        return [PpcBoss.parsing_json(boss).to_dict() for boss in data["data"]["ppc"]["bosses"]]

    def get_current_ppc_item(self, server, type):
        data = self.get_current_ppc(server, type)
        ppc_model = PpcModel.parsing_json(data).to_dict()
        return ppc_model

ppc_service = PpcService()