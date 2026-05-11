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
    processed_weekly_stats_messages,
)
from utils.db.monthly_goal_tracker import upsert_monthly_goal
from utils.db.weekly_goal_tracker import fetch_all_weekly_goals, upsert_weekly_goal
from utils.functions.get_pokemeow_reply import (
    get_message_interaction_member,
    get_pokemeow_reply,
)
from utils.functions.stats_parsers import (
    parse_clan_stats_message,
    split_known_and_unknown_members,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

from .pokemon_caught_listener import goal_checker

#enable_debug(f"{__name__}.weekly_stats_listener")


def extract_current_page_number(footer_text: str) -> int | None:
    """
    Extracts the current page number from a PokéMeow stats embed footer.
    Returns the page number as an int, or None if not found.
    Example footer: "Page 1/5 • Stat categories: ;clan stats daily/weekly/monthly/yearly"
    """
    match = re.search(r"Page (\d+)", footer_text)
    if match:
        return int(match.group(1))
    return None


async def weekly_stats_listener(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):
    embed = after_message.embeds[0] if after_message.embeds else None
    if not embed:
        debug_log("No embed found in edited message. Exiting weekly_stats_listener.")
        return
    embed_footer = embed.footer.text
    embed_description = embed.description or ""
    debug_log(
        f"Weekly stats embed received: message_id={after_message.id}, footer={embed_footer!r}, description_len={len(embed_description)}"
    )

    # Get command user
    command_user: discord.Member = await get_pokemeow_reply(before_message)
    debug_log(
        f"Extracted command user from PokéMeow reply: {command_user.name if command_user else 'None'}"
    )
    if not command_user:
        # Fallback to interaction user
        debug_log("No command user from reply. Falling back to interaction member.")
        command_user = get_message_interaction_member(before_message)
        if not command_user:
            debug_log("No interaction member found. Exiting weekly_stats_listener.")
            return
    debug_log(f"Resolved command user: {command_user.name} ({command_user.id})")

    command_user_id = command_user.id
    command_user_name = command_user.name
    guild = after_message.guild

    # Extract current page number
    current_page = extract_current_page_number(embed_footer)
    debug_log(f"Extracted current_page={current_page} from footer.")
    # Check if current page and message id is in processed messages
    key = (after_message.id, current_page)
    if key in processed_weekly_stats_messages:
        debug_log(f"Message/page key already processed: {key}. Skipping.")
        return
    processed_weekly_stats_messages.add(key)
    debug_log(f"Queued message/page key as processed: {key}")

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
    debug_log(
        f"Cache check for command user {command_user_id}: in_weekly_cache={command_user_id in weekly_goal_cache}, in_monthly_cache={command_user_id in monthly_goal_cache}, personal_channel_id={personal_channel_id}"
    )
    if command_user_id not in weekly_goal_cache:
        debug_log(
            f"Command user {command_user_id} missing in weekly_goal_cache. Upserting defaults."
        )
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
        debug_log(
            f"Command user {command_user_id} missing in monthly_goal_cache. Upserting defaults."
        )
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
        r"You're Rank \d+ in your clan's weekly stats — with ([\d,]+) catches!",
        embed_description,
    )
    top_line_catches = 0
    if user_top_line_match:
        top_line_catches = int(user_top_line_match.group(1).replace(",", ""))
        debug_log(
            f"Parsed top line catches for {command_user_name}: {top_line_catches} (page={current_page})"
        )
        pretty_log(
            "info",
            f"Top line catches for {command_user_name}: {top_line_catches}",
            label="💠 WEEKLY STATS DEBUG",
            bot=bot,
        )
        # Goal checking
        if top_line_catches >= WEEKLY_REQUIREMENT and current_page == 1:
            await goal_checker(
                bot=bot,
                user_id=command_user_id,
                user_name=command_user_name,
                channel=after_message.channel,
                top_line_weekly_catches=top_line_catches,
                guild=guild,
                context="stats_command",
            )
            pretty_log(
                "info",
                f"Weekly stats listener: User {command_user_name} ({command_user_id}) has {top_line_catches} weekly catches.",
            )
    else:
        debug_log("Could not parse top line catches from embed description.")

    # Parse clan members stats
    clan_members_stats = parse_clan_stats_message(embed_description)
    debug_log(f"Parsed clan member stats entries: {len(clan_members_stats)}")
    if not clan_members_stats:
        debug_log("No clan member stats parsed from embed description. Exiting.")
        return

    # Fetch old weekly goals from DB
    from utils.cache.celestial_members_cache import (
        fetch_user_id_by_user_name_or_pokemeow_name_cache,
    )

    old_weekly_goals = await fetch_all_weekly_goals(bot=bot)
    # Convert list of dicts to dict keyed by user_id for fast lookup
    old_weekly_goals_dict = {g["user_id"]: g for g in old_weekly_goals}
    debug_log(f"Fetched old weekly goals count: {len(old_weekly_goals)}")
    if not old_weekly_goals:
        debug_log("No existing weekly goals found. Entering initial upsert path.")
        # Upsert both known and unknown members
        for username, catches, fishes in clan_members_stats:
            debug_log(
                f"Initial upsert candidate: username={username}, catches={catches}, fishes={fishes}"
            )
            # Manually set member_id for this user before anything else
            if username == "neverlikenever_42984":
                member_id = 1327864338018730044
                debug_log(f"Manually resolved member_id for {username}: {member_id}")
            else:
                member_id = fetch_user_id_by_user_name_or_pokemeow_name_cache(username)
                debug_log(f"Resolved member_id for {username}: {member_id}")
            if member_id is None:
                pretty_log(
                    "info",
                    f"[WEEKLY STATS] Skipping upsert: Could not resolve user_id for username '{username}'",
                    label="💥 WEEKLY STATS USER_ID NULL",
                    bot=bot,
                )
                continue
            debug_log(f"Resolved member_id for {username}: {member_id}")
            member_info = celestial_members_cache.get(member_id)
            channel_id = member_info.get("channel_id") if member_info else None
            # Preserve existing requirement mark if user is already in cache
            existing_mark = weekly_goal_cache.get(member_id, {}).get(
                "weekly_requirement_mark", False
            )
            await upsert_weekly_goal(
                bot=bot,
                user_id=member_id,
                user_name=username,
                channel_id=channel_id,
                pokemon_caught=catches,
                fish_caught=fishes,
                battles_won=0,
                weekly_requirement_mark=existing_mark,
            )
            debug_log(
                f"Upserted initial weekly goal for {username} ({member_id}): catches={catches}, fishes={fishes}, channel_id={channel_id}, mark={existing_mark}"
            )
            await goal_checker(
                bot=bot,
                user_id=member_id,
                user_name=username,
                channel=after_message.channel,
                context="stats_command",
                guild=guild,
            )
            debug_log(
                f"Ran goal_checker for {username} ({member_id}) after initial upsert."
            )
    else:
        debug_log("Existing weekly goals found. Entering delta update path.")
        changes_detected = 0
        # Compare values
        for username, catches, fishes in clan_members_stats:
            member_id = fetch_user_id_by_user_name_or_pokemeow_name_cache(username)
            if member_id is None:
                pretty_log(
                    "info",
                    f"[WEEKLY STATS] Skipping upsert: Could not resolve user_id for username '{username}'",
                    label="💥 WEEKLY STATS USER_ID NULL",
                    bot=bot,
                )
                continue
            # Compare from old weekly goals from db
            old_goal = old_weekly_goals_dict.get(member_id) if member_id else None
            old_catches = old_goal.get("pokemon_caught") if old_goal else 0
            old_fishes = old_goal.get("fish_caught") if old_goal else 0
            debug_log(
                f"Weekly delta check for {username} ({member_id}): old=({old_catches},{old_fishes}), new=({catches},{fishes})"
            )
            if catches != old_catches or fishes != old_fishes:
                changes_detected += 1
                member_info = (
                    celestial_members_cache.get(member_id) if member_id else None
                )
                channel_id = member_info.get("channel_id") if member_info else None
                # Preserve existing requirement mark to avoid resetting if goal_checker already set it true
                existing_mark = weekly_goal_cache.get(member_id, {}).get(
                    "weekly_requirement_mark", False
                )
                debug_log(
                    f"Detected weekly stats change for {username} ({member_id}). Upserting and running goal_checker."
                )
                await upsert_weekly_goal(
                    bot=bot,
                    user_id=member_id,
                    user_name=username,
                    channel_id=channel_id,
                    pokemon_caught=catches,
                    fish_caught=fishes,
                    battles_won=0,
                    weekly_requirement_mark=existing_mark,
                )
                debug_log(
                    f"Upserted updated weekly goal for {username} ({member_id}): catches={catches}, fishes={fishes}, channel_id={channel_id}, mark={existing_mark}"
                )
                await goal_checker(
                    bot=bot,
                    user_id=member_id,
                    user_name=username,
                    channel=after_message.channel,
                    top_line_weekly_catches=catches,
                    context="stats_command",
                    guild=guild,
                )
                debug_log(
                    f"Ran goal_checker for {username} ({member_id}) after detected change."
                )
        if changes_detected == 0:
            pretty_log(
                "info",
                "No changes detected in weekly goals compared to the database.",
                label="💠 WEEKLY STATS DEBUG",
                bot=bot,
            )
            debug_log("Delta update path complete: no weekly stat changes detected.")
        else:
            debug_log(
                f"Delta update path complete: updated {changes_detected} member(s)."
            )
    pretty_log(
        "info",
        f"Weekly stats listener processed message ID {after_message.id} for page {current_page}.",
        label="💠 WEEKLY STATS DEBUG",
        bot=bot,
    )
    debug_log(
        f"weekly_stats_listener finished: message_id={after_message.id}, page={current_page}, top_line_catches={top_line_catches}"
    )
