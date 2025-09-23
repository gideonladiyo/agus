import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api_service import api_service
from utils import ppc_type_parse

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
    response = "\n\n".join([f"**{boss['name']}**\n{boss['imgUrl']}" for boss in bosses])
    await ctx.send(response)

# Jalankan bot dengan token dari .env
bot.run(TOKEN)
