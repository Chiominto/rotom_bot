# 🟦────────────────────────────────────────────
#       🐾 User egg alert Cache Loader 🐾
# ─────────────────────────────────────────────

import time

import discord

from utils.logs.pretty_log import pretty_log

from utils.cache.cache_list import egg_alert_cache


async def load_egg_alert_cache(bot):
    """
    Load all egg alerts into memory cache.
    """
    from utils.db.egg_alert_db_func import fetch_all_egg_alerts

    egg_alert_cache.clear()
    rows = await fetch_all_egg_alerts(bot)
    for row in rows:
        egg_alert_cache[row["user_id"]] = {
            "user_name": row.get("user_name"),
            "notify": row.get("notify"),
        }

    try:
        pretty_log(
            "info",
            f"Loaded {len(egg_alert_cache)} egg alert entries into cache",
            label="🛡️ Egg Alert CACHE",
            bot=bot,
        )
    except Exception as e:
        # fallback to console if Discord logging fails
        pretty_log(
            "error",
            f"Failed to log egg alert cache load: {e}",
            label="🛡️ Egg Alert CACHE",
        )
    return egg_alert_cache


# 🟦────────────────────────────────────────────
#       🔹 Upsert egg Alert in Cache 🔹
# ─────────────────────────────────────────────
def upsert_egg_alert_cache(user: discord.Member, notify: str):
    """
    Insert or update a user's egg alert in cache.
    """
    user_id = user.id
    user_name = user.name

    egg_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted egg alert for {user_name} ({user_id}) → {notify}",
        label="🐾 egg Alert CACHE",
    )


def upsert_egg_alert_cache_via_user_id(
    user_id: int, user_name: str, notify: str
):
    """
    Insert or update a user's egg alert in cache using user ID.
    """
    egg_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted egg alert for {user_name} ({user_id}) → {notify}",
        label="🐾 egg Alert CACHE",
    )


# 🟦────────────────────────────────────────────
#       🔍 Fetch Single egg Alert 🔍
# ─────────────────────────────────────────────
def fetch_user_egg_alert_cache(user_id: int) -> dict | None:
    """
    Fetch a single user's egg alert from cache.
    """
    return egg_alert_cache.get(user_id)


# 🟦────────────────────────────────────────────
#       📋 Fetch All egg alerts 📋
# ─────────────────────────────────────────────
def fetch_all_egg_alert_cache() -> dict[int, dict]:
    """
    Fetch all egg alerts from cache.
    """
    return egg_alert_cache


# 🟦────────────────────────────────────────────
#       ❌ Remove egg alert from Cache ❌
# ─────────────────────────────────────────────
def remove_user_egg_alert_cache(user: discord.Member):
    """
    Remove a user's egg alert from cache.
    """
    user_id = user.id
    user_name = user.name
    if user_id in egg_alert_cache:
        egg_alert_cache.pop(user_id)
        pretty_log(
            "info",
            f"Removed egg alert for {user_name} from cache",
            label="🐾 egg Alert CACHE",
        )


# 🟦────────────────────────────────────────────
#       ✏️ Update Alert Type in Cache ✏️
# ─────────────────────────────────────────────
def update_egg_alert_notify_type_cache(
    user: discord.Member, new_notify_type: str
):
    """
    Update the alert_type of a user in cache.
    """
    user_id = user.id
    user_name = user.name

    if user_id in egg_alert_cache:
        egg_alert_cache[user_id]["notify"] = new_notify_type
        pretty_log(
            "info",
            f"Updated alert_type for {user_name} → {new_notify_type}",
            label="🐾 egg alert CACHE",
        )
