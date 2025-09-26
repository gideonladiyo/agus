import pandas as pd

class PpcTimer:
    def __init__(self):
        self.ult_filepath = "timer_ult.csv"
        self.adv_filepath = "timer_adv.csv"

    def read_data(self):
        data = pd.read_csv(self.ult_filepath, sep=";", thousands=".")
        data.rename(columns={"Kill Time (value)": "kill_time"}, inplace=True)
        return data
    
    def read_adv(self):
        data = pd.read_csv(self.adv_filepath, sep=",")
        return data

    def get_score(self, time, stage, type):
        if type.lower() == "advanced":
            data = self.read_adv()
        else:
            data = self.read_data()
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
