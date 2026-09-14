import re

import discord

from utils.db.faction_db import upsert_new_name
from utils.functions.get_pokemeow_reply import get_pokemeow_reply
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log


def extract_username(message: str) -> str | None:
    """
    Extracts the username from a message like:
    'You spent <:PokeCoin:666879070650236928> **100,000** to change your username to **cici.the.dictator**!'
    Returns the username string, or None if not found.
    """
    match = re.search(r"username to \*\*(.*?)\*\*", message, re.IGNORECASE)
    return match.group(1) if match else None

async def handle_username_change(bot: discord.Client, message:discord.Message):
    # Handle a username change by updating faction username in database

    # Extract member ID first
    member = await get_pokemeow_reply(message)
    if not member:
        pretty_log(
            "warning",
            f"Could not identify the user for username change message ID {message.id}",
            bot=bot,
        )
        return

    user_id = member.id
    new_user_name = extract_username(message.content)
    if not new_user_name:
        pretty_log(
            "warning",
            f"Could not extract the new username from message ID {message.id}",
            bot=bot,
        )
        return

    return await upsert_new_name(bot, user_id, new_user_name)
