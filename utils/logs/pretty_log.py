import traceback
from datetime import datetime

import discord
from discord.ext import commands

CC_ERROR_LOGS_CHANNEL_ID = 1444997181244444672
# -------------------- 🧩 Global Bot Reference --------------------
from typing import Optional

BOT_INSTANCE: Optional[commands.Bot] = None


def set_bot(bot: commands.Bot):
    """Set the global bot instance for automatic logging."""
    global BOT_INSTANCE
    BOT_INSTANCE = bot


# -------------------- ⚡ Rotom Log Tags --------------------
TAGS = {
    "info": "⚡ INFO",
    "db": "🧊 DB",
    "cmd": "🎛️ CMD",
    "ready": "🔌 READY",
    "error": "🔥 ERROR",
    "warn": "🌩️ WARN",
    "critical": "🚨 CRITICAL",
    "skip": "📵 SKIP",
    "sent": "📡 SENT",
    "debug": "👻 DEBUG",
    "success": "✨ SUCCESS",
    "cache": "💾 CACHE",
    "schedule": "⏱️ SCHEDULE",
}

# -------------------- 🎨 Rotom ANSI Colors --------------------
COLOR_ROTOM_ORANGE = "\033[38;2;255;117;24m"
COLOR_ROTOM_RED = "\033[38;2;230;57;70m"
COLOR_ROTOM_YELLOW = "\033[38;2;255;214;10m"
COLOR_ROTOM_WHITE = "\033[38;2;255;244;214m"
COLOR_RESET = "\033[0m"

DEFAULT_LOG_COLOR = COLOR_ROTOM_ORANGE
TAG_COLORS = {
    "warn": COLOR_ROTOM_YELLOW,
    "error": COLOR_ROTOM_RED,
    "critical": COLOR_ROTOM_RED,
}

# -------------------- ⚠️ Critical Logs Channel --------------------
CRITICAL_LOG_CHANNEL_ID = 1444997181244444672  # CC Error Logs
CRITICAL_LOG_CHANNEL_LIST = [
    1410202143570530375,  # Ghouldengo Bot Logs
    CC_ERROR_LOGS_CHANNEL_ID,
    1375702774771093697,
]


# -------------------- 🌟 Pretty Log --------------------
def pretty_log(
    tag: str = "info",
    message: str = "",
    *,
    label: str = None,
    bot: commands.Bot = None,
    include_trace: bool = True,
):
    """
    Prints a colored log for Rotom-themed bots with timestamp and emoji.
    Sends critical/error/warn messages to Discord if bot is set.
    """
    prefix = TAGS.get(tag) if tag else ""
    prefix_part = f"[{prefix}] " if prefix else ""
    label_str = f"[{label}] " if label else ""

    color = TAG_COLORS.get(tag, DEFAULT_LOG_COLOR)

    now = datetime.now().strftime("%H:%M:%S")
    log_message = f"{color}[{now}] {prefix_part}{label_str}{message}{COLOR_RESET}"
    print(log_message)

    # Optionally print traceback
    if include_trace and tag in ("error", "critical"):
        traceback.print_exc()

    # Send to all Discord channels in the list if bot available
    bot_to_use = bot or BOT_INSTANCE
    if bot_to_use and tag in ("critical", "error", "warn"):
        for channel_id in CRITICAL_LOG_CHANNEL_LIST:
            try:
                channel = bot_to_use.get_channel(channel_id)
                if channel:
                    full_message = f"{prefix_part}{label_str}{message}"
                    if include_trace and tag in ("error", "critical"):
                        full_message += f"\n```py\n{traceback.format_exc()}```"
                    if len(full_message) > 2000:
                        full_message = full_message[:1997] + "..."
                    bot_to_use.loop.create_task(channel.send(full_message))
            except Exception:
                print(
                    f"{COLOR_ROTOM_RED}[🔥 ERROR] Failed to send log to Discord channel {channel_id}{COLOR_RESET}"
                )
                traceback.print_exc()


# -------------------- 🌸 UI Error Logger --------------------
def log_ui_error(
    *,
    error: Exception,
    interaction: discord.Interaction = None,
    label: str = "UI",
    bot: commands.Bot = None,
    include_trace: bool = True,
):
    """Logs UI errors with automatic Discord reporting."""
    location_info = ""
    if interaction:
        user = interaction.user
        location_info = f"User: {user} ({user.id}) | Channel: {interaction.channel} ({interaction.channel_id})"

    error_message = f"UI error occurred. {location_info}".strip()
    now = datetime.now().strftime("%H:%M:%S")

    print(
        f"{COLOR_ROTOM_RED}[{now}] [🚨 CRITICAL] {label} error: {error_message}{COLOR_RESET}"
    )
    if include_trace:
        traceback.print_exception(type(error), error, error.__traceback__)

    bot_to_use = bot or BOT_INSTANCE

    pretty_log(
        "error",
        error_message,
        label=label,
        bot=bot_to_use,
        include_trace=include_trace,
    )

    if bot_to_use:
        for channel_id in CRITICAL_LOG_CHANNEL_LIST:
            try:
                channel = bot_to_use.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title=f"⚠️ UI Error Logged [{label}]",
                        description=f"{location_info or '*No interaction data*'}",
                        color=0xFF7518,
                    )
                    if include_trace:
                        trace_text = "".join(
                            traceback.format_exception(
                                type(error), error, error.__traceback__
                            )
                        )
                        if len(trace_text) > 1000:
                            trace_text = trace_text[:1000] + "..."
                        embed.add_field(
                            name="Traceback",
                            value=f"```py\n{trace_text}```",
                            inline=False,
                        )
                    bot_to_use.loop.create_task(channel.send(embed=embed))
            except Exception:
                print(
                    f"{COLOR_ROTOM_RED}[🔥 ERROR] Failed to send UI error to bot channel {channel_id}{COLOR_RESET}"
                )
                traceback.print_exc()
