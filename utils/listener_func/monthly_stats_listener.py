import re

import discord

from constants.celestial_constants import (
    CELESTIAL_TEXT_CHANNELS,
    DEFAULT_EMBED_COLOR,
    MONTHLY_REQUIREMENT,
    WEEKLY_REQUIREMENT,
)
from utils.cache.cache_list import (
    celestial_members_cache,
    monthly_goal_cache,
    processed_monthly_stats_messages,
)
from utils.db.monthly_goal_tracker import upsert_monthly_goal
from utils.db.weekly_goal_tracker import upsert_weekly_goal
from utils.functions.get_pokemeow_reply import (
    get_message_interaction_member,
    get_pokemeow_reply,
)
from utils.functions.stats_parsers import parse_clan_stats_message
from utils.logs.pretty_log import pretty_log

from .pokemon_caught_listener import goal_checker
from .weekly_stats_listener import extract_current_page_number


async def monthly_stats_listener(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):
    embed = after_message.embeds[0] if after_message.embeds else None
    if not embed:
        return
    embed_footer = embed.footer.text
    embed_description = embed.description or ""

    # Get command user
    command_user: discord.Member = await get_pokemeow_reply(before_message)
    if not command_user:
        # Fallback to interaction user
        command_user = get_message_interaction_member(before_message)
        if not command_user:
            return

    command_user_id = command_user.id
    command_user_name = command_user.name
    guild = after_message.guild

    # Extract current page number
    current_page = extract_current_page_number(embed_footer)
    # Check if current page and message id is in processed messages
    key = (after_message.id, current_page)
    if key in processed_monthly_stats_messages:
        return
    processed_monthly_stats_messages.add(key)

    # Check if command user is in monthly and weekly goal caches
    from utils.cache.cache_list import (
        celestial_members_cache,
        monthly_goal_cache,
        weekly_goal_cache,
    )

    clan_member_info = celestial_members_cache.get(command_user_id)
    personal_channel_id = (
        clan_member_info.get("channel_id") if clan_member_info else None
    )
    if command_user_id not in weekly_goal_cache:

        await upsert_weekly_goal(
            bot=bot,
            user_id=command_user_id,
            user_name=command_user_name,
            channel_id=personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            weekly_requirement_mark=False,
        )
    if command_user_id not in monthly_goal_cache:
        await upsert_monthly_goal(
            bot=bot,
            user_id=command_user_id,
            user_name=command_user_name,
            channel_id=personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            monthly_requirement_mark=False,
        )

    top_line_catches = 0
    # Get top line catches
    user_top_line_match = re.search(
        r"You're Rank \d+ in your clan's monthly stats — with ([\d,]+) catches!",
        embed_description,
    )
    top_line_catches = 0
    if user_top_line_match:
        top_line_catches = int(user_top_line_match.group(1).replace(",", ""))
        pretty_log(
            "info",
            f"Top line catches for {command_user_name}: {top_line_catches}",
            label="💠 MONTHLY STATS DEBUG",
            bot=bot,
        )
        # Goal checking
        if top_line_catches >= MONTHLY_REQUIREMENT and current_page == 1:
            await goal_checker(
                bot=bot,
                user_id=command_user_id,
                user_name=command_user_name,
                channel=after_message.channel,
                top_line_monthly_catches=top_line_catches,
                context="stats_command",
                guild=guild,
            )
            pretty_log(
                "info",
                f"Monthly stats listener: User {command_user_name} ({command_user_id}) has {top_line_catches} weekly catches.",
            )

    # Parse clan members stats
    clan_members_stats = parse_clan_stats_message(embed_description)
    if not clan_members_stats:
        return

    # Resolve member IDs from parsed stats names
    from utils.cache.celestial_members_cache import (
        fetch_user_id_by_user_name_or_pokemeow_name_cache,
    )

    upserts_count = 0
    goal_checks_count = 0
    for username, catches, fishes in clan_members_stats:
        # Manually set member_id for this user before anything else
        if username == "neverlikenever_42984":
            member_id = 1327864338018730044
        else:
            member_id = fetch_user_id_by_user_name_or_pokemeow_name_cache(username)
        if member_id is None:
            pretty_log(
                "info",
                f"[MONTHLY STATS] Skipping upsert: Could not resolve user_id for username '{username}'",
                label="💥 MONTHLY STATS USER_ID NULL",
                bot=bot,
            )
            continue

        member_info = celestial_members_cache.get(member_id)
        channel_id = member_info.get("channel_id") if member_info else None
        # Keep mark state so already-announced users don't get duplicate posts.
        existing_mark = monthly_goal_cache.get(member_id, {}).get(
            "monthly_requirement_mark", False
        )
        await upsert_monthly_goal(
            bot=bot,
            user_id=member_id,
            user_name=username,
            channel_id=channel_id,
            pokemon_caught=catches,
            fish_caught=fishes,
            battles_won=0,
            monthly_requirement_mark=existing_mark,
        )
        upserts_count += 1

        # Run goal checks for anyone meeting the monthly threshold on this page.
        total_catches = catches + fishes
        if (
            catches >= MONTHLY_REQUIREMENT
            or fishes >= MONTHLY_REQUIREMENT
            or total_catches >= MONTHLY_REQUIREMENT
        ):
            await goal_checker(
                bot=bot,
                user_id=member_id,
                user_name=username,
                channel=after_message.channel,
                context="stats_command",
                guild=guild,
            )
            goal_checks_count += 1

    pretty_log(
        "info",
        f"Monthly stats processed page {current_page}: upserts={upserts_count}, goal_checks={goal_checks_count}.",
        label="💠 MONTHLY STATS DEBUG",
        bot=bot,
    )
