from PIL import Image
from io import BytesIO
import aiohttp
import asyncio
from discord import Embed
import discord
import json
from config import baseConfig


def ppc_type_parse(type: str):
    type_map = {"ultimate": 4, "advanced": 3}
    return type_map.get(type.lower(), None)


def server_map(server):
    servers = {"asia": "ap", "korea": "kr", "china": "cn", "japan": "jp"}
    return servers.get(server.lower(), None)


async def fetch_image(session, url):
    async with session.get(url) as resp:
        if resp.status == 200:
            return Image.open(BytesIO(await resp.read())).convert("RGBA")
        return None


async def merge_images_horizontal(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, url) for url in urls]
        images = await asyncio.gather(*tasks)

    images = [img for img in images if img]

    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    merged = Image.new("RGBA", (total_width, max_height))
    x_offset = 0
    for img in images:
        merged.paste(img, (x_offset, 0))
        x_offset += img.width

    bio = BytesIO()
    merged.save(bio, format="PNG")
    bio.seek(0)
    return bio


def wz_embed(title, json):
    embed = Embed(title=title, color=discord.Color.red())
    for wz_item in json["area"]:
        buffs_text = ""
        for buff in wz_item.get("buffs", []):
            buffs_text += f"- {buff['name']}\n" f"  {buff['description']}\n"
        weathers_text = ""
        for w in wz_item.get("weathers", []):
            weathers_text += f"- {w['name']}\n" f"  {w['description']}\n"
        text_content = f"{wz_item['description']}\n" f"{buffs_text}" f"{weathers_text}"
        embed.add_field(
            name=wz_item["name"],
            value=text_content if text_content.strip() else "No data",
            inline=True,
        )
    return embed


def ppc_boss_stat_embed(data: dict) -> Embed:
    difficulties = {"knight": "🛡️ Knight", "chaos": "💀 Chaos", "hell": "🔥 Hell"}
    embed = Embed(title=f"⚔️ Boss **{data['name']}**", color=discord.Color.red())
    embed.add_field(name="🔥 Weakness", value=data["weakness"], inline=False)
    embed.add_field(name="⏳ Start Time", value=f"{data['start_time']}s", inline=False)
    for key, label in difficulties.items():
        embed.add_field(name=f"{label}", value=f"{data[key]}", inline=True)
    embed.set_image(url=data["img_url"])
    embed.set_footer(text="PPC Boss Stats")
    return embed


def memory_embed(data: dict) -> Embed:
    name = data.get("name", "Unknown Memory")
    quality = data.get("quality")
    title_prefix = f"{quality}★ Memory" if quality else "Memory"

    embed = Embed(
        title=f"{title_prefix} **{name}**",
        color=discord.Color.blue()
    )

    if data.get("description"):
        embed.description = f"*{data['description']}*"

    icon = data.get("icon", {})
    if isinstance(icon, dict):
        if icon.get("big"):
            embed.set_thumbnail(url=f"{baseConfig.baseImgUrl}{icon['big']}.webp")
        elif icon.get("normal"):
            embed.set_thumbnail(url=f"{baseConfig.baseImgUrl}{icon['normal']}.webp")

    skills = data.get("skills", [])
    if skills:
        for skill in skills:
            level = skill.get("level")
            desc = skill.get("description", "No description")
            field_name = f"{level}-Piece Set Effect" if level else "Skill Effect"
            embed.add_field(name=field_name, value=desc, inline=False)
    else:
        embed.add_field(name="Skills", value="No skill data available", inline=False)
    return embed



# ============== ERROR COMMAND ================
def error_message():
    return f"Ada yang gagal diproses. Coba cek lagi perintahnya atau buka `{baseConfig.commandPrefix}help`."


ALLOWED_SERVER_IDS = frozenset(
    {
        1273463276847632405,
        1010450041514754109,
        648563331162177536,
        1238540250494533692,
    }
)


async def server_permission(ctx):
    return bool(ctx.guild and ctx.guild.id in ALLOWED_SERVER_IDS)


async def admin_permission(ctx):
    if ctx.author.id not in baseConfig.adminIds:
        await ctx.send("Perintah ini khusus admin Agus.")
        return False
    return True


# =============== Read File =======================
FILE_PATH = "services/announcement_channel_ids.json"
FILE_PATH_DUMMY = "services/announcement_test.json"
async def read_channel_ids():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

async def add_chanel_id(id, role_id):
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_map = {
        "id": id,
        "role_id": role_id
    }
    if any(str(item.get("id")) == str(id) for item in data):
        return False

    data.append(new_map)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return True


async def delete_channel_id(channel_id):
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_length = len(data)

    data = [item for item in data if str(item["id"]) != str(channel_id)]

    if len(data) < original_length:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return True

    return False

def compare_output(runs):
    return "\n".join([f"{k}/{c}/{h} → {s}" for k, c, h, s in runs])


# ==================== LOGGER =====================
LOG_CHANNEL_ID = 1446026484824412281
async def send_log_simple(bot, message: str):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print(f"[LOGGER] Channel {LOG_CHANNEL_ID} tidak ditemukan di cache.")
