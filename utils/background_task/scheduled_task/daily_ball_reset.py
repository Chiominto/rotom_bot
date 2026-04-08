import discord
from utils.logs.pretty_log import pretty_log

from utils.db.daily_fa_ball import clear_daily_faction_ball

# 🍥──────────────────────────────────────────────
#   Daily Faction Ball Reset Task
# 🍥──────────────────────────────────────────────
async def daily_ball_reset(bot):
    """Resets the daily faction ball data."""
    try:
        await clear_daily_faction_ball(bot)
        pretty_log(
            tag="background_task",
            message="Daily faction ball data has been reset.",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to reset daily faction ball data: {e}",
            bot=bot,
        )


