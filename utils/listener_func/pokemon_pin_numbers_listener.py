import re

import discord

from constants.aesthetics import Emojis
from utils.cache.cache_list import (pin_numbers_alert_cache,
                                    processed_pin_numbers_messages)
from utils.cache.celestial_members_cache import \
    fetch_user_id_by_user_name_or_pokemeow_name_cache
from utils.cache.faction_cache import get_user_id_by_name
from utils.db.pin_numbers_alert_db_func import (fetch_user_pin_numbers_alert,
                                                upsert_user_pin_numbers_alert)
from utils.functions.get_pokemeow_reply import \
    get_pokemeow_reply_or_interaction_member
from utils.functions.retry_function import _retry_discord_call
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

enable_debug(f"{__name__}.pokemon_pin_numbers_listener")


def extract_trainer_name_from_pin_description(description: str) -> str | None:
    """Extracts the bolded trainer name from a 'found/fished a wild' embed description."""
    match = re.search(r"\*\*(.+?)\*\*\s+(?:found|fished) a wild", description)
    if match:
        return match.group(1).strip()
    return None


async def pokemon_pin_numbers_listener(bot:discord.Client, message:discord.Message, pin_number: str, source:str):
    debug_log(
        f"Pin-number listener triggered: message_id={message.id}, "
        f"pin_number={pin_number!r}, channel_id={message.channel.id}"
    )

    if message.id in processed_pin_numbers_messages:
        debug_log(f"Skipping already processed message: {message.id}")
        return
    processed_pin_numbers_messages.add(message.id)
    debug_log(f"Marked message as processed: {message.id}")

    # Get member object
    member = await get_pokemeow_reply_or_interaction_member(message)
    debug_log(f"Resolved pin-number member: {member!r}")
    if not member:
        # Fallback: no reply/interaction available (e.g. prefix command), extract trainer name from embed
        debug_log("No reply or interaction member found; attempting embed fallback")
        description = message.embeds[0].description if message.embeds else None
        trainer_name = (
            extract_trainer_name_from_pin_description(description) if description else None
        )
        debug_log(f"Fallback extracted trainer name: {trainer_name!r}")

        user_id = None
        if trainer_name:
            user_id = get_user_id_by_name(trainer_name)
            if user_id is None:
                user_id = fetch_user_id_by_user_name_or_pokemeow_name_cache(trainer_name)
        debug_log(f"Fallback resolved user_id: {user_id!r}")

        member = message.guild.get_member(user_id) if user_id and message.guild else None
        debug_log(f"Fallback resolved member: {member!r}")

        if not member:
            debug_log("Fallback could not resolve member; returning")
            return

    user_id = member.id
    debug_log(f"Resolved member ID: {user_id}")
    if not user_id:
        debug_log("Resolved member has no user ID; returning")
        return

    # Check if user id is in the pin numbers cache
    user_pin_alert = pin_numbers_alert_cache.get(user_id)
    debug_log(f"Pin alert cache lookup for user {user_id}: {user_pin_alert!r}")

    if not user_pin_alert:
        # Upsert with default on_no_pings
        debug_log(f"No pin alert found for user {user_id}; creating on_no_pings alert")
        await upsert_user_pin_numbers_alert(bot, member, "on_no_pings")
        user_pin_alert = {"notify": "on_no_pings"}
        debug_log(f"Created default pin alert for user {user_id}")

    user_pin_notify = user_pin_alert.get("notify")
    debug_log(f"User pin notify setting: {user_pin_notify}")
    if not user_pin_notify or user_pin_notify.lower() == "off":
        debug_log("User notify setting is off or missing, returning early")
        return
    if source == "pokemon":
        command = ";p"
    elif source == "fish":
        command = ";f"
    elif source == "safari":
        command = ";sz"
    else:
        command = ";p"
    if user_pin_notify.lower() == "on":
        content = f"#️⃣ {member.mention}, your `{command}` pin number is **{pin_number}**"
        debug_log(f"Using mention notification mode for user {user_id}")
    elif user_pin_notify.lower() == "on_no_pings":
        content = f"#️⃣ **{member.name}**, your `{command}` pin number is **{pin_number}**"
        debug_log(f"Using name-only notification mode for user {user_id}")

    else:
        debug_log(f"Unknown user pin notification setting: {user_pin_notify}")
        return

    debug_log(f"Sending pin-number alert from {source} to channel {message.channel.name}")
    await _retry_discord_call(message.channel.send, content=content)
    debug_log(f"Pin-number alert sent successfully for user {user_id}")