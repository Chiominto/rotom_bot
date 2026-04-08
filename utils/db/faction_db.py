from utils.logs.pretty_log import pretty_log
import discord
# SQL SCRIPT
"""CREATE TABLE factions (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT,
    faction TEXT
);"""


async def upsert_faction(bot:discord.Client, user_id: int, user_name: str, faction: str):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO factions (user_id, user_name, faction)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET
                    user_name = EXCLUDED.user_name,
                    faction = EXCLUDED.faction
                """,
                user_id,
                user_name,
                faction,
            )

        pretty_log(
            "db",
            f"Upserted faction for {user_name} → {faction}",
            bot=bot,
        )
        # Upsert into cache as well
        from utils.cache.faction_cache import upsert_faction_cache
        upsert_faction_cache(user_id, user_name, faction)

    except Exception as e:
        pretty_log(
            "error",
            f"Failed to upsert faction for {user_name}: {e}",
            bot=bot,
        )

async def fetch_all_user_factions(bot:discord.Client):
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id, user_name, faction FROM factions")
            result = {row["user_id"]: {"user_name": row["user_name"], "faction": row["faction"]} for row in rows}
            pretty_log(
                "db",
                f"Fetched {len(result)} user factions from database",
                bot=bot,
            )
            return result

    except Exception as e:
        pretty_log(
            "error",
            f"Failed to fetch user factions: {e}",
            bot=bot,
        )
        return {}

async def remove_faction(bot:discord.Client, user_id: int):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM factions WHERE user_id = $1",
                user_id,
            )

        pretty_log(
            "db",
            f"Removed faction for user_id {user_id}",
            bot=bot,
        )
        # Remove from cache as well
        from utils.cache.faction_cache import remove_faction_cache
        remove_faction_cache(user_id)

    except Exception as e:
        pretty_log(
            "error",
            f"Failed to remove faction for user_id {user_id}: {e}",
            bot=bot,
        )
