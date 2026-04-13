import discord

from utils.db.wb_fight_db import fetch_all_wb_battle_alerts
from utils.logs.pretty_log import pretty_log

from utils.cache.cache_list import wb_battle_alert_cache


async def load_wb_battle_alert_cache(bot: discord.Client):
    """
    Load all world boss battle alerts from the database into the in-memory cache.
    This function should be called during bot startup.
    """

    wb_battle_alert_cache.clear()
    rows = await fetch_all_wb_battle_alerts(bot)
    for row in rows:
        wb_battle_alert_cache[row["user_id"]] = {
            "user_name": row.get("user_name"),
            "notify": row.get("notify"),
        }
    try:
        pretty_log(
            "info",
            f"Loaded {len(wb_battle_alert_cache)} world boss battle alert entries into cache",
            label="🛡️  World Boss Battle Alert CACHE",
            bot=bot,
        )
        #print(wb_battle_alert_cache)
    except Exception as e:
        # fallback to console if Discord logging fails
        print(
            f"[🛡️  World Boss Battle ALERT CACHE] Loaded {len(wb_battle_alert_cache)} entries (pretty_log failed: {e})"
        )
    return wb_battle_alert_cache


def upsert_wb_battle_alert_cache(user_id: int, user_name: str, notify: str):
    """
    Upsert a world boss battle alert into the in-memory cache.

    Args:
        user_id: The Discord user ID.
        user_name: The Discord user name.
        notify: Notification preference string.
    """

    wb_battle_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted world boss battle alert for user {user_id} into cache.",
    )


def update_wb_battle_alert_cache(user_id: int, notify: str):
    """
    Update the notification preference of a world boss battle alert in the in-memory cache.

    Args:
        user_id: The Discord user ID.
        notify: New notification preference string.
    """
    if user_id in wb_battle_alert_cache:
        user_name = wb_battle_alert_cache[user_id]["user_name"]
        wb_battle_alert_cache[user_id]["notify"] = notify
        pretty_log(
            "info",
            f"Updated world boss battle alert notify for user {user_name} in cache.",
        )


def remove_wb_battle_alert_cache(user_id: int):
    """
    Remove a world boss battle alert from the in-memory cache.

    Args:
        user_id: The Discord user ID.
    """
    if user_id in wb_battle_alert_cache:
        user_name = wb_battle_alert_cache[user_id]["user_name"]
        del wb_battle_alert_cache[user_id]
        pretty_log(
            "info",
            f"Removed world boss battle alert for user {user_name} from cache.",
        )

def fetch_wb_battle_alert_notify_cache(user_id: int) -> str | None:
    """
    Fetch the notification preference for a specific user from the world boss battle alert cache.

    Args:
        user_id: The Discord user ID.
    Returns:
        The notification preference string if the user exists in the cache, otherwise None.
    """
    alert_info = wb_battle_alert_cache.get(user_id)
    if alert_info:
        return alert_info.get("notify")
    return None