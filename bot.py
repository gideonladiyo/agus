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
# from translate_korea import TranslateKorea

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
    await server_permission(ctx)
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
        value="Shows PPC Ultimate score based on difficulty and kill time",
        inline=False,
    ),
    embed.add_field(
        name="!ultitotalscore (knight) (chaos) (hell). Ex: !ultitotalscore 8 8 10",
        value="Calculate total score based on each difficulty's timer",
        inline=False,
    ),
    embed.add_field(
        name="!advscore (difficulty) (time). Ex: !advscore Knight 5",
        value="Shows PPC Advanced score based on difficulty and kill time",
        inline=False
    ),
    embed.add_field(
        name="!advtotalscore (knight) (chaos) (hell). Ex: !advtotalscore 7 7 7",
        value="Calculate total score based on each difficulty's timer",
        inline=False
    ),
    embed.add_field(
        name="!ppcboss (bossname). Ex: !ppcboss ephialtes",
        value="Return boss stats based on boss name in lowercase",
        inline=False,
    ),
    embed.add_field(
        name="!ppcbosslist. Ex: !ppcbosslist",
        value="Return boss name and slug",
        inline=False,
    ),
    
    await ctx.send(embed=embed)

@bot.command()
async def ppc(ctx, server, type):
    await server_permission(ctx)
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
    # await server_permission(ctx)
    # try:
    #     ppc_item = ppc_service.get_current_ppc_item("ap", type)
    #     if type.lower() == "ultimate":
    #         idx = 0
    #     else:
    #         idx = 1
    #     week_json = api_service.ppc_week("kr", ppc_item["activity"] + idx, type)
    #     boss_names = "\n".join(
    #         [f"• {b['name']}" for b in week_json["data"]["ppc"]["bosses"]]
    #     )
    #     img_urls = [
    #         f"{baseConfig.baseImgUrl}{b['icon']}.webp"
    #         for b in week_json["data"]["ppc"]["bosses"]
    #     ]

    #     embed = Embed(
    #         title=f"Week 1", description=boss_names, color=discord.Color.blue()
    #     )

    #     start_time = time.perf_counter()
    #     merged_img = await merge_images_horizontal(img_urls)
    #     end_time = time.perf_counter()
    #     print(f"Week 1: {(end_time - start_time):.4f}")
    #     file = discord.File(merged_img, filename=f"bosses.png")
    #     embed.set_image(url=f"attachment://bosses.png")

    #     start_time = time.perf_counter()
    #     await ctx.send(
    #         content=f"PPC {type} boss prediction for the next 3 weeks:",
    #         embed=embed,
    #         file=file,
    #     )
    #     end_time = time.perf_counter()
    #     print(f"Uploading time: {(end_time - start_time):.4f}")
    # except:
    #     await ctx.send(error_message())

@bot.command()
async def wz(ctx, server):
    await server_permission(ctx)
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
    # await server_permission(ctx)
    # try:
    #     current_wz = warzone_service.get_wz_map("asia")
    #     pred_id = current_wz["activity"] - 1
    #     pred_wz = warzone_service.get_wz_map("korea", pred_id)
    #     pred_wz["area"] = [
    #         TranslateKorea.translate_korea_warzone(area) for area in pred_wz["area"]
    #     ]
    #     embed = wz_embed(f"**Warzone prediction on asia server!**", pred_wz)
    #     await ctx.send(embed=embed)
    # except Exception as e:
    #     await ctx.send(error_message())
    #     print(repr(e))
    #     traceback.print_exc()

@bot.command()
async def ultitotalscore(ctx, knight: int, chaos: int, hell: int):
    await server_permission(ctx)
    try:
        total_score = ppc_service.get_total_score(knight, chaos, hell, "ultimate")
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
    await server_permission(ctx)
    try:
        score = ppc_service.get_score(time, difficulty.capitalize(), "ultimate")
        embed = Embed(
            title=f"{difficulty.capitalize()} {time}s score:",
            description=f"**{score}**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send(error_message())


@bot.command()
async def advtotalscore(ctx, knight: int, chaos: int, hell: int):
    await server_permission(ctx)
    try:
        total_score = ppc_service.get_total_score(knight, chaos, hell, "advanced")
        embed = Embed(
            title=f"Total score: ",
            description=f"**{total_score}**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send(error_message())


@bot.command()
async def advscore(ctx, difficulty, time: int):
    await server_permission(ctx)
    try:
        score = ppc_service.get_score(time, difficulty.capitalize(), "advanced")
        embed = Embed(
            title=f"{difficulty.capitalize()} {time}s score:",
            description=f"**{score}**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send(error_message())

@bot.command()
async def ppcboss(ctx, name):
    await server_permission(ctx)
    try:
        boss_data = ppc_service.get_boss_stat(name)
        print(boss_data["name"])
        embed = ppc_boss_stat_embed(boss_data)
        await ctx.send(embed = embed)
    except:
        await ctx.send(error_message())

@bot.command()
async def ppcbosslist(ctx):
    await server_permission(ctx)
    try:
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
    except:
        await ctx.send(error_message())

bot.run(TOKEN)
