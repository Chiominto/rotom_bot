import discord

from constants.celestial_constants import *
from utils.cache.cache_list import (
    processed_caught_messages,
    research_fossil_alert_cache,
)
from utils.cache.utilities_cache import fetch_user_utility_type_setting_cache
from utils.db.research_fossil_alert_db_func import (
    upsert_user_research_fossil_alert_via_user_id,
)
from utils.db.utilities_db import upsert_utility_setting
from utils.functions.get_pokemeow_reply import get_pokemeow_reply
from utils.logs.pretty_log import pretty_log

from .faction_ball_alert import extract_member_username_from_embed, get_user_id_by_name


def phone_copy_description(text: str, setting: str):
    if setting == "iphone":
        new_text = f"`{text}`"  # Wrap in code block for iPhone formatting
    elif setting == "android":
        new_text = f"{text}"  # Plain text for Android
    else:
        new_text = text  # Default to plain text if setting is unrecognized
    return new_text


async def pokemon_caught_listener(
    bot: discord.Client, before_message: discord.Message, message: discord.Message
):
    # Process message embeds
    if not message.embeds:
        return

    embed = message.embeds[0]
    embed_color = embed.color.value if embed.color else None
    embed_description = embed.description or ""

    # Prevent double processing
    if message.id in processed_caught_messages:
        return
    processed_caught_messages.add(message.id)

    member = await get_pokemeow_reply(before_message)
    if not member:
        # Fall back to username extraction from embed
        username = extract_member_username_from_embed(embed)
        if not username:
            pretty_log(
                "info",
                f"Could not extract username from embed or reply for message ID {message.id}",
                label="💠 POKÉMON CAUGHT LISTENER",
                bot=bot,
            )
            return
        user_id = get_user_id_by_name(username)
        if not user_id:
            return
        member = message.guild.get_member(user_id)
        if not member:
            return

    member_id = member.id
    member_name = member.name
    # Plume fossil alert
    if (
        ":plume_fossil" in embed_description
        and member_id in research_fossil_alert_cache
    ):
        phone_setting = (
            fetch_user_utility_type_setting_cache(member_id, "phone") or "iphone"
        )
        user_data = research_fossil_alert_cache[member_id]
        notify = str(user_data.get("notify", "off")).lower()  # ✅ CORRECT!

        if notify == "on" or notify == "on_no_pings":
            command_text = ";res ex plume_fossil"
            command_text = phone_copy_description(command_text, phone_setting)
            if notify == "on":
                # Send ping alert
                content = f"{member.mention}, Oh a plume fossil! Don't forget to do the command"
            elif notify == "on_no_pings":
                # Send non-ping alert
                content = f"**{member.name}**, Oh a plume fossil! Don't forget to do the command"

            embed_msg = discord.Embed(
                description=command_text, color=DEFAULT_EMBED_COLOR
            )
            await message.channel.send(
                content=content,
                embed=embed_msg,
            )
            pretty_log(
                "info",
                f"Sent Plume Fossil alert to {member_name} ({member_id})",
                label="🦴 RESEARCH FOSSILS ALERT",
                bot=bot,
            )
            # Upsert phone setting to db if there is no entry yet and set it to iphone by default
            if fetch_user_utility_type_setting_cache(member_id, "phone") is None:
                await upsert_utility_setting(
                    bot, member_id, member_name, "phone", "iphone"
                )
                pretty_log(
                    "info",
                    f"Upserted default phone setting for {member_name} ({member_id}) in Research Fossil Alert flow",
                    label="🦴 RESEARCH FOSSILS ALERT",
                    bot=bot,
                )
            # Upsert research fossil alert setting to db if there is no entry yet and set it to on_no_pings by default
            if (
                fetch_user_utility_type_setting_cache(
                    member_id, "research_fossil_alert"
                )
                is None
            ):
                await upsert_user_research_fossil_alert_via_user_id(
                    bot, member_id, member_name, "on_no_pings"
                )
                pretty_log(
                    "info",
                    f"Upserted default research fossil alert setting for {member_name} ({member_id}) in Research Fossil Alert flow",
                    label="🦴 RESEARCH FOSSILS ALERT",
                    bot=bot,
                )
