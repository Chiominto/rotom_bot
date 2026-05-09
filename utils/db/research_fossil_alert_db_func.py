# 💠────────────────────────────────────────────
#   🐾 User research_fossil alert DB Functions
# 💠────────────────────────────────────────────

import asyncpg
import discord

from utils.logs.pretty_log import pretty_log

TABLE_NAME = "user_alerts"
ALERT_TYPE = "research_fossil"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💾 Fetch all research_fossil alerts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def fetch_all_research_fossil_alerts(bot) -> list[asyncpg.Record]:
    """
    Fetch all rows where alert_type='research_fossil'.

    Args:
        bot: The Discord bot instance containing the PostgreSQL pool.

    Returns:
        List of asyncpg.Record representing all research_fossil alerts.
        Returns [] if query fails.
    """
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT * FROM {TABLE_NAME} WHERE alert_type=$1", ALERT_TYPE
            )
            return rows

    except Exception as e:
        pretty_log("error", f"Failed to fetch {ALERT_TYPE} alerts: {e}", bot=bot)
        return []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💾 Fetch single user research_fossil alert
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def fetch_user_research_fossil_alert(bot, user_id: int) -> asyncpg.Record | None:
    """
    Fetch a single user's research_fossil alert row.

    Args:
        bot: The Discord bot instance containing the PostgreSQL pool.
        user_id: The Discord user ID.

    Returns:
        asyncpg.Record if found, else None.
    """
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT * FROM {TABLE_NAME} WHERE user_id=$1 AND alert_type=$2",
                user_id,
                ALERT_TYPE,
            )
            return row

    except Exception as e:
        pretty_log(
            "error", f"Failed to fetch {ALERT_TYPE} alert for {user_id}: {e}", bot=bot
        )
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💾 Upsert research_fossil alert
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def upsert_user_research_fossil_alert(bot, user: discord.Member, notify: str):
    """
    Insert or update a user's research_fossil alert.

    Args:
        bot: The Discord bot instance containing the PostgreSQL pool.
        user_id: Discord user ID.
        user_name: Discord username.
        notify: How the user wants to be notified.
    """
    user_id = user.id
    user_name = user.name
    try:
        from utils.cache.research_fossil_alert_cache import upsert_research_fossil_alert_cache

        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {TABLE_NAME} (user_id, user_name, alert_type, notify)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, alert_type)
                DO UPDATE SET
                    user_name = EXCLUDED.user_name,
                    notify = EXCLUDED.notify
                """,
                user_id,
                user_name,
                ALERT_TYPE,
                notify,
            )

        pretty_log(
            "db",
            f"Upserted {ALERT_TYPE} alert for {user_name} → notify: {notify}",
            bot=bot,
        )

        upsert_research_fossil_alert_cache(user=user, notify=notify)

    except Exception as e:
        pretty_log(
            "error", f"Failed to upsert {ALERT_TYPE} alert for {user_id}: {e}", bot=bot
        )


async def upsert_user_research_fossil_alert_via_user_id(
    bot, user_id: int, user_name: str, notify: str
):
    """
    Upsert a user's research_fossil alert using user ID and name.

    Args:
        bot: The Discord bot instance containing the PostgreSQL pool.
        user_id: Discord user ID.
        user_name: Discord username.
        notify: How the user wants to be notified.
    """
    try:
        from utils.cache.research_fossil_alert_cache import (
            upsert_research_fossil_alert_cache_via_user_id,
        )

        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {TABLE_NAME} (user_id, user_name, alert_type, notify)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, alert_type)
                DO UPDATE SET
                    user_name = EXCLUDED.user_name,
                    notify = EXCLUDED.notify
                """,
                user_id,
                user_name,
                ALERT_TYPE,
                notify,
            )

        pretty_log(
            "db",
            f"Upserted {ALERT_TYPE} alert for {user_name} → notify: {notify}",
            bot=bot,
        )

        upsert_research_fossil_alert_cache_via_user_id(
            user_id=user_id, user_name=user_name, notify=notify
        )

    except Exception as e:
        pretty_log(
            "error", f"Failed to upsert {ALERT_TYPE} alert for {user_id}: {e}", bot=bot
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💾 Remove research_fossil alert
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def remove_user_research_fossil_alert(bot, user: discord.Member):
    """
    Remove a user's research_fossil alert row from DB and cache.

    Args:
        bot: The Discord bot instance containing the PostgreSQL pool.
        user: The Discord member object.
    """
    user_id = user.id
    user_name = user.name

    try:
        from utils.cache.research_fossil_alert_cache import (
            remove_user_research_fossil_alert_cache,
        )

        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                f"DELETE FROM {TABLE_NAME} WHERE user_id=$1 AND alert_type=$2",
                user_id,
                ALERT_TYPE,
            )

        pretty_log("db", f"Removed {ALERT_TYPE} alert for {user_name}", bot=bot)
        remove_user_research_fossil_alert_cache(user=user)

    except Exception as e:
        pretty_log(
            "error",
            f"Failed to remove {ALERT_TYPE} alert for {user_name}: {e}",
            bot=bot,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💾 Update notify type
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def update_user_research_fossil_notify(bot, user: discord.Member, new_notify: str):
    """
    Update a user's `notify` type for research_fossil alerts.

    Args:
        bot: The Discord bot instance containing the PostgreSQL pool.
        user: The Discord member object.
        new_notify: The new notify setting to apply.
    """
    user_id = user.id
    user_name = user.name

    try:
        from utils.cache.research_fossil_alert_cache import (
            update_research_fossil_alert_notify_type_cache,
        )

        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                f"""
                UPDATE {TABLE_NAME}
                SET notify=$1
                WHERE user_id=$2 AND alert_type=$3
                """,
                new_notify,
                user_id,
                ALERT_TYPE,
            )

        pretty_log(
            "db",
            f"Updated {ALERT_TYPE} notify for {user_name} → {new_notify}",
            bot=bot,
        )

        update_research_fossil_alert_notify_type_cache(user=user, new_notify=new_notify)

    except Exception as e:
        pretty_log(
            "error",
            f"Failed to update {ALERT_TYPE} notify for {user_name}: {e}",
            bot=bot,
        )
