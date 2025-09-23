import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from services.api_service import api_service
from utils import ppc_type_parse, merge_images_horizontal, server_map
from discord import Embed
from models import PpcModel, PpcBoss
from services.ppc_service import ppc_service
from io import BytesIO
from config import baseConfig

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} sudah online!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Halo {ctx.author.mention}")

@bot.command()
async def ppc(ctx, server, type):
    bosses = ppc_service.get_current_ppc_bosses(server_map(server), ppc_type_parse(type))

    boss_names = "\n".join([f"**{b['name']}**" for b in bosses])
    embed = Embed(
        title=f"PPC {type}",
        description=boss_names,
        color=discord.Color.blue()
    )
    
    merged_img = merge_images_horizontal(b["imgUrl"] for b in bosses)
    
    file = discord.File(merged_img, filename="bosses.png")
    embed.set_image(url="attachment://bosses.png")
    
    await ctx.send(embed=embed, file=file)
    os.remove(merged_img)

@bot.command()
async def pred_ppc(ctx, type):
    ppc_item = ppc_service.get_current_ppc_item("ap", type)

    embeds = []
    files = []
    for i in range(3):
        week_json = api_service.ppc_week("kr", ppc_item["activity"]+i, type)
        print(week_json)
        boss_names = "\n".join([f"• {b['name']}" for b in week_json["data"]["ppc"]["bosses"]])
        img_urls = [f"{baseConfig.baseImgUrl}{b['icon']}.webp" for b in week_json["data"]["ppc"]["bosses"]]
        
        print(img_urls)

        embed = Embed(
            title=f"Week {i+1}", description=boss_names, color=discord.Color.blue()
        )

        merged_img = merge_images_horizontal(img_urls)
        file = discord.File(merged_img, filename=f"bosses_{i}.png")
        embed.set_image(url=f"attachment://bosses_{i}.png")

        embeds.append(embed)
        files.append(file)

    await ctx.send(
        content="📅 Prediksi Boss PPC 3 minggu ke depan:", embeds=embeds, files=files
    )

bot.run(TOKEN)
