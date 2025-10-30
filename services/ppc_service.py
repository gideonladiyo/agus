from models import PpcBoss, PpcModel
from services.api_service import api_service
from config import baseConfig
from logger import setup_logger
import pandas as pd

logger = setup_logger(__name__)


class PpcService:
    def __init__(self):
        self.ult_url = baseConfig.ultimateScoreUrl
        self.adv_url = baseConfig.advancedScoreUrl
        self.boss_stat_url = baseConfig.bossStatUrl

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
        """Read CSV data from URL with proper error handling."""
        try:
            logger.info(f"Reading CSV data from: {url}")
            data = pd.read_csv(url, timeout=10)
            if data.empty:
                raise ValueError(f"Empty CSV data from {url}")
            return data
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty CSV file: {url}")
            raise ValueError(f"Empty CSV file: {url}") from e
        except Exception as e:
            logger.error(f"Error reading CSV from {url}: {e}")
            raise

    def get_boss_stat(self, name):
        """Get boss statistics by name with validation."""
        try:
            data = self.read_data(self.boss_stat_url)
            boss_data = data[data["slug"] == name.lower()]

            if boss_data.empty:
                logger.warning(f"Boss not found: {name}")
                raise ValueError(f"Boss '{name}' not found in database")

            row = boss_data.iloc[0]
            logger.info(f"Retrieved boss stats for: {name}")
            return {
                "name": row["boss"],
                "knight": row["knight"],
                "chaos": row["chaos"],
                "hell": row["hell"],
                "start_time": row["start_time"],
                "weakness": row["weakness"],
                "img_url": row["img_url"]
            }
        except Exception as e:
            logger.error(f"Error getting boss stats for {name}: {e}")
            raise
    
    def get_boss_list(self):
        data = self.read_data(self.boss_stat_url)
        names = data["boss"].tolist()
        slugs = data["slug"].tolist()
        return {
            "names": names,
            "slugs": slugs
        }

    # ============ PPC TIMER ============
    def get_score(self, time, stage, type):
        """Get score for specific time and stage with validation."""
        try:
            if type.lower() == "advanced":
                data = self.read_data(self.adv_url)
            else:
                data = self.read_data(self.ult_url)

            filtered_data = data.loc[data["kill_time"] == time, stage]

            if filtered_data.empty:
                logger.warning(f"No score found for time={time}, stage={stage}, type={type}")
                raise ValueError(f"No score found for time {time}s in {stage} difficulty")

            score = filtered_data.iloc[0]
            logger.info(f"Score retrieved: {score} for {stage} {time}s ({type})")
            return score
        except Exception as e:
            logger.error(f"Error getting score for {stage} {time}s ({type}): {e}")
            raise

    def get_total_score(self, knight, chaos, hell, type):
        knight_score = self.get_score(knight, "Knight", type)
        chaos_score = self.get_score(chaos, "Chaos", type)
        hell_score = self.get_score(hell, "Hell", type)
        total_score = knight_score + chaos_score + hell_score
        return total_score


ppc_service = PpcService()
