import asyncio
import re

import discord
from utils.db.egg_alert_db_func import upsert_user_egg_alert_via_user_id
from utils.cache.egg_alert_cache import fetch_user_egg_alert_cache
from constants.aesthetics import *
from utils.functions.get_pokemeow_reply import (
    get_message_interaction_member,
    get_pokemeow_reply,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

"""enable_debug(f"{__name__}.egg_ready_to_hatch_listener")
enable_debug(f"{__name__}.egg_hatched_listener")"""


def extract_user_id(message: str) -> int | None:
    match = re.search(r"<@(\d+)>", message)
    if match:
        return match.group(1).strip()
    return None


async def egg_ready_to_hatch_listener(bot: discord.Client, message: discord.Message):
    """
    Listens for egg hatching messages and adds a reaction.
    """
    user_id = extract_user_id(message.content)
    debug_log(f"Extracted user ID: {user_id}")
    if not user_id:
        debug_log("No user ID found in the message.")
        return
    try:
        user_id_int = int(user_id)
    except Exception:
        debug_log(f"User ID {user_id} could not be converted to int.")
        return
    user = message.guild.get_member(user_id_int)
    debug_log(f"Fetched user: {user}")
    if not user:
        debug_log(f"User with ID {user_id} not found.")
        return

    # Check if user ID is in the egg alert cache
    notify_type = None
    user_alert = fetch_user_egg_alert_cache(user_id_int)
    debug_log(f"Fetched user alert from cache: {user_alert}")
    if not user_alert:
        # Upsert with default notify method if not found in cache
        debug_log(f"No alert found for user ID {user_id_int}. Upserting with default notify method.")
        notify_type = "on_no_pings"
        await upsert_user_egg_alert_via_user_id(bot=bot, user_id=user_id_int,user_name=user.name, notify=notify_type)
    else:
        notify_type = user_alert.get("notify")
        debug_log(f"User ID {user_id_int} has alert with notify type: {notify_type}")
        if notify_type == "off":
            debug_log(f"User ID {user_id_int} has notifications turned off. Exiting listener.")
            return

    mention_str = f"<@{user_id}>"
    if notify_type == "on_no_pings":
        mention_str = user.name

    content = f"{Emojis.egg_shake} **{mention_str}**,  Use </egg hatch:1015311084594405485> to hatch your egg! "
    await message.channel.send(content)

    pretty_log(
        "info",
        f"Egg hatch listener triggered for user {user_id} in channel {message.channel.id}",
    )


async def egg_hatched_listener(bot: discord.Client, message: discord.Message):
    """
    Listens for egg hatched messages and sends a congratulatory message.
    """
    embed = message.embeds[0] if message.embeds else None
    member = await get_pokemeow_reply(message)
    debug_log(f"Fetched member: {member}")
    if not member:
        debug_log("No member found from the Pokemeow reply.")
        # Use interaction member as fallback
        member = get_message_interaction_member(message)
        debug_log(f"Fetched interaction member: {member}")
        if not member:
            debug_log("No member found from the interaction.")
            return

    member_id = member.id
    try:
        member_id_int = int(member_id)
    except Exception:
        debug_log(f"Member ID {member_id} could not be converted to int.")
        return
    # Check if user ID is in the egg alert cache
    notify_type = None
    user_alert = fetch_user_egg_alert_cache(member_id_int)
    debug_log(f"Fetched user alert from cache: {user_alert}")
    if not user_alert:
        debug_log(f"No alert found for member ID {member_id_int}. Upserting with default notify method.")
        notify_type = "on_no_pings"
        await upsert_user_egg_alert_via_user_id(bot=bot, user_id=member_id_int,user_name=member.name, notify=notify_type)
    else:
        notify_type = user_alert.get("notify")
        debug_log(f"Member ID {member_id_int} has alert with notify type: {notify_type}")
        if notify_type == "off":
            debug_log(f"Member ID {member_id_int} has notifications turned off. Exiting listener.")
            return

    mention_str = f"<@{member_id}>"
    if notify_type == "on_no_pings":
        mention_str = member.name
    # Delay 1 second
    await asyncio.sleep(1)
    content = f"{Emojis.egg} **{mention_str}**,  Use </egg hold:1015311084594405485> to hold another egg!"
    await message.channel.send(content)
    pretty_log(
        "info",
        f"Egg hatched listener triggered for user {member_id} in channel {message.channel.id}",
    )
