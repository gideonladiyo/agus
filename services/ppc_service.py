from models import PpcBoss, PpcModel
from services.api_service import api_service
import pandas as pd

class PpcService:
    def __init__(self):
        self.ult_url = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=ult"
        self.adv_url = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=adv"
        self.boss_stat_url = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=ppc_boss"

    # ============ PPC WEEK ============
    def get_current_ppc(self, server, type):
        return api_service.ppc_week(server, "current", type)

    def get_current_ppc_bosses(self, server, type):
        data = self.get_current_ppc(server, type)
        return [PpcBoss.parsing_json(boss).to_dict() for boss in data["data"]["ppc"]["bosses"]]

    def get_current_ppc_item(self, server, type):
        data = self.get_current_ppc(server, type)
        ppc_model = PpcModel.parsing_json(data).to_dict()
        return ppc_model

    # ============ PPC BOSS STAT ============
    def read_data(self, url):
        data = pd.read_csv(url)
        return data
    
    def get_boss_stat(self, name):
        data = self.read_data(self.boss_stat_url)
        print(data)
        boss_data = data[data["slug"] == name.lower()]
        row = boss_data.iloc[0]
        return {
            "name": row["boss"],
            "knight": row["knight"],
            "chaos": row["chaos"],
            "hell": row["hell"],
            "start_time": row["start_time"],
            "weakness": row["weakness"],
            "img_url": row["img_url"]
        }

    # ============ PPC TIMER ============
    def get_score(self, time, stage, type):
        if type.lower() == "advanced":
            data = self.read_data(self.adv_url)
        else:
            data = self.read_data(self.ult_url)
        score = data.loc[data["kill_time"] == time, stage].iloc[0]
        return score

    def get_total_score(self, knight, chaos, hell, type):
        knight_score = self.get_score(knight, "Knight", type)
        chaos_score = self.get_score(chaos, "Chaos", type)
        hell_score = self.get_score(hell, "Hell", type)
        total_score = knight_score + chaos_score + hell_score
        return total_score


ppc_service = PpcService()
