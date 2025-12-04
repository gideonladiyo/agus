import os
import time
import logging
from logging.handlers import RotatingFileHandler
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
)
from discord import Embed
from services.ppc_service import ppc_service
from services.warzone_service import warzone_service

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# Optional: channel to receive log summaries (ID as int)
LOG_CHANNEL_ID = os.getenv("1446026484824412281")  # example: "123456789012345678"
# How often (seconds) to allow sending log messages to the log channel
LOG_SEND_COOLDOWN_SECONDS = int(os.getenv("LOG_SEND_COOLDOWN_SECONDS") or 10)

# ---------- Setup logger ----------
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "agus_bot.log")
logger = logging.getLogger("agus_bot")
logger.setLevel(logging.INFO)
# Rotating handler to avoid infinite growth
handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
# Also log to console for realtime visibility
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# ---------- Bot setup ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# cooldown for sending log messages to channel
_last_log_send_time = 0.0


async def maybe_send_log_channel(summary_title: str, summary_body: str):
    """
    Send a short embed with log summary to LOG_CHANNEL_ID (if configured),
    but respect a cooldown to avoid spamming the channel.
    """
    global _last_log_send_time
    try:
        if not LOG_CHANNEL_ID:
            return False
        # ensure it's an int
        channel_id = int(LOG_CHANNEL_ID)
        now = time.time()
        if now - _last_log_send_time < LOG_SEND_COOLDOWN_SECONDS:
            # skip due to cooldown
            return False
        ch = bot.get_channel(channel_id)
        if ch is None:
            # try fetch (in case not cached)
            try:
                ch = await bot.fetch_channel(channel_id)
            except Exception as e:
                logger.warning(f"Unable to fetch log channel {channel_id}: {e}")
                return False
        # build embed
        embed = Embed(
            title=summary_title,
            description=summary_body[:1900],
            color=discord.Color.blue(),
        )
        # include absolute path to log file on server
        abs_log_path = os.path.abspath(LOG_FILE)
        embed.set_footer(text=f"Log file: {abs_log_path}")
        try:
            await ch.send(embed=embed)
            _last_log_send_time = now
            return True
        except Exception as e:
            logger.warning(f"Failed to send log embed to channel {channel_id}: {e}")
            return False
    except Exception as e:
        logger.exception("Unexpected error in maybe_send_log_channel")
        return False


# ---------- Events ----------
@bot.event
async def on_ready():
    logger.info(f"Bot {bot.user} sudah online!")
    # notify log channel that bot started
    await maybe_send_log_channel(
        "Bot started",
        f"Bot `{bot.user}` started and logging to `{os.path.abspath(LOG_FILE)}`.",
    )


@bot.event
async def on_command_error(ctx, error):
    # improved handling + logging
    try:
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error_message())
            logger.info(
                f"MissingRequiredArgument | user={ctx.author} | channel={getattr(ctx.channel,'id',None)} | command={getattr(ctx.command,'name',None)} | message={ctx.message.content}"
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error_message())
            logger.info(
                f"BadArgument | user={ctx.author} | channel={getattr(ctx.channel,'id',None)} | command={getattr(ctx.command,'name',None)} | message={ctx.message.content}"
            )
        elif isinstance(error, commands.CommandNotFound):
            # ignore to reduce spam, but log debug
            logger.debug(
                f"CommandNotFound: {ctx.message.content} by {ctx.author} in {getattr(ctx.guild,'id',None)}"
            )
        else:
            # generic error
            logger.exception(
                f"Unhandled command error: user={ctx.author} command={getattr(ctx.command,'name',None)} msg={ctx.message.content}"
            )
            try:
                await ctx.send(error_message())
            except Exception as e:
                logger.warning(f"Failed to send error_message to user: {e}")
    except Exception:
        # if handling error itself fails, make sure we log it
        logger.exception("Exception in on_command_error")


@bot.event
async def on_command(ctx):
    """
    Triggered before a command is invoked.
    We log command usage here and optionally notify the log channel.
    """
    try:
        cmd_name = getattr(ctx.command, "name", None)
        author = f"{ctx.author} ({ctx.author.id})"
        guild = (
            f"{getattr(ctx.guild, 'name', None)} ({getattr(ctx.guild, 'id', None)})"
            if ctx.guild
            else "DM"
        )
        channel = (
            f"{getattr(ctx.channel, 'name', None)} ({getattr(ctx.channel, 'id', None)})"
        )
        content = ctx.message.content
        # build a neat log line
        log_line = f"CMD | {cmd_name} | user={author} | guild={guild} | channel={channel} | content={content}"
        logger.info(log_line)
        # also optionally send a concise notification to log channel:
        summary_title = f"Command: {cmd_name}"
        summary_body = (
            f"User: {author}\nServer: {guild}\nChannel: {channel}\nMessage: {content}"
        )
        # run send in background but await so discord rate-limit handled (we keep it non-blocking minimal)
        await maybe_send_log_channel(summary_title, summary_body)
    except Exception:
        logger.exception("Exception in on_command")


# ---------- Commands (unchanged logic, but using logger) ----------
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
        except Exception as e:
            logger.exception(f"Exception in ppc command: {e}")
            await ctx.send(error_message())


@bot.command()
async def predppc(ctx, type):
    try:
        await ctx.send(
            embed=Embed(
                title="**This command is deprecated**", color=discord.Color.red()
            )
        )
    except Exception as e:
        logger.exception(f"Exception in predppc command: {e}")
        await ctx.send(
            embed=Embed(
                title="**This command is deprecated**", color=discord.Color.red()
            )
        )


@bot.command()
async def wz(ctx, server):
    if await server_permission(ctx):
        try:
            current_wz = warzone_service.get_wz_map(server)
            print(current_wz)
            embed = wz_embed(f"**Current Warzone on {server} server!**", current_wz)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.exception(f"Exception in wz command: {e}")
            await ctx.send(error_message())


@bot.command()
async def predwz(ctx):
    try:
        await ctx.send(
            embed=Embed(
                title="**This command is deprecated**", color=discord.Color.red()
            )
        )
    except Exception as e:
        logger.exception(f"Exception in predwz command: {e}")
        await ctx.send(
            embed=Embed(
                title="**This command is deprecated**", color=discord.Color.red()
            )
        )


@bot.command()
async def ulttotal(ctx, knight: int, chaos: int, hell: int):
    if await server_permission(ctx):
        try:
            if knight > 60 or chaos > 60 or hell > 60:
                await ctx.send("Timer must >60s")
                return
            else:
                total_score = ppc_service.get_total_score(
                    knight, chaos, hell, "ultimate"
                )
                embed = Embed(
                    title=f"Total score: ",
                    description=f"**{total_score}**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
        except Exception as e:
            logger.exception(f"Exception in ulttotal command: {e}")
            await ctx.send(
                "Command must contain knight, chaos, and hell time. ex: `!ulttotal 8 9 10`, means 8 knight, 9 chaos, 10 hell"
            )


@bot.command()
async def ult(ctx, difficulty, time: int):
    if await server_permission(ctx):
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
        except Exception as e:
            logger.exception(f"Exception in ult command: {e}")
            await ctx.send(error_message())


@bot.command()
async def advtotal(ctx, knight: int, chaos: int, hell: int):
    if await server_permission(ctx):
        try:
            if knight > 60 or chaos > 60 or hell > 60:
                await ctx.send("Timer must >60s")
                return
            else:
                total_score = ppc_service.get_total_score(
                    knight, chaos, hell, "advanced"
                )
                embed = Embed(
                    title=f"Total score: ",
                    description=f"**{total_score}**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
        except Exception as e:
            logger.exception(f"Exception in advtotal command: {e}")
            await ctx.send(
                "Command must contain knight, chaos, and hell time. ex: `!advtotal 8 9 10`, means 8 knight, 9 chaos, 10 hell"
            )


@bot.command()
async def adv(ctx, difficulty, time: int):
    if await server_permission(ctx):
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
        except Exception as e:
            logger.exception(f"Exception in adv command: {e}")
            await ctx.send(error_message())


@bot.command()
async def boss(ctx, name):
    if await server_permission(ctx):
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
                    color=discord.Color.red(),
                )
                embed.set_image(
                    url="https://assets.huaxu.app/browse/glb/image/uifubenchallengemapboss/bosssingleimghard.png"
                )
                await ctx.send(embed=embed)
                return
            else:
                boss_data = ppc_service.get_boss_stat(name)
                if boss_data == None:
                    await ctx.send(
                        "Boss data not found, please use command `!boss list` to see list of bosses"
                    )
                    return
                else:
                    print(boss_data["name"])
                    embed = ppc_boss_stat_embed(boss_data)
                    await ctx.send(embed=embed)
                    return
        except Exception as e:
            logger.exception(f"Exception in boss command: {e}")
            await ctx.send(error_message())


# ---------- Run ----------
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.exception(f"Bot crashed on run: {e}")
