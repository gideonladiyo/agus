import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from services.api_service import api_service
from utils import ppc_type_parse, merge_images_horizontal, server_map, wz_embed
from discord import Embed
from models import PpcModel, PpcBoss
from services.ppc_service import ppc_service
from io import BytesIO
from config import baseConfig
import time
from services.warzone_service import warzone_service
from translate_korea import TranslateKorea

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
    bosses = ppc_service.get_current_ppc_bosses(server_map(server), type)

    boss_names = "\n".join([f"**{b['name']}**" for b in bosses])
    embed = Embed(
        title=f"PPC {type}", description=boss_names, color=discord.Color.blue()
    )

    merged_img = await merge_images_horizontal(b["imgUrl"] for b in bosses)

    file = discord.File(merged_img, filename="bosses.png")
    embed.set_image(url="attachment://bosses.png")

    await ctx.send(embed=embed, file=file)


@bot.command()
async def pred_ppc(ctx, type):
    ppc_item = ppc_service.get_current_ppc_item("ap", type)

    embeds = []
    files = []
    for i in range(3):
        week_json = api_service.ppc_week("kr", ppc_item["activity"] + i, type)
        # print(week_json)
        boss_names = "\n".join(
            [f"• {b['name']}" for b in week_json["data"]["ppc"]["bosses"]]
        )
        img_urls = [
            f"{baseConfig.baseImgUrl}{b['icon']}.webp"
            for b in week_json["data"]["ppc"]["bosses"]
        ]

        embed = Embed(
            title=f"Week {i+1}", description=boss_names, color=discord.Color.blue()
        )

        start_time = time.perf_counter()
        merged_img = await merge_images_horizontal(img_urls)
        end_time = time.perf_counter()
        print(f"Week {i+1}: {(end_time - start_time):.4f}")
        file = discord.File(merged_img, filename=f"bosses_{i}.png")
        embed.set_image(url=f"attachment://bosses_{i}.png")

        embeds.append(embed)
        files.append(file)

    start_time = time.perf_counter()
    await ctx.send(
        content=f"PPC {type} boss prediction for the next 3 weeks:",
        embeds=embeds,
        files=files,
    )
    end_time = time.perf_counter()
    print(f"Uploading time: {(end_time - start_time):.4f}")


@bot.command()
async def wz(ctx, server):
    current_wz = warzone_service.get_wz_map(server)
    embed = await wz_embed(f"**Current Warzone on {server} server!**", current_wz)
    await ctx.send(embed=embed)


@bot.command()
async def next_wz(ctx):
    current_wz = warzone_service.get_wz_map("asia")
    pred_id = current_wz["activity"] - 1
    pred_wz = warzone_service.get_wz_map("korea", pred_id)
    pred_wz["area"] = [TranslateKorea.translate_korea_warzone(area) for area in pred_wz["area"]]
    embed = wz_embed(
        f"**Warzone prediction on asia server!**",
        pred_wz
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)
