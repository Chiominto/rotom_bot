import re

import discord

from constants.aesthetics import Thumbnails
from constants.celestial_constants import (
    CELESTIAL_ROLES,
    CELESTIAL_TEXT_CHANNELS,
    DEFAULT_EMBED_COLOR,
    MONTHLY_REQUIREMENT,
    WEEKLY_REQUIREMENT,
)
from utils.cache.cache_list import (
    processed_caught_messages,
    research_fossil_alert_cache,
)
from utils.cache.utilities_cache import fetch_user_utility_type_setting_cache
from utils.db.celestial_members_db import update_pokemeow_name
from utils.db.monthly_goal_tracker import upsert_monthly_goal
from utils.db.research_fossil_alert_db_func import (
    upsert_user_research_fossil_alert_via_user_id,
)
from utils.db.utilities_db import upsert_utility_setting
from utils.db.weekly_goal_tracker import upsert_weekly_goal
from utils.functions.get_pokemeow_reply import get_pokemeow_reply
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

from .faction_ball_alert import extract_member_username_from_embed, get_user_id_by_name

"""enable_debug(f"{__name__}.pokemon_caught_goal_processer")
enable_debug(f"{__name__}.pokemon_caught_listener")
enable_debug(f"{__name__}.goal_checker")"""
FISHING_COLOR = 0x87CEFA


async def goal_checker(
    bot: discord.Client,
    user_id: int,
    user_name: str,
    guild: discord.Guild,
    channel: discord.TextChannel,
    top_line_weekly_catches: int = None,
    top_line_monthly_catches: int = None,
    context: str = None,
):
    # return  # Temporarily disable goal checking
    from utils.cache.cache_list import monthly_goal_cache, weekly_goal_cache
    from utils.cache.monthly_goal_tracker_cache import update_monthly_requirement_mark
    from utils.cache.weekly_goal_tracker_cache import update_weekly_requirement_mark

    # Get current caught counts
    weekly_pokemon_caught = weekly_goal_cache.get(user_id, {}).get("pokemon_caught", 0)
    monthly_pokemon_caught = monthly_goal_cache.get(user_id, {}).get(
        "pokemon_caught", 0
    )
    weekly_fish_caught = weekly_goal_cache.get(user_id, {}).get("fish_caught", 0)
    monthly_fish_caught = monthly_goal_cache.get(user_id, {}).get("fish_caught", 0)
    weekly_requirement_mark = weekly_goal_cache.get(user_id, {}).get(
        "weekly_requirement_mark", False
    )
    monthly_requirement_mark = monthly_goal_cache.get(user_id, {}).get(
        "monthly_requirement_mark", False
    )

    # Compute total
    total_weekly_caught = weekly_pokemon_caught + weekly_fish_caught
    total_monthly_caught = monthly_pokemon_caught + monthly_fish_caught

    debug_log(
        f"total_weekly_caught={total_weekly_caught}, total_monthly_caught={total_monthly_caught}"
    )
    goal_tracker_channel = guild.get_channel(CELESTIAL_TEXT_CHANNELS.goal_tracker)
    # Update weekly requirement mark
    if not weekly_requirement_mark:
        if (
            weekly_pokemon_caught >= WEEKLY_REQUIREMENT
            or total_weekly_caught >= WEEKLY_REQUIREMENT
            or weekly_fish_caught >= WEEKLY_REQUIREMENT
        ) or (
            top_line_weekly_catches and top_line_weekly_catches >= WEEKLY_REQUIREMENT
        ):
            if not goal_tracker_channel:
                pretty_log(
                    "warning",
                    f"Weekly goal reached for {user_name} ({user_id}) but goal tracker channel was not found. Keeping weekly_requirement_mark=False to retry.",
                    label="💠 GOAL CHECKER",
                    bot=bot,
                )
            else:
                try:
                    user = guild.get_member(user_id)
                    if not user:
                        # Fetch user via user id
                        user = await bot.fetch_user(user_id)
                    user_line = user.mention if user else user_name
                    avatar_url = user.display_avatar.url if user else None
                    # Add cosmic catch goal role if user has met the requirement and doesn't have the role yet
                    role = guild.get_role(CELESTIAL_ROLES.cosmic_catch_goal)
                    member = guild.get_member(user_id)
                    if member:
                        if role and role not in member.roles:
                            await member.add_roles(role)
                            pretty_log(
                                "info",
                                f"Added Cosmic Catch Goal role to {user_name} ({user_id}) for meeting weekly goal.",
                                label="💠 GOAL CHECKER",
                                bot=bot,
                            )
                    role_str = f"- **Role Reward:** Cosmic Catch Goal" if role else ""
                    desc = (
                        f"- **Member:** {user_line}\n"
                        f"- **Goal:** {WEEKLY_REQUIREMENT:,} catches\n"
                        f"{role_str}"
                    )
                    embed = discord.Embed(
                        title="🎉 Weekly Goal Achieved!",
                        description=desc,
                        color=DEFAULT_EMBED_COLOR,
                    )
                    embed.set_thumbnail(url=Thumbnails.weekly_goal)
                    embed.set_author(name=user.display_name, icon_url=avatar_url)
                    await send_webhook(
                        bot=bot,
                        channel=goal_tracker_channel,
                        embed=embed,
                    )

                    # Mark only after successful goal tracker announcement.
                    update_weekly_requirement_mark(user_id, True)
                    pretty_log(
                        "info", f"User {user_name} has met the weekly requirement."
                    )
                    if not context or context != "stats_command":
                        await channel.send(
                            f"🎉 Congratulations **{user_name}**! You have met the weekly requirement of {WEEKLY_REQUIREMENT:,}"
                        )

                except Exception as e:
                    pretty_log(
                        "error",
                        f"Failed to send weekly goal tracker announcement for {user_name} ({user_id}): {e}. Keeping weekly_requirement_mark=False for retry.",
                        label="💠 GOAL CHECKER",
                        bot=bot,
                    )

    if not monthly_requirement_mark:
        if (
            monthly_pokemon_caught >= MONTHLY_REQUIREMENT
            or total_monthly_caught >= MONTHLY_REQUIREMENT
            or monthly_fish_caught >= MONTHLY_REQUIREMENT
        ) or (
            top_line_monthly_catches and top_line_monthly_catches >= MONTHLY_REQUIREMENT
        ):
            if not goal_tracker_channel:
                pretty_log(
                    "warning",
                    f"Monthly goal reached for {user_name} ({user_id}) but goal tracker channel was not found. Keeping monthly_requirement_mark=False to retry.",
                    label="💠 GOAL CHECKER",
                    bot=bot,
                )
            else:
                try:
                    user = guild.get_member(user_id)

                    if not user:
                        # Fetch user via user id
                        user = await bot.fetch_user(user_id)

                    avatar_url = user.display_avatar.url if user else None
                    user_line = user.mention if user else user_name
                    desc = (
                        f"- **Member:** {user_line}\n"
                        f"- **Goal:** {MONTHLY_REQUIREMENT:,} catches\n"
                    )
                    embed = discord.Embed(
                        title="🏆 Monthly Goal Achieved!",
                        description=desc,
                        color=0xFFD700,
                    )
                    embed.set_thumbnail(url=Thumbnails.monthly_goal)
                    embed.set_author(name=user.display_name, icon_url=avatar_url)
                    await send_webhook(
                        bot=bot,
                        channel=goal_tracker_channel,
                        embed=embed,
                    )

                    update_monthly_requirement_mark(user_id, True)
                    pretty_log(
                        "info", f"User {user_name} has met the monthly requirement."
                    )
                    if not context or context != "stats_command":
                        await channel.send(
                            f"🏆 Congratulations **{user_name}**! You have met the monthly requirement of {MONTHLY_REQUIREMENT:,}"
                        )
                    pretty_log(
                        "info",
                        f"Sent monthly requirement met webhook for user {user_name}.",
                    )
                except Exception as e:
                    pretty_log(
                        "error",
                        f"Failed to send monthly goal tracker announcement for {user_name} ({user_id}): {e}. Keeping monthly_requirement_mark=False for retry.",
                        label="💠 GOAL CHECKER",
                        bot=bot,
                    )


def extract_member_username_from_embed(embed: discord.Embed) -> str | None:
    """
    Extracts the username from the embed author name, e.g. "Congratulations, frayl!" -> "frayl".
    Returns None if not found.
    """
    if embed.author and embed.author.name:
        # Try 'Congratulations, username!' first
        match = re.search(r"Congratulations, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
        # Fallback: 'Well done, username!'
        match = re.search(r"Well done, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
        # Fallback: 'Great work, username!'
        match = re.search(r"Great work, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
    return None


async def check_pokemeow_name(bot, member: discord.Member, pokemeow_name: str):
    """Check if the PokéMeow name matches the cached name for the member ID., if not updates it"""
    from utils.cache.cache_list import celestial_members_cache

    member_id = member.id
    clan_member_info = celestial_members_cache.get(member_id)
    if not clan_member_info:
        debug_log(f"No Clan member info found in cache for member ID {member_id}.")
        return

    cached_pokemeow_name = clan_member_info.get("pokemeow_name")
    if cached_pokemeow_name != pokemeow_name:
        debug_log(
            f"PokéMeow name mismatch for member ID {member_id}: cached='{cached_pokemeow_name}', new='{pokemeow_name}'. Updating cache."
        )
        await update_pokemeow_name(bot, member.id, pokemeow_name)
        log_channel = member.guild.get_channel(CELESTIAL_TEXT_CHANNELS.server_logs)
        embed = discord.Embed(
            title="PokéMeow Name Updated",
            description=(
                f"**Member:** <@{member_id}>\n"
                f"**Old PokéMeow Name:** {cached_pokemeow_name}\n"
                f"**New PokéMeow Name:** {pokemeow_name}"
            ),
            color=0x00FF00,
        )
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Member ID: {member_id}", icon_url=member.guild.icon.url)
        if log_channel:
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=embed,
            )


# Pokemon Caught Listener
async def pokemon_caught_goal_processer(
    bot: discord.Client,
    before_message: discord.Message,
    after_message: discord.Message,
):
    from utils.cache.celestial_members_cache import (
        celestial_members_cache,
        fetch_user_id_by_user_name_or_pokemeow_name_cache,
    )

    if not after_message.embeds:
        debug_log("No embeds found in after_message.")
        return
    embed = after_message.embeds[0]
    guild = after_message.guild
    member = await get_pokemeow_reply(before_message)
    debug_log(f"Pokémon caught listener - initial member: {member}")
    if not member:
        # Try to extract username from embed author
        username = extract_member_username_from_embed(embed)
        debug_log(f"Extracted username from embed: {username}")
        if not username:
            pretty_log(
                "info",
                "⚠️ Could not determine user from Pokémon caught message embed.",
            )
            return
        user_id = fetch_user_id_by_user_name_or_pokemeow_name_cache(username)
        debug_log(f"Fetched user_id from username: {user_id}")
        if not user_id:
            pretty_log(
                "info",
                f"⚠️ Could not find Clan member for username '{username}' from Pokémon caught message embed.",
            )
            # Try searching username in guild members as a last resort
            member = guild.get_member_named(username)
            user_id = member.id if member else None

        member = after_message.guild.get_member(user_id) if user_id else None
        debug_log(f"Fetched member from guild: {member}")
        if not member:
            pretty_log(
                "info",
                f"⚠️ Could not find Discord member for Clan member ID '{user_id}' from Pokémon caught message embed.",
            )
            return

    member_id = member.id
    member_name = member.name
    debug_log(f"member_id={member_id}, member_name={member_name}")

    # Add member to Weekly Goal Tracker and Monthly Goal Tracker caches if not present
    from utils.cache.cache_list import (
        celestial_members_cache,
        monthly_goal_cache,
        weekly_goal_cache,
    )
    from utils.cache.monthly_goal_tracker_cache import (
        increment_monthly_fish_caught,
        mark_monthly_goal_dirty,
        set_monthly_pokemon_caught,
        upsert_monthly_goal_cache,
    )
    from utils.cache.weekly_goal_tracker_cache import (
        increment_fish_caught,
        mark_weekly_goal_dirty,
        set_pokemon_caught,
        upsert_weekly_goal_cache,
    )

    clan_member_info = celestial_members_cache.get(member_id)
    debug_log(f"clan_member_info={clan_member_info}")
    if not clan_member_info:
        pretty_log(
            "info",
            f"⚠️ Clan member info not found in cache for member ID {member_id} ({member_name}).",
        )
        return

    personal_channel_id = (
        clan_member_info.get("channel_id") if clan_member_info else None
    )
    debug_log(f"personal_channel_id={personal_channel_id}")

    if member_id not in weekly_goal_cache:
        debug_log(f"member_id {member_id} not in weekly_goal_cache, upserting...")
        try:
            await upsert_weekly_goal(
                bot,
                member_id,
                member_name,
                personal_channel_id,
                pokemon_caught=0,
                fish_caught=0,
                battles_won=0,
                weekly_requirement_mark=False,
            )
            pretty_log(
                "info",
                f"Upserted weekly goal for member ID {member_id} ({member_name}).",
            )
        except Exception as e:
            pretty_log(
                "error",
                f"❌ Exception while upserting weekly goal for member ID {member_id}: {e}",
            )
            return

    if member_id not in monthly_goal_cache:
        debug_log(f"member_id {member_id} not in monthly_goal_cache, upserting...")
        await upsert_monthly_goal(
            bot,
            member_id,
            member_name,
            personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            monthly_requirement_mark=False,
        )

    embed_color = embed.color.value if embed.color else None
    embed_description = embed.description or ""
    debug_log(f"embed_color={embed_color}, embed_description={embed_description}")

    # Fish catch
    if embed_color == FISHING_COLOR:
        debug_log(f"Detected fish catch for member_id {member_id}")
        increment_fish_caught(member)
        increment_monthly_fish_caught(member)
        mark_monthly_goal_dirty(member_id)
        mark_weekly_goal_dirty(member_id)

    else:
        current_weekly_caught = weekly_goal_cache[member_id].get("pokemon_caught", 0)
        current_monthly_caught = monthly_goal_cache[member_id].get("pokemon_caught", 0)
        new_weekly_caught = current_weekly_caught + 1
        new_monthly_caught = current_monthly_caught + 1
        debug_log(
            f"Incrementing caught counts: weekly {new_weekly_caught}, monthly {new_monthly_caught}"
        )
        set_pokemon_caught(member, new_weekly_caught)
        set_monthly_pokemon_caught(member, new_monthly_caught)
        mark_weekly_goal_dirty(member_id)
        mark_monthly_goal_dirty(member_id)

    # Check for goal completion
    await goal_checker(
        bot=bot,
        user_id=member_id,
        user_name=member_name,
        guild=after_message.guild,
        channel=after_message.channel,
    )
    # Check and update PokéMeow name if needed
    pokemeow_name = clan_member_info.get("pokemeow_name")
    if pokemeow_name:
        await check_pokemeow_name(bot, member, pokemeow_name)


def phone_copy_description(text: str, setting: str = None, member_id: int = None):
    if setting is None:
        if member_id is not None:
            setting = (
                fetch_user_utility_type_setting_cache(member_id, "phone") or "iphone"
            )
        else:
            setting = "iphone"
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
        ":jaw_fossil" in embed_description
        and member_id in research_fossil_alert_cache
    ):
        phone_setting = (
            fetch_user_utility_type_setting_cache(member_id, "phone") or "iphone"
        )
        user_data = research_fossil_alert_cache[member_id]
        notify = str(user_data.get("notify", "off")).lower()  # ✅ CORRECT!

        if notify == "on" or notify == "on_no_pings":
            command_text = ";res ex jaw_fossil"
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
    # Process goal checking for Pokémon caught
    try:
        await pokemon_caught_goal_processer(
            bot=bot,
            before_message=before_message,
            after_message=message,
        )
    except Exception as e:
        pretty_log(
            "error",
            f"Exception in pokemon_caught_goal_processer: {e}",
            label="💠 POKÉMON CAUGHT LISTENER",
            bot=bot,
        )
