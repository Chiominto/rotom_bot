import discord

from constants.celestial_constants import (
    CELESTIAL_TEXT_CHANNELS,
    CELESTIALS_SERVER_ID,
    DEFAULT_EMBED_COLOR,
    MONTHLY_REQUIREMENT,
    WEEKLY_REQUIREMENT,
)
from utils.cache.cache_list import monthly_goal_cache, weekly_goal_cache
from utils.cache.monthly_goal_tracker_cache import monthly_goal_cache_dirty
from utils.cache.weekly_goal_tracker_cache import weekly_goal_cache_dirty
from utils.db.monthly_goal_tracker import delete_all_monthly_goals
from utils.db.weekly_goal_tracker import delete_all_weekly_goals
from utils.logs.pretty_log import pretty_log

NEW_WEEK_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493871255475191888/1502590235899461643/Embed_2.png?ex=6a00ec75&is=69ff9af5&hm=d83d9a82cdf692a90f60e5caae7eaaad1c62cd93b1a3ab8bfbcdf86deda959f5"
NEW_MONTH_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493871255475191888/1502590276743462922/Embed_3.png?ex=6a00ec7e&is=69ff9afe&hm=01f91800236b8a4a7eb7293bf01ab3d2a5e26a7664b9fa99d224a14e87c4e6ab"
GOAL_TRACKER_CHANNEL_ID = CELESTIAL_TEXT_CHANNELS.goal_tracker


# 🍥──────────────────────────────────────────────
# Weekly Goal Tracker Reset Task
# 🍥──────────────────────────────────────────────
async def weekly_goal_track_reset(bot):
    """Resets the weekly goal tracker data."""
    try:
        await delete_all_weekly_goals(bot)
        # Keep runtime state aligned with DB reset to allow fresh weekly announcements.
        weekly_goal_cache.clear()
        weekly_goal_cache_dirty.clear()
        pretty_log(
            tag="background_task",
            message="Weekly goal tracker data has been reset.",
            bot=bot,
        )
        # Send notification to Goal Tracker channel
        guild = bot.get_guild(CELESTIALS_SERVER_ID)
        if guild:
            channel = guild.get_channel(GOAL_TRACKER_CHANNEL_ID)
            if channel:
                await channel.send(NEW_WEEK_IMAGE_URL)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to reset weekly goal tracker data: {e}",
            bot=bot,
        )


# 🍥──────────────────────────────────────────────
# Monthly Goal Tracker Reset Task
# 🍥──────────────────────────────────────────────
async def monthly_goal_track_reset(bot):
    """Resets the monthly goal tracker data."""
    try:
        await delete_all_monthly_goals(bot)
        # Keep runtime state aligned with DB reset to allow fresh monthly announcements.
        monthly_goal_cache.clear()
        monthly_goal_cache_dirty.clear()
        pretty_log(
            tag="background_task",
            message="Monthly goal tracker data has been reset.",
            bot=bot,
        )
        # Send notification to Goal Tracker channel
        guild = bot.get_guild(CELESTIALS_SERVER_ID)
        if guild:
            channel = guild.get_channel(GOAL_TRACKER_CHANNEL_ID)
            if channel:
                await channel.send(NEW_MONTH_IMAGE_URL)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to reset monthly goal tracker data: {e}",
            bot=bot,
        )
