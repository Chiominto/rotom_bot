import re

import discord
from discord.ext import commands

from constants.held_items import held_item_message
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.functions.get_pokemeow_reply import get_pokemeow_reply
from .faction_ball_alert import extract_member_username_from_embed, get_user_id_by_name

enable_debug(f"{__name__}.held_item_ping_handler")


async def held_item_ping_handler(bot: commands.Bot, message: discord.Message):
    """
    Scan message embeds for Pokemon spawns.
    Logs all Pokemon, but only pings if spawn has a held item AND user is subscribed.
    """
    from utils.cache.item_alert_cache import fetch_user_item_alert_cache

    target_user = await get_pokemeow_reply(message)
    if not target_user:
        # Fallback try to extract username from embed author if possible
        trainer_name = re.search(r"\*\*(.+?)\*\* found a wild", message.content)
        if not trainer_name:
            debug_log("No username match found in message content.")
            return
        
        # If we got a trainer name from the embed, we can try to find the user ID from the name
        target_user_id = get_user_id_by_name(trainer_name)
        if not target_user_id:
            debug_log(
                f"Skipped: could not find user ID for trainer name '{trainer_name}' extracted from embed author"
            )
            return
        target_user = await bot.fetch_user(target_user_id)
        if not target_user:
            debug_log(
                f"Skipped: could not fetch user with ID {target_user_id} extracted from embed author"
            )
            return

    # Get user subscription from cache
    user_item_alert = fetch_user_item_alert_cache(target_user.id)
    # Return of None or "off"
    if not user_item_alert or user_item_alert.get("notify") == "off":
        debug_log(
            f"User {target_user.id} has no item alert or notifications turned off"
        )
        return

    debug_log(f"User item alert settings: {user_item_alert}")

    if not message.embeds:
        debug_log("Skipped: message has no embeds")
        return

    for embed in message.embeds:
        desc = embed.description or ""
        debug_log(f"Embed description raw: {repr(desc)}")

        # Regex: extract optional held item and Pokemon name
        pattern = (
            r"(?:<:[^:]+:\d+>\s*)?"  # optional leading NPC emoji
            r"\*\*.+?\*\*\s*found a wild\s*"
            r"(?P<teamlogo><:team_logo:\d+>)?\s*"  # optional team logo emoji
            r"(?P<held><:held_item:\d+>)?\s*"  # optional held item emoji
            r"(?:<:[^:]+:\d+>\s*)+"  # Pokemon emoji (+ optional dexCaught)
            r"\*\*(?P<pokemon>[A-Za-z_-]+)\*\*"  # pokemon name (allow hyphens)
        )
        matches = re.finditer(pattern, desc)

        for match in matches:
            pokemon_name = match.group("pokemon").lower()
            has_held_item = bool(match.group("held"))
            debug_log(f"Detected Pokemon: {pokemon_name}, Held item? {has_held_item}")

            # Only ping if the spawn actually has a held item
            if not has_held_item:
                continue

            msg = held_item_message(pokemon_name)
            if not msg:
                debug_log(
                    f"No held item message configured for {pokemon_name}, skipping"
                )
                continue

            try:
                mention_str = f"<@{target_user.id}>"
                if user_item_alert == "on_no_pings":
                    mention_str = f"**{target_user.name}**"
                await message.channel.send(f"{mention_str} {msg}")
                debug_log(f"Sent held item ping to {target_user.id} for {pokemon_name}")
                pretty_log(
                    "info",
                    f"Pinged {target_user.id} for {pokemon_name}",
                    label="🐭 HELD ITEM PING",
                    bot=bot,
                )
            except Exception as e:
                debug_log(
                    f"Failed to send held item ping to {target_user.id} for {pokemon_name}: {e}"
                )
                pretty_log(
                    "error",
                    f"Failed to ping {target_user.id} for {pokemon_name}: {e}",
                    label="🐭 HELD ITEM PING",
                    bot=bot,
                )
