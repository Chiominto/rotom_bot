import asyncio
import re
from datetime import datetime

import discord
from discord.ext import commands

from constants.aesthetics import *
from constants.celestial_constants import POKEMEOW_APPLICATION_ID
from utils.cache.cache_list import timer_cache, timer_users  # 💜 import your cache
from utils.functions.get_pokemeow_reply import get_pokemeow_reply
from utils.functions.retry_function import _retry_discord_call
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

#enable_debug(f"{__name__}.fish_timer_handler")
FISH_TIMER = 25

# 🗂 Track scheduled "command ready" tasks to avoid duplicates
fish_ready_tasks = {}


def extract_fishing_trainer_name(description: str) -> str | None:
    """
    Extracts the trainer name (e.g. 'khy.09') from a PokéMeow fishing embed description.
    Example: '<:irida:...> **khy.09** cast a ...'
    """
    match = re.search(r"\*\*(.+?)\*\* cast a", description)
    if match:
        return match.group(1).strip()
    return None


# 💜────────────────────────────────────────────
#   Function: detect_pokemeow_reply
#   Handles Pokemon timer notifications per user settings
# 💜────────────────────────────────────────────
async def fish_timer_handler(message: discord.Message):
    """
    Triggered on any message.
    Handles Fish ready notifications depending on user's timer cache settings:
      - off → ignore
      - on → ping them in channel
      - on w/o pings → send message w/o mention
    """
    try:
        debug_log(f"Received message from author ID: {message.author.id}")
        if message.author.id != POKEMEOW_APPLICATION_ID:
            # debug_log("Message is not from PokeMeow bot, ignoring.")
            return

        if not message.embeds:
            # debug_log("Message has no embeds, ignoring.")
            return

        embed = message.embeds[0]
        embed_description = embed.description or ""
        guild = message.guild
        # debug_log(f"Embed description (first 100 chars): {embed_description[:100]}")

        member = await get_pokemeow_reply(message)
        if not member:
            debug_log(
                "get_pokemeow_reply returned None, falling back to username extraction."
            )
            # Fall back to username extraction if needed
            user_name = extract_fishing_trainer_name(embed_description)
            if not user_name:
                debug_log("No trainer name found in embed description.")
                return
            debug_log(f"Extracted trainer name: {user_name}")

            # Check timer_users cache first
            if user_name in timer_users:
                member = guild.get_member(timer_users[user_name])
            else:
                from utils.cache.timers_cache import fetch_id_by_user_name

                user_id = fetch_id_by_user_name(user_name)
                if not user_id:
                    debug_log(f"No user ID found for trainer name: {user_name}")
                    return
                member = guild.get_member(user_id)
                if member:
                    timer_users[user_name] = member.id  # cache for next time
            if not member:
                debug_log(f"No guild member found for trainer name: {user_name}")
                return

        debug_log(f"Matched member: {member} (ID: {member.id})")

        # -------------------------------
        # 💜 Check timer_cache settings
        # -------------------------------
        from utils.cache.timers_cache import timer_cache

        debug_log(
            f"Current timer_cache keys: {list(timer_cache.keys())[:3]} (showing 3)"
        )
        user_settings = timer_cache.get(member.id)
        debug_log(f"User settings from timer_cache: {user_settings}")
        if not user_settings:
            debug_log("No user settings found in timer_cache.")
            return

        setting = (user_settings.get("fish_setting") or "off").lower()
        debug_log(f"Fish timer setting: {setting}")
        if setting == "off":
            debug_log("Fish timer setting is off, not notifying.")
            return

        # Cancel previous ready task if any
        if member.id in fish_ready_tasks and not fish_ready_tasks[member.id].done():
            debug_log(f"Cancelling previous fish ready task for member {member.id}")
            fish_ready_tasks[member.id].cancel()

        # Schedule behavior depending on setting
        async def notify_ready():
            # 💜────────────────────────────────────────────
            #   Fish Timer Notification Task
            # 💜────────────────────────────────────────────
            try:
                debug_log(
                    f"notify_ready: sleeping for {FISH_TIMER} seconds before notifying."
                )
                await asyncio.sleep(FISH_TIMER)
                debug_log(
                    f"notify_ready: woke up, preparing to notify (setting: {setting})",
                    highlight=True,
                )

                if setting == "on":
                    debug_log(f"Notifying with mention for {member}")
                    content = f"{FISH_TIMER_EMOJI} {member.mention}, your </fish spawn:1015311084812501026> command is ready! "
                elif setting in ("on_no_pings", "on w/o pings"):
                    debug_log(f"Notifying without mention for {member}")
                    content = f"{FISH_TIMER_EMOJI} **{member.name}**, your </fish spawn:1015311084812501026> command is ready!"
                else:
                    debug_log(f"Unknown fish setting '{setting}', skipping.")
                    return

                await _retry_discord_call(message.channel.send, content)

            except asyncio.CancelledError:
                debug_log(f"notify_ready: Cancelled for {member}")
                # 💙 [CANCELLED] Scheduled ready notification cancelled
                pretty_log(
                    tag="info",
                    message=f"Cancelled scheduled ready notification for {member}",
                )
            except Exception as e:
                debug_log(f"notify_ready: Exception occurred for {member}: {e}")
                # 💜 [MISSED] Timer ran correctly but message failed
                # Trackable: include member ID and username
                pretty_log(
                    tag="error",
                    message=(
                        f"Missed fish timer notification for {member} "
                        f"(ID: {member.id}). Timer ran correctly but message failed: {e}"
                    ),
                )

        debug_log(f"Creating notify_ready task for member {member.id}")
        fish_ready_tasks[member.id] = asyncio.create_task(notify_ready())

    except Exception as e:
        debug_log(f"Exception in fish_timer_handler: {e}", highlight=True)
        pretty_log(
            tag="critical",
            message=f"Unhandled exception in fish_timer_handler: {e}",
        )
