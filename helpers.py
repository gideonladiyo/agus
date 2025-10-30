"""Helper functions for Discord bot commands."""
import discord
from discord import Embed
from logger import setup_logger

logger = setup_logger(__name__)


async def send_score_embed(ctx, title: str, score, color=discord.Color.red()):
    """Send a score embed to the Discord channel."""
    try:
        embed = Embed(
            title=title,
            description=f"**{score}**",
            color=color,
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Failed to send score embed: {e}", exc_info=True)
        raise


async def handle_command_error(ctx, error: Exception, command_name: str):
    """Handle command errors with proper logging and user feedback."""
    from utils import error_message

    logger.error(f"Error in command '{command_name}': {error}", exc_info=True)

    # Provide more specific error messages when possible
    error_msg = str(error)
    if "not found" in error_msg.lower():
        await ctx.send(f"❌ {error_msg}")
    elif "empty" in error_msg.lower():
        await ctx.send("❌ No data available. Please try again later.")
    else:
        await ctx.send(error_message())
