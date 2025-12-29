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
    ppc_boss_stat_embed,
    add_chanel_id,
    delete_channel_id,
    send_log_simple
)
from discord import Embed
from services.ppc_service import ppc_service
from services.warzone_service import warzone_service
from services.twitter_webhook import twitter_task

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

LOG_CHANNEL_ID = 1446026484824412281

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} sudah online!")
    twitter_task.start(bot)

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
    await server_permission(ctx)
    await send_log_simple(bot,f"[CMD] {ctx.author} executing: {ctx.message.content}")
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
        name="!ult (difficulty) (time) — Ex: `!ult hell 10`",
        value="Shows PPC Ultimate score based on difficulty and kill time (seconds).",
        inline=False,
    )
    embed.add_field(
        name="!ulttotal (knight) (chaos) (hell) — Ex: `!ulttotal 8 8 10`",
        value="Calculate total Ultimate score from each difficulty's timer (seconds).",
        inline=False,
    )
    embed.add_field(
        name="!adv (difficulty) (time) — Ex: `!adv Knight 5`",
        value="Shows PPC Advanced score based on difficulty and kill time (seconds).",
        inline=False,
    )
    embed.add_field(
        name="!advtotal (knight) (chaos) (hell) — Ex: `!advtotal 7 7 7`",
        value="Calculate total Advanced score from each difficulty's timer (seconds).",
        inline=False,
    )
    embed.add_field(
        name="!boss (boss-slug) — Ex: `!boss ephialtes`",
        value="Return boss stats based on boss slug/name. Use lowercase slug when available.",
        inline=False,
    )
    embed.add_field(
        name="!boss list — Ex: `!boss list`",
        value="Show list of available PPC bosses and their slugs.",
        inline=False,
    )

    await ctx.send(embed=embed)

@bot.command()
async def ppc(ctx, server, type):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {ctx.message.content}")
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
        await ctx.send(embed=Embed(
            title="**This command is deprecated**",
            color=discord.Color.red()
        ))
    except:
        await ctx.send(
            embed=Embed(
                title="**This command is deprecated**", color=discord.Color.red()
            )
        )

@bot.command()
async def wz(ctx, server):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {ctx.message.content}")
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
        await ctx.send(
            embed=Embed(
                title="**This command is deprecated**", color=discord.Color.red()
            )
        )
    except:
        await ctx.send(
            embed=Embed(
                title="**This command is deprecated**", color=discord.Color.red()
            )
        )

@bot.command()
async def ulttotal(ctx, knight: int, chaos: int, hell: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {ctx.message.content}")
        try:
            if knight > 60 or chaos > 60 or hell > 60:
                await ctx.send("Timer must >60s")
                return
            else:
                total_score = ppc_service.get_total_score(knight, chaos, hell, "ultimate")
                embed = Embed(
                    title=f"Total score: ",
                    description=f"**{total_score}**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
        except:
            await ctx.send("Command must contain knight, chaos, and hell time. ex: `!ulttotal 8 9 10`, means 8 knight, 9 chaos, 10 hell")

@bot.command()
async def ult(ctx, difficulty, time: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {ctx.message.content}")
        try:
            if time > 60:
                await ctx.send("Timer must >60s")
                return
            else:
                score = ppc_service.get_score(time, difficulty.capitalize(), "ultimate")
                embed = Embed(
                    title=f"{difficulty.capitalize()} {time}s score:",
                    description=f"**{score}**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
        except:
            await ctx.send(error_message())


@bot.command()
async def advtotal(ctx, knight: int, chaos: int, hell: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {ctx.message.content}")
        try:
            if knight > 60 or chaos > 60 or hell > 60:
                await ctx.send("Timer must >60s")
                return
            else:
                total_score = ppc_service.get_total_score(knight, chaos, hell, "advanced")
                embed = Embed(
                    title=f"Total score: ",
                    description=f"**{total_score}**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
        except:
            await ctx.send(
                "Command must contain knight, chaos, and hell time. ex: `!advtotal 8 9 10`, means 8 knight, 9 chaos, 10 hell"
            )

@bot.command()
async def adv(ctx, difficulty, time: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {ctx.message.content}")
        try:
            if time > 60:
                await ctx.send("Timer must >60s")
                return
            else:
                score = ppc_service.get_score(time, difficulty.capitalize(), "advanced")
                embed = Embed(
                    title=f"{difficulty.capitalize()} {time}s score:",
                    description=f"**{score}**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
        except:
            await ctx.send(error_message())

@bot.command()
async def boss(ctx, name):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {ctx.message.content}")
        try:
            if name == "list":
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
                await ctx.send(embed = embed)
                return
            else:
                boss_data = ppc_service.get_boss_stat(name)
                if boss_data == None:
                    await ctx.send("Boss data not found, please use command `!boss list` to see list of bosses")
                    return
                else:
                    print(boss_data["name"])
                    embed = ppc_boss_stat_embed(boss_data)
                    await ctx.send(embed = embed)
                    return
        except:
            await ctx.send(error_message())

@bot.command()
async def add_channel_id(ctx, id, role_id):
    if await add_chanel_id(id, role_id):
        await ctx.send("Successfully added channel id!")
    else:
        await ctx.send("Failed to add channel id!")

@bot.command()
async def delete_channel_id(ctx, id):
    if await delete_channel_id(id):
        await ctx.send("Successfully delete channel id!")
    else:
        await ctx.send("Failed to delete channel id!")

bot.run(TOKEN)