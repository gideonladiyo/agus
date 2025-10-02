from PIL import Image
from io import BytesIO
import aiohttp
import asyncio
from discord import Embed
import discord

def ppc_type_parse(type: str):
    type_map = {
        "ultimate": 4,
        "advanced": 3
    }
    return type_map.get(type.lower(), None)

def server_map(server):
    servers = {
        "asia": "ap",
        "korea": "kr",
        "china": "cn",
        "japan": "jp" 
    }
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

    # return BytesIO
    bio = BytesIO()
    merged.save(bio, format="PNG")
    bio.seek(0)
    return bio

def wz_embed(title, json):
    embed = Embed(title=title, color=discord.Color.red())

    for wz_item in json["area"]:
        # Buffs
        buffs_text = ""
        for buff in wz_item.get("buffs", []):
            buffs_text += (
                f"- {buff['name']}\n"
                f"  {buff['description']}\n"
            )

        # Weathers
        weathers_text = ""
        for w in wz_item.get("weathers", []):
            weathers_text += (
                f"- {w['name']}\n"
                f"  {w['description']}\n"
            )

        # Konten utama
        text_content = (
            f"{wz_item['description']}\n"
            f"{buffs_text}"
            f"{weathers_text}"
        )

        # Tambahin field ke embed
        embed.add_field(
            name=wz_item["name"],
            value=text_content if text_content.strip() else "No data",
            inline=True,
        )

    return embed

def ppc_boss_stat_embed(data):
    embed = Embed(
        title=data["name"],
        description=f"""
        **Weakness:** {data["weakness"]}
        
        **Start Time:** {data["start_time"]}s
        
        **HP:**
        Knight: {data["knight"]}
        Chaos: {data["chaos"]}
        Hell: {data["hell"]}
        """,
        color=discord.Color.red()
    )
    embed.set_image(url=data["img_url"])
    return embed

# ============== ERROR COMMAND ================
def error_message():
    return f"There is an error. Please check your command or check `!help` for list commands or ask <@{533104933168480286}> as the creator"

async def server_permission(ctx):
    server_ids = [1273463276847632405, 1010450041514754109]
    if ctx.guild.id not in server_ids:
        await ctx.send("These server doesn't have permission to use Agus")
    else:
        return