import os
from dotenv import load_dotenv
import requests
from discord.ext import tasks
from utils import read_channel_ids, send_log_simple
import datetime

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
USERNAME = os.getenv("TWITTER_USERNAME")
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

last_tweet_id = "2004967135349743825"

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()["data"]["id"]

def get_latest_tweet(user_id):
    url = f"https://api.x.com/2/users/{user_id}/tweets"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()["data"][0]


async def send_to_discord(channel_id, bot, tweet, role_id):
    tweet_url = f"https://x.com/{USERNAME}/status/{tweet['id']}"
    channel = bot.get_channel(channel_id)

    if not channel:
        print("[LOGGER] Channel tidak ditemukan.")
        return

    role_mention = f"<@&{role_id}>\n" if role_id else ""

    message = (
        f"{role_mention}"
        f"📢 **New Tweet from [@{USERNAME}]({USERNAME})**\n"
        f"🔗 [Link]({tweet_url})"
    )

    await channel.send(message)

@tasks.loop(minutes=15)
async def twitter_task(bot):
    global last_tweet_id
    channel_ids = await read_channel_ids()
    await send_log_simple(bot, f"[LOGS] executing: twitter_task {datetime.datetime.now()}")

    try:
        user_id = get_user_id(USERNAME)
        tweet = get_latest_tweet(user_id)

        if tweet["id"] != last_tweet_id:
            last_tweet_id = tweet["id"]
            for channel in channel_ids:
                await send_to_discord(channel["id"], bot, tweet, channel["role_id"])
                log_success_msg = {
                    "status": "Success get new tweet",
                    "id_tweet": tweet["id"],
                    "message": tweet["text"],
                    "time": datetime.datetime.now()
                }
                await send_log_simple(
                    bot, f"[LOGS] executing: TwitterLogs {log_success_msg}"
                )
        else:
            log_fail_message = {
                "status": "No newer tweet",
                "time": datetime.datetime.now()
            }
            await send_log_simple(
                    bot, f"[LOGS] executing: TwitterLogs {log_fail_message}"
                )
            print("Tidak ada tweet baru")

    except Exception as e:
        print("Error:", e)
        await send_log_simple(bot, f"[ERROR] executing: TwitterLogs {e}")
