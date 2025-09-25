import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from services.api_service import api_service
from utils import (
    ppc_type_parse,
    merge_images_horizontal,
    server_map,
    wz_embed,
    error_message,
)
from discord import Embed
from models import PpcModel, PpcBoss
from services.ppc_service import ppc_service
from io import BytesIO
from config import baseConfig
import time
from services.warzone_service import warzone_service
from translate_korea import TranslateKorea
from services.ppc_timer_service import ppc_timer

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} sudah online!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(error_message())
    elif isinstance(error, commands.BadArgument):
        await ctx.send(error_message())
    else:
        await ctx.send(error_message())

@bot.command()
async def help(ctx):
    embed = Embed(
        title="**Help**", description="List of commands:", color=discord.Color.red()
    )
    embed.add_field(
        name="!ppc (server) (type). Ex: !ppc asia ultimate",
        value="Shows current PPC bosses based on server and type (Ultimate/Advanced)",
        inline=False,
    )
    embed.add_field(
        name="!predppc (type). Ex: !predppc ultimate",
        value="Shows global server PPC prediction based on Korea server",
        inline=False,
    )
    embed.add_field(
        name="!wz (server). Ex: !wz asia",
        value="Shows warzone stage based on server",
        inline=False,
    )
    embed.add_field(
        name="!predwz. Ex: !predwz",
        value="Shows global next Warzone prediction base on Korea server",
        inline=False,
    )
    embed.add_field(
        name="!ultiscore (difficulty) (time). Ex: !ultiscore hell 10",
        value="Shows PPC ultimate score based on difficulty",
        inline=False,
    ),
    embed.add_field(
        name="!ultitotalscore (knight) (chaos) (hell). Ex: !ultitotalscore 8 8 10",
        value="Calculate total score based on each difficulty's timer",
        inline=False,
    )
    await ctx.send(embed=embed)

@bot.command()
async def ppc(ctx, server, type):
    try:
        bosses = ppc_service.get_current_ppc_bosses(server_map(server), type)

        boss_names = "\n".join([f"**{b['name']}**" for b in bosses])
        embed = Embed(
            title=f"PPC {type}", description=boss_names, color=discord.Color.blue()
        )

        merged_img = await merge_images_horizontal(b["imgUrl"] for b in bosses)

        file = discord.File(merged_img, filename="bosses.png")
        embed.set_image(url="attachment://bosses.png")

        await ctx.send(embed=embed, file=file)
    except:
        await ctx.send(error_message())

@bot.command()
async def predppc(ctx, type):
    try:
        ppc_item = ppc_service.get_current_ppc_item("ap", type)
        if type.lower() == "ultimate":
            idx = 0
        else:
            idx = 1
        week_json = api_service.ppc_week("kr", ppc_item["activity"] + idx, type)
        boss_names = "\n".join(
            [f"• {b['name']}" for b in week_json["data"]["ppc"]["bosses"]]
        )
        img_urls = [
            f"{baseConfig.baseImgUrl}{b['icon']}.webp"
            for b in week_json["data"]["ppc"]["bosses"]
        ]

        embed = Embed(
            title=f"Week 1", description=boss_names, color=discord.Color.blue()
        )

        start_time = time.perf_counter()
        merged_img = await merge_images_horizontal(img_urls)
        end_time = time.perf_counter()
        print(f"Week 1: {(end_time - start_time):.4f}")
        file = discord.File(merged_img, filename=f"bosses.png")
        embed.set_image(url=f"attachment://bosses.png")

        start_time = time.perf_counter()
        await ctx.send(
            content=f"PPC {type} boss prediction for the next 3 weeks:",
            embed=embed,
            file=file,
        )
        end_time = time.perf_counter()
        print(f"Uploading time: {(end_time - start_time):.4f}")
    except:
        await ctx.send(error_message())

@bot.command()
async def wz(ctx, server):
    try:
        current_wz = warzone_service.get_wz_map(server)
        print(current_wz)
        embed = wz_embed(f"**Current Warzone on {server} server!**", current_wz)
        await ctx.send(embed=embed)
    except:
        await ctx.send(error_message())

@bot.command()
async def predwz(ctx):
    try:
        current_wz = warzone_service.get_wz_map("asia")
        pred_id = current_wz["activity"] - 1
        pred_wz = warzone_service.get_wz_map("korea", pred_id)
        pred_wz["area"] = [
            TranslateKorea.translate_korea_warzone(area) for area in pred_wz["area"]
        ]
        embed = wz_embed(f"**Warzone prediction on asia server!**", pred_wz)
        await ctx.send(embed=embed)
    except:
        await ctx.send(error_message())

@bot.command()
async def ultitotalscore(ctx, knight: int, chaos: int, hell: int):
    try:
        total_score = ppc_timer.get_total_score(knight, chaos, hell)
        embed = Embed(
            title=f"Total score: ",
            description=f"**{total_score}**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send(error_message())

@bot.command()
async def ultiscore(ctx, difficulty, time: int):
    try:
        score = ppc_timer.get_score(time, difficulty.capitalize())
        embed = Embed(
            title=f"{difficulty.capitalize()} {time}s score:",
            description=f"**{score}**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send(error_message())

bot.run(TOKEN)