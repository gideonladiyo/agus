import pandas as pd

filepath = "timer_ult.csv"

class PpcTimer:
    def __init__(self):
        self.filepath = filepath

    def read_data(self):
        data = pd.read_csv(self.filepath, sep=";", thousands=".")
        data.rename(columns={"Kill Time (value)": "kill_time"}, inplace=True)
        return data
    
    def get_score(self, time, stage):
        data = self.read_data()
        score = data.loc[data["kill_time"] == time, stage].iloc[0]
        return score
    
    def get_total_score(self, knight, chaos, hell):
        knight_score = self.get_score(knight, "Knight")
        chaos_score = self.get_score(chaos, "Chaos")
        hell_score = self.get_score(hell, "Hell")
        total_score = knight_score + chaos_score + hell_score
        return total_score

ppc_timer = PpcTimer()
# total_score = ppc_timer.get_total_score(8, 8, 10)