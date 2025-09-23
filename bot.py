import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api_service import api_service
from utils import ppc_type_parse, merge_images_horizontal
from discord import Embed

# Load .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup intents
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
async def ping(ctx):
    await ctx.send("Pong! 🏓")

@bot.command()
async def ppc(ctx, server: str, type: str):
    bosses = api_service.ppc_boss(server, ppc_type_parse(type))
    # response = "\n\n".join([f"**{boss['name']}**\n{boss['imgUrl']}" for boss in bosses])
    # await ctx.send(response)

    # embeds = []
    # for boss in bosses:
    #     embed = Embed(title=boss["name"])
    #     embed.set_image(url=boss["imgUrl"])
    #     embeds.append(embed)

    # await ctx.send(embeds=embeds)

    boss_names = "\n".join([f"**{b['name']}**" for b in bosses])
    embed = discord.Embed(
        title=f"PPC {type}",
        description=boss_names,
        color=discord.Color.blue()
    )
    
    merged_img = merge_images_horizontal(b["imgUrl"] for b in bosses)
    
    file = discord.File(merged_img, filename="bosses.png")
    embed.set_image(url="attachment://bosses.png")
    
    await ctx.send(embed=embed, file=file)
    os.remove(merged_img)

# Jalankan bot dengan token dari .env
bot.run(TOKEN)
