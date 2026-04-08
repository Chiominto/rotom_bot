from utils.db.daily_fa_ball import fetch_all_faction_balls
from utils.logs.pretty_log import pretty_log
from utils.cache.cache_list import daily_faction_ball_cache
# 🌸──────────────────────────────────────────────
#      🧸 Daily Faction Ball Cache Functions
# 🌸──────────────────────────────────────────────

# 🍡──────────────────────────────────────────────
#   Load Daily Faction Ball Cache from Database
# 🍡──────────────────────────────────────────────
async def load_daily_faction_ball_cache(bot):
    """Load the daily faction ball cache from the database."""
    try:
        new_cache = await fetch_all_faction_balls(bot)
        daily_faction_ball_cache.update(new_cache)
        pretty_log(tag="cache", message="Loaded daily faction ball cache.", bot=bot)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to load daily faction ball cache: {e}",
            bot=bot,
        )
    return daily_faction_ball_cache


# 🍥──────────────────────────────────────────────
#   Update a Specific Faction Ball in Cache
# 🍥──────────────────────────────────────────────
def update_daily_faction_ball_cache(faction: str, ball_type: str | None):
    """Update a specific faction ball in the cache."""
    if faction in daily_faction_ball_cache:
        daily_faction_ball_cache[faction] = ball_type
        pretty_log(
            tag="cache",
            message=f"Updated {faction} ball in cache to {ball_type}.",
            bot=None,
        )
    else:
        pretty_log(
            tag="info",
            message=f"Attempted to update invalid faction {faction} in cache.",
            bot=None,
        )


# 🧁──────────────────────────────────────────────
#   Get the Entire Daily Faction Ball Cache
# 🧁──────────────────────────────────────────────
def get_daily_faction_ball_cache() -> dict[str, str | None]:
    """Get the current daily faction ball cache."""
    return daily_faction_ball_cache


# 🍬──────────────────────────────────────────────
#   Get a Specific Faction Ball from Cache
# 🍬──────────────────────────────────────────────
def get_faction_ball(faction: str) -> str | None:
    """Get the ball type for a specific faction from the cache."""
    return daily_faction_ball_cache.get(faction)


# 🍭──────────────────────────────────────────────
#   Clear the Daily Faction Ball Cache
# 🍭──────────────────────────────────────────────
def clear_daily_faction_ball_cache():
    """Clear the daily faction ball cache (set all to None)."""
    for faction in daily_faction_ball_cache:
        daily_faction_ball_cache[faction] = None
    pretty_log(tag="cache", message="Cleared daily faction ball cache.")
    return daily_faction_ball_cache
