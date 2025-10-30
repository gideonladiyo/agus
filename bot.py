import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import (
    server_permission,
    merge_images_horizontal,
    server_map,
    wz_embed,
    error_message,
    ppc_boss_stat_embed
)
from discord import Embed
from services.ppc_service import ppc_service
from services.warzone_service import warzone_service
from logger import setup_logger
from helpers import send_score_embed, handle_command_error

logger = setup_logger(__name__)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f"✅ Bot {bot.user} is now online!")

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for bot commands."""
    if isinstance(error, commands.MissingRequiredArgument):
        logger.warning(f"Missing required argument in command: {error}")
        await ctx.send(f"❌ Missing argument: {error.param.name}. Use `!help` for command usage.")
    elif isinstance(error, commands.BadArgument):
        logger.warning(f"Bad argument in command: {error}")
        await ctx.send(f"❌ Invalid argument: {error}. Use `!help` for command usage.")
    elif isinstance(error, commands.CommandNotFound):
        logger.debug(f"Command not found: {error}")
        await ctx.send(f"❌ Command not found. Use `!help` to see available commands.")
    else:
        logger.error(f"Unexpected error: {error}", exc_info=True)
        await ctx.send(error_message())

@bot.command()
async def help(ctx):
    """Display help information for all available commands."""
    try:
        await server_permission(ctx)

        commands_list = [
            ("!ppc (server) (type). Ex: !ppc asia ultimate",
             "Shows current PPC bosses based on server and type (Ultimate/Advanced)"),
            ("!predppc (type). Ex: !predppc ultimate",
             "Shows global server PPC prediction based on Korea server (DEPRECATED)"),
            ("!wz (server). Ex: !wz asia",
             "Shows warzone stage based on server"),
            ("!predwz. Ex: !predwz",
             "Shows global next Warzone prediction base on Korea server (DEPRECATED)"),
            ("!ultiscore (difficulty) (time). Ex: !ultiscore hell 10",
             "Shows PPC Ultimate score based on difficulty and kill time"),
            ("!ultitotalscore (knight) (chaos) (hell). Ex: !ultitotalscore 8 8 10",
             "Calculate total score based on each difficulty's timer"),
            ("!advscore (difficulty) (time). Ex: !advscore Knight 5",
             "Shows PPC Advanced score based on difficulty and kill time"),
            ("!advtotalscore (knight) (chaos) (hell). Ex: !advtotalscore 7 7 7",
             "Calculate total score based on each difficulty's timer"),
            ("!ppcboss (bossname). Ex: !ppcboss ephialtes",
             "Return boss stats based on boss name in lowercase"),
            ("!ppcbosslist. Ex: !ppcbosslist",
             "Return boss name and slug"),
        ]

        embed = Embed(
            title="**Help**",
            description="List of commands:",
            color=discord.Color.red()
        )

        for name, value in commands_list:
            embed.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed)
        logger.info(f"Help command executed by user: {ctx.author}")
    except Exception as e:
        await handle_command_error(ctx, e, "help")

@bot.command()
async def ppc(ctx, server, type):
    """Display current PPC bosses for a server."""
    try:
        await server_permission(ctx)
        logger.info(f"PPC command: server={server}, type={type}")

        bosses = ppc_service.get_current_ppc_bosses(server_map(server), type)

        boss_names = "\n".join([f"**{b['name']}**" for b in bosses])
        embed = Embed(
            title=f"PPC {type}", description=boss_names, color=discord.Color.blue()
        )

        merged_img = await merge_images_horizontal(b["imgUrl"] for b in bosses)

        file = discord.File(merged_img, filename="bosses.png")
        embed.set_image(url="attachment://bosses.png")

        await ctx.send(embed=embed, file=file)
        logger.info(f"PPC command completed successfully for {server} {type}")
    except Exception as e:
        await handle_command_error(ctx, e, "ppc")

@bot.command()
async def predppc(ctx, type):
    """Deprecated command - PPC prediction is no longer available."""
    logger.info(f"Deprecated predppc command called by {ctx.author}")
    await ctx.send(embed=Embed(
        title="**This command is deprecated**",
        description="PPC prediction is no longer available.",
        color=discord.Color.red()
    ))

@bot.command()
async def wz(ctx, server):
    """Display current warzone information for a server."""
    try:
        await server_permission(ctx)
        logger.info(f"WZ command: server={server}")

        current_wz = warzone_service.get_wz_map(server)
        logger.debug(f"Warzone data retrieved: {current_wz}")

        embed = wz_embed(f"**Current Warzone on {server} server!**", current_wz)
        await ctx.send(embed=embed)
        logger.info(f"WZ command completed successfully for {server}")
    except Exception as e:
        await handle_command_error(ctx, e, "wz")

@bot.command()
async def predwz(ctx):
    """Deprecated command - Warzone prediction is no longer available."""
    logger.info(f"Deprecated predwz command called by {ctx.author}")
    await ctx.send(embed=Embed(
        title="**This command is deprecated**",
        description="Warzone prediction is no longer available.",
        color=discord.Color.red()
    ))

@bot.command()
async def ultitotalscore(ctx, knight: int, chaos: int, hell: int):
    """Calculate total PPC Ultimate score."""
    try:
        await server_permission(ctx)
        logger.info(f"Ultimate total score: K={knight}, C={chaos}, H={hell}")

        total_score = ppc_service.get_total_score(knight, chaos, hell, "ultimate")
        await send_score_embed(ctx, "Total score:", total_score)
        logger.info(f"Ultimate total score completed: {total_score}")
    except Exception as e:
        await handle_command_error(ctx, e, "ultitotalscore")

@bot.command()
async def ultiscore(ctx, difficulty, time: int):
    """Calculate PPC Ultimate score for a specific difficulty and time."""
    try:
        await server_permission(ctx)
        difficulty = difficulty.capitalize()
        logger.info(f"Ultimate score: {difficulty} {time}s")

        score = ppc_service.get_score(time, difficulty, "ultimate")
        await send_score_embed(ctx, f"{difficulty} {time}s score:", score)
        logger.info(f"Ultimate score completed: {score}")
    except Exception as e:
        await handle_command_error(ctx, e, "ultiscore")

@bot.command()
async def advtotalscore(ctx, knight: int, chaos: int, hell: int):
    """Calculate total PPC Advanced score."""
    try:
        await server_permission(ctx)
        logger.info(f"Advanced total score: K={knight}, C={chaos}, H={hell}")

        total_score = ppc_service.get_total_score(knight, chaos, hell, "advanced")
        await send_score_embed(ctx, "Total score:", total_score)
        logger.info(f"Advanced total score completed: {total_score}")
    except Exception as e:
        await handle_command_error(ctx, e, "advtotalscore")

@bot.command()
async def advscore(ctx, difficulty, time: int):
    """Calculate PPC Advanced score for a specific difficulty and time."""
    try:
        await server_permission(ctx)
        difficulty = difficulty.capitalize()
        logger.info(f"Advanced score: {difficulty} {time}s")

        score = ppc_service.get_score(time, difficulty, "advanced")
        await send_score_embed(ctx, f"{difficulty} {time}s score:", score)
        logger.info(f"Advanced score completed: {score}")
    except Exception as e:
        await handle_command_error(ctx, e, "advscore")

@bot.command()
async def ppcboss(ctx, name):
    """Display PPC boss statistics."""
    try:
        await server_permission(ctx)
        logger.info(f"PPC boss command: {name}")

        boss_data = ppc_service.get_boss_stat(name)
        logger.info(f"Boss data retrieved: {boss_data['name']}")

        embed = ppc_boss_stat_embed(boss_data)
        await ctx.send(embed=embed)
        logger.info(f"PPC boss command completed for {name}")
    except Exception as e:
        await handle_command_error(ctx, e, "ppcboss")

@bot.command()
async def ppcbosslist(ctx):
    """Display list of all PPC bosses."""
    try:
        await server_permission(ctx)
        logger.info("PPC boss list command")

        boss_list = ppc_service.get_boss_list()
        bosses_string = "\n".join(
            [
                f"- {boss_list['names'][i]} ({boss_list['slugs'][i]})"
                for i in range(len(boss_list["names"]))
            ]
        )
        embed = Embed(
            title="List PPC Bosses:",
            description=bosses_string,
            color=discord.Color.red()
        )
        embed.set_image(
            url="https://assets.huaxu.app/browse/glb/image/uifubenchallengemapboss/bosssingleimghard.png"
        )
        await ctx.send(embed=embed)
        logger.info("PPC boss list command completed")
    except Exception as e:
        await handle_command_error(ctx, e, "ppcbosslist")

bot.run(TOKEN)
