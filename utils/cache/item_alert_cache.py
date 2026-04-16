# 🟦────────────────────────────────────────────
#       🐾 User item alert Cache Loader 🐾
# ─────────────────────────────────────────────

import time

import discord

from utils.logs.pretty_log import pretty_log

from utils.cache.cache_list import item_alert_cache


async def load_item_alert_cache(bot):
    """
    Load all item alerts into memory cache.
    """
    from utils.db.item_alert_db_func  import fetch_all_item_alerts

    item_alert_cache.clear()
    rows = await fetch_all_item_alerts(bot)
    for row in rows:
        item_alert_cache[row["user_id"]] = {
            "user_name": row.get("user_name"),
            "notify": row.get("notify"),
        }

    try:
        pretty_log(
            "info",
            f"Loaded {len(item_alert_cache)} item alert entries into cache",
            label="🛡️ item Alert CACHE",
            bot=bot,
        )
    except Exception as e:
        # fallback to console if Discord logging fails
        pretty_log(
            "error",
            f"Failed to log item alert cache load: {e}",
            label="🛡️ item Alert CACHE",
        )
    return item_alert_cache


# 🟦────────────────────────────────────────────
#       🔹 Upsert item Alert in Cache 🔹
# ─────────────────────────────────────────────
def upsert_item_alert_cache(user: discord.Member, notify: str):
    """
    Insert or update a user's item alert in cache.
    """
    user_id = user.id
    user_name = user.name

    item_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted item alert for {user_name} ({user_id}) → {notify}",
        label="🐾 item Alert CACHE",
    )


def upsert_item_alert_cache_via_user_id(
    user_id: int, user_name: str, notify: str
):
    """
    Insert or update a user's item alert in cache using user ID.
    """
    item_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted item alert for {user_name} ({user_id}) → {notify}",
        label="🐾 item Alert CACHE",
    )


# 🟦────────────────────────────────────────────
#       🔍 Fetch Single item Alert 🔍
# ─────────────────────────────────────────────
def fetch_user_item_alert_cache(user_id: int) -> dict | None:
    """
    Fetch a single user's item alert from cache.
    """
    return item_alert_cache.get(user_id)


# 🟦────────────────────────────────────────────
#       📋 Fetch All item alerts 📋
# ─────────────────────────────────────────────
def fetch_all_item_alert_cache() -> dict[int, dict]:
    """
    Fetch all item alerts from cache.
    """
    return item_alert_cache


# 🟦────────────────────────────────────────────
#       ❌ Remove item alert from Cache ❌
# ─────────────────────────────────────────────
def remove_user_item_alert_cache(user: discord.Member):
    """
    Remove a user's item alert from cache.
    """
    user_id = user.id
    user_name = user.name
    if user_id in item_alert_cache:
        item_alert_cache.pop(user_id)
        pretty_log(
            "info",
            f"Removed item alert for {user_name} from cache",
            label="🐾 item Alert CACHE",
        )


# 🟦────────────────────────────────────────────
#       ✏️ Update Alert Type in Cache ✏️
# ─────────────────────────────────────────────
def update_item_alert_notify_type_cache(
    user: discord.Member, new_notify_type: str
):
    """
    Update the alert_type of a user in cache.
    """
    user_id = user.id
    user_name = user.name

    if user_id in item_alert_cache:
        item_alert_cache[user_id]["notify"] = new_notify_type
        pretty_log(
            "info",
            f"Updated alert_type for {user_name} → {new_notify_type}",
            label="🐾 item alert CACHE",
        )
