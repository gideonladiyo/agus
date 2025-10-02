import pandas as pd

class PpcTimer:
    def __init__(self):
        self.ult_url = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=ult"
        self.adv_url = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=adv"
        self.boss_stat_url = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=ppc_boss"

    def read_data(self, url):
        data = pd.read_csv(url)
        return data

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

ppc_timer = PpcTimer()
# total_score = ppc_timer.get_total_score(8, 8, 10)
