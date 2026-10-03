import os
import asyncio
from io import BytesIO
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils import (
    server_permission,
    merge_images_horizontal,
    server_map,
    wz_embed,
    error_message,
    ppc_boss_stat_embed,
    memory_embed,
    add_chanel_id,
    delete_channel_id as delete_channel_id_config,
    send_log_simple,
    compare_output,
    admin_permission,
)
from discord import Embed
from services.ppc_service import ppc_service
from services.warzone_service import warzone_service
from services.memories_service import memories_service
from services.team_service import TeamNotFound, team_service
from config import baseConfig
import math

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
COMMAND_PREFIX = baseConfig.commandPrefix


class AgusBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()


bot = AgusBot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)


@bot.check
async def allowed_server_only(ctx):
    return await server_permission(ctx)

LOG_CHANNEL_ID = 1446026484824412281


def command_invocation(ctx):
    if ctx.interaction:
        return f"/{ctx.command.qualified_name}"
    return ctx.message.content


async def defer_response(ctx):
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} sudah online!")
    # twitter_task.start(bot)

@bot.event
async def on_command_error(ctx, error):
    if not await server_permission(ctx) or isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(error_message())
    elif isinstance(error, commands.BadArgument):
        await ctx.send(error_message())
    else:
        await ctx.send(error_message())


@bot.hybrid_command(description="Show the list of available commands")
@app_commands.guild_only()
async def help(ctx):
    if not await server_permission(ctx):
        return
    await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
    embed = Embed(
        title="Help", description="Available commands:", color=discord.Color.red()
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}help",
        value="Show this command list.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}ult <difficulty> <time>",
        value="Show the Ultimate PPC score for a difficulty and clear time in seconds.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}ulttotal <knight> <chaos> <hell>",
        value="Calculate the total Ultimate PPC score from the three clear times in seconds.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}adv <difficulty> <time>",
        value="Show the Advanced PPC score for a difficulty and clear time in seconds.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}advtotal <knight> <chaos> <hell>",
        value="Calculate the total Advanced PPC score from the three clear times in seconds.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}ib <timer> <buff>",
        value="Calculate the Intensive Battle score using a timer and buff.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}comparetotal <runs> vs <runs>",
        value="Compare the total scores of two or more PPC runs. Enter each run as Knight, Chaos, and Hell times.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}boss <name|list>",
        value="Show boss stats, or enter `list` to see the available boss names and slugs.",
        inline=False,
    )
    embed.add_field(
        name=f"{COMMAND_PREFIX}team <element> <mode> or {COMMAND_PREFIX}team <meta|f2p>",
        value="Show a team image by element and mode, or a full list (Meta: A1:J44; F2P: L1:U44).",
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.hybrid_command(with_app_command=False)
@app_commands.describe(server="Choose a server", type="Choose Ultimate or Advanced PPC")
@app_commands.choices(
    server=[
        app_commands.Choice(name=s.title(), value=s)
        for s in ("asia", "korea", "china", "japan")
    ],
    type=[
        app_commands.Choice(name=s.title(), value=s) for s in ("ultimate", "advanced")
    ],
)
async def ppc(ctx, server, type):
    if await server_permission(ctx):
        await defer_response(ctx)
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
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


@bot.hybrid_command(with_app_command=False)
@app_commands.choices(
    type=[
        app_commands.Choice(name=s.title(), value=s) for s in ("ultimate", "advanced")
    ]
)
async def predppc(ctx, type="ultimate"):
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


@bot.hybrid_command(with_app_command=False)
@app_commands.choices(
    server=[
        app_commands.Choice(name=s.title(), value=s)
        for s in ("asia", "korea", "china", "japan")
    ]
)
async def wz(ctx, server):
    if await server_permission(ctx):
        await defer_response(ctx)
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
        try:
            current_wz = warzone_service.get_wz_map(server)
            print(current_wz)
            embed = wz_embed(f"**Current Warzone on {server} server!**", current_wz)
            await ctx.send(embed=embed)
        except:
            await ctx.send(error_message())


@bot.hybrid_command(with_app_command=False)
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


@bot.hybrid_command(description="Calculate the total Ultimate PPC score from three clear times")
@app_commands.guild_only()
@app_commands.describe(
    knight="Knight clear time in seconds",
    chaos="Chaos clear time in seconds",
    hell="Hell clear time in seconds",
)
async def ulttotal(ctx, knight: int, chaos: int, hell: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
        try:
            if knight > 60 or chaos > 60 or hell > 60:
                await ctx.send("Each timer must be 60 seconds or less.")
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
            await ctx.send(
                f"Enter the Knight, Chaos, and Hell times. Example: `{COMMAND_PREFIX}ulttotal 8 9 10` means 8 seconds for Knight, 9 for Chaos, and 10 for Hell."
            )


@bot.hybrid_command(description="Show the Ultimate PPC score for a difficulty and clear time")
@app_commands.guild_only()
@app_commands.choices(
    difficulty=[
        app_commands.Choice(name=s.title(), value=s)
        for s in ("knight", "chaos", "hell")
    ]
)
@app_commands.describe(time="Clear time in seconds")
async def ult(ctx, difficulty, time: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
        try:
            if time > 60:
                await ctx.send("Timer must be 60 seconds or less.")
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


@bot.hybrid_command(description="Compare the total scores of two or more PPC runs")
@app_commands.guild_only()
@app_commands.describe(runs="Runs formatted as: Knight Chaos Hell vs Knight Chaos Hell")
async def comparetotal(ctx, *, runs: str):
    if not await server_permission(ctx):
        return
    try:
        args = runs.split()

        if "vs" not in args:
            await ctx.send(f"Format: {COMMAND_PREFIX}comparetotal <runs> vs <runs>")
            return

        split = args.index("vs")
        left = args[:split]
        right = args[split+1:]

        if len(left) % 3 != 0 or len(right) % 3 != 0:
            await ctx.send("Each run must be 3 numbers (knight chaos hell)")
            return

        left_runs, left_total = ppc_service.parse_runs(left)
        right_runs, right_total = ppc_service.parse_runs(right)

        diff = left_total - right_total

        embed = Embed(
            title="Score comparison",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="LEFT",
            value=f"{compare_output(left_runs)}\n**Total: {left_total}**"
        )

        embed.add_field(
            name="RIGHT",
            value=f"{compare_output(right_runs)}\n**Total: {right_total}**"
        )

        if diff > 0:
            result = f"Left wins **+{abs(diff)}**"
        elif diff < 0:
            result = f"Right wins **+{abs(diff)}**"
        else:
            result = "Draw"

        embed.add_field(
            name="Result",
            value=result
        )

        await ctx.send(embed=embed)
    except:
        await ctx.send("Invalid input format")


@bot.hybrid_command(description="Calculate the total Advanced PPC score from three clear times")
@app_commands.guild_only()
@app_commands.describe(
    knight="Knight clear time in seconds",
    chaos="Chaos clear time in seconds",
    hell="Hell clear time in seconds",
)
async def advtotal(ctx, knight: int, chaos: int, hell: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
        try:
            if knight > 60 or chaos > 60 or hell > 60:
                await ctx.send("Each timer must be 60 seconds or less.")
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
                f"Enter the Knight, Chaos, and Hell times. Example: `{COMMAND_PREFIX}advtotal 8 9 10` means 8 seconds for Knight, 9 for Chaos, and 10 for Hell."
            )


@bot.hybrid_command(description="Show the Advanced PPC score for a difficulty and clear time")
@app_commands.guild_only()
@app_commands.choices(
    difficulty=[
        app_commands.Choice(name=s.title(), value=s)
        for s in ("knight", "chaos", "hell")
    ]
)
@app_commands.describe(time="Clear time in seconds")
async def adv(ctx, difficulty, time: int):
    if await server_permission(ctx):
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
        try:
            if time > 60:
                await ctx.send("Timer must be 60 seconds or less.")
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


@bot.hybrid_command(name="ib", description="Calculate the Intensive Battle score using a timer and buff")
@app_commands.guild_only()
@app_commands.describe(timer="Clear time in seconds", buff="Buff bonus")
@app_commands.choices(
    buff=[
        app_commands.Choice(name="15.5% Bonus", value=1),
        app_commands.Choice(name="25% Bonus", value=2),
    ]
)
async def ib(
    ctx: commands.Context, timer: int, buff: int
):
    if await server_permission(ctx):
        await send_log_simple(
            bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}"
        )
        try:
            score = ppc_service.ib_timer(timer, buff)
            embed = Embed(
                title=f"Intensive Battle {timer}s score:",
                description=f"**{math.floor(score + 0.5)}**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return
        except:
            print(error_message())
            await ctx.send(error_message())


@bot.hybrid_command(description="Show boss stats or list available bosses")
@app_commands.guild_only()
@app_commands.describe(name="Boss slug, or `list` to show available bosses")
async def boss(ctx, name):
    if await server_permission(ctx):
        await defer_response(ctx)
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
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
                    await ctx.send(f"Boss data not found, please use command {COMMAND_PREFIX}boss list to see list of bosses")
                    return
                else:
                    print(boss_data["name"])
                    embed = ppc_boss_stat_embed(boss_data)
                    await ctx.send(embed = embed)
                    return
        except:
            await ctx.send(error_message())


@bot.hybrid_command(aliases=["get_memory"], with_app_command=False)
async def memory(ctx, *, slug: str):
    if await server_permission(ctx):
        await defer_response(ctx)
        await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
        try:
            memory = memories_service.getMemory(slug)
            if not memory:
                await ctx.send(f"Memory `{slug}` not found. Check spelling")
                return
            embed = memory_embed(memory)
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error in get_memory: {e}")
            await ctx.send(error_message())


@bot.hybrid_command(description="Show a Meta or F2P team list, or a team for an element and mode")
@app_commands.guild_only()
@app_commands.describe(
    target="Team element, or meta/f2p for a full list",
    mode="Team mode (required when target is an element)",
)
async def team(ctx, target: str, mode: str = None):
    if not await server_permission(ctx):
        return
    await defer_response(ctx)
    await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
    try:
        section = target.strip().casefold()
        if mode is None:
            if section not in team_service.section_areas:
                await ctx.send(
                    f"Usage: `{COMMAND_PREFIX}team <element> <mode>`, "
                    f"`{COMMAND_PREFIX}team meta`, or `{COMMAND_PREFIX}team f2p`."
                )
                return
            image = await asyncio.to_thread(team_service.get_team_section_image, section)
            title = f"{section.upper()} Team List"
            filename = f"team_{section}.png"
        else:
            image = await asyncio.to_thread(team_service.get_team_image, target, mode)
            title = f"{target.title()} {mode.title()} Team"
            filename = f"team_{target}_{mode}.png"

        embed = Embed(title=title, color=discord.Color.blue())
        embed.set_image(url=f"attachment://{filename}")
        await ctx.send(embed=embed, file=discord.File(BytesIO(image), filename=filename))
    except TeamNotFound:
        await ctx.send(f"Team `{target} {mode or ''}` tidak ditemukan di sheet `meta_team`.")
    except Exception as error:
        print(f"Team command error: {type(error).__name__}: {error}")
        await ctx.send(error_message())


@bot.hybrid_command(
    name="add-channel-id", aliases=["add_channel_id"], with_app_command=False
)
async def add_channel_id(ctx, id, role_id):
    if not await server_permission(ctx):
        return
    await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
    if not await admin_permission(ctx):
        return
    try:
        if await add_chanel_id(id, role_id):
            await ctx.send("Channel itu sudah berhasil ditambahkan.")
        else:
            await ctx.send("Channel itu sepertinya sudah terdaftar.")
    except Exception:
        await ctx.send(error_message())


@bot.hybrid_command(
    name="delete-channel-id", aliases=["delete_channel_id"], with_app_command=False
)
async def delete_channel_id(ctx, id):
    if not await server_permission(ctx):
        return
    await send_log_simple(bot, f"[CMD] {ctx.author} executing: {command_invocation(ctx)}")
    if not await admin_permission(ctx):
        return
    try:
        if await delete_channel_id_config(id):
            await ctx.send("Channel itu sudah dihapus dari daftar.")
        else:
            await ctx.send("Channel itu tidak ditemukan di daftar.")
    except Exception:
        await ctx.send(error_message())


if __name__ == "__main__":
    bot.run(TOKEN)
