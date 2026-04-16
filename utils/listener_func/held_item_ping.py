import re

import discord
from discord.ext import commands

from constants.held_items import held_item_message
from utils.logs.pretty_log import pretty_log


async def held_item_ping_handler(bot: commands.Bot, message: discord.Message):
    """
    Scan message embeds for Pokemon spawns.
    Logs all Pokemon, but only pings if spawn has a held item AND user is subscribed.
    """
    from utils.cache.item_alert_cache import fetch_user_item_alert_cache

    """pretty_log(
        "info", f"Processing message {message.id}", label="🐭 HELD ITEM PING", bot=bot
    )"""

    if not message.reference or not message.reference.resolved:
        """pretty_log(
            "skip",
            "Skipped: not a reply or replied msg not cached",
            label="🐭 HELD ITEM PING",
            bot=bot,
        )"""
        return

    target_user = message.reference.resolved.author
    if not target_user:
        """pretty_log(
            "skip", "Skipped: reply has no author", label="🐭 HELD ITEM PING", bot=bot
        )"""
        return
    # Get user subscription from cache
    user_item_alert = fetch_user_item_alert_cache(target_user.id)
    # Return of None or "off"
    if not user_item_alert or user_item_alert.get("notify") == "off":
        """pretty_log(
            "skip",
            f"User {target_user.id} has no item alert or notifications turned off",
            label="🐭 HELD ITEM PING",
            bot=bot,
        )"""
        return


    if not message.embeds:
        """pretty_log(
            "skip", "Skipped: message has no embeds", label="🐭 HELD ITEM PING", bot=bot
        )"""
        return

    for embed in message.embeds:
        desc = embed.description or ""

        """pretty_log(
            "debug",
            f"Embed description raw: {repr(desc)}",
            label="🐭 HELD ITEM PING",
            bot=bot,
        )"""

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

            # Log every Pokemon
            """pretty_log(
                "info",
                f"Detected Pokemon: {pokemon_name}, Held item? {has_held_item}",
                label="🐭 HELD ITEM PING",
                bot=bot,
            )"""

            # Only ping if the spawn actually has a held item
            if not has_held_item:
                continue

            msg = held_item_message(pokemon_name)
            if not msg:
                """pretty_log(
                    "skip",
                    f"User {target_user.id} not subscribed for {pokemon_name}'s items",
                    label="🐭 HELD ITEM PING",
                    bot=bot,
                )"""
                continue

            try:
                mention_str = f"<@{target_user.id}>"
                if user_item_alert == "on_no_pings":
                    mention_str = f"**{target_user.name}**"
                await message.channel.send(f"{mention_str} {msg}")
                pretty_log(
                    "info",
                    f"Pinged {target_user.id} for {pokemon_name}",
                    label="🐭 HELD ITEM PING",
                    bot=bot,
                )
            except Exception as e:
                pretty_log(
                    "error",
                    f"Failed to ping {target_user.id} for {pokemon_name}: {e}",
                    label="🐭 HELD ITEM PING",
                    bot=bot,
                )
