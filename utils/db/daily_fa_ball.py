from utils.logs.pretty_log import pretty_log

# 🌸──────────────────────────────────────────────
#      🧸 Daily Faction Ball DB Functions
# 🌸──────────────────────────────────────────────

FACTIONS = ["aqua", "flare", "galactic", "magma", "plasma", "rocket", "skull", "yell"]


# 🍡──────────────────────────────────────────────
#   Fetch All Faction Ball Values as Dict
# 🍡──────────────────────────────────────────────
async def fetch_all_faction_balls(bot) -> dict:
    """Fetch all faction ball values as a dict."""
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM daily_faction_ball")
            return dict(row) if row else {f: None for f in FACTIONS}
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to fetch daily faction ball values: {e}",
            bot=bot,
        )
        return {f: None for f in FACTIONS}


# 🍥──────────────────────────────────────────────
#   Update a Specific Faction Ball Value
# 🍥──────────────────────────────────────────────
async def update_faction_ball(bot, faction: str, ball_type: str | None):
    """Ensure a single row exists and update the faction ball value."""
    if faction not in FACTIONS:
        raise ValueError(f"Invalid faction: {faction}")
    try:
        async with bot.pg_pool.acquire() as conn:
            # Insert a single row if none exists, then update
            await conn.execute(
                """
                INSERT INTO daily_faction_ball (id)
                VALUES (1)
                ON CONFLICT (id) DO NOTHING
            """
            )
            await conn.execute(
                f"UPDATE daily_faction_ball SET {faction} = $1 WHERE id = 1",
                ball_type,
            )

        pretty_log(
            tag="db",
            message=f"Upserted {faction} ball to {ball_type}",
            bot=bot,
        )

        # Update cache
        from utils.cache.daily_fa_ball_cache import update_daily_faction_ball_cache

        update_daily_faction_ball_cache(faction, ball_type)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to upsert {faction} ball: {e}",
            bot=bot,
        )


# 🍭──────────────────────────────────────────────
#   Clear All Faction Ball Values
# 🍭──────────────────────────────────────────────
async def clear_daily_faction_ball(bot):
    """Set all faction ball values to NULL."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                "UPDATE daily_faction_ball SET "
                + ", ".join(f"{f} = NULL" for f in FACTIONS)
            )
        pretty_log(
            tag="db",
            message="Cleared all daily faction ball values.",
            bot=bot,
        )
        # Also clear the cache
        from utils.cache.daily_fa_ball_cache import \
            clear_daily_faction_ball_cache

        clear_daily_faction_ball_cache()
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to clear daily faction ball table: {e}",
            bot=bot,
        )
