# 🟦────────────────────────────────────────────
#       🐾 User pin_numbers alert Cache Loader 🐾
# ─────────────────────────────────────────────

import time

import discord

from utils.logs.pretty_log import pretty_log

from utils.cache.cache_list import pin_numbers_alert_cache


async def load_pin_numbers_alert_cache(bot):
    """
    Load all pin_numbers alerts into memory cache.
    """
    from utils.db.pin_numbers_alert_db_func import fetch_all_pin_numbers_alerts

    pin_numbers_alert_cache.clear()
    rows = await fetch_all_pin_numbers_alerts(bot)
    for row in rows:
        pin_numbers_alert_cache[row["user_id"]] = {
            "user_name": row.get("user_name"),
            "notify": row.get("notify"),
        }

    try:
        pretty_log(
            "info",
            f"Loaded {len(pin_numbers_alert_cache)} pin_numbers alert entries into cache",
            label="🛡️ pin_numbers Alert CACHE",
            bot=bot,
        )
    except Exception as e:
        # fallback to console if Discord logging fails
        pretty_log(
            "error",
            f"Failed to log pin_numbers alert cache load: {e}",
            label="🛡️ pin_numbers Alert CACHE",
        )
    return pin_numbers_alert_cache


# 🟦────────────────────────────────────────────
#       🔹 Upsert pin_numbers Alert in Cache 🔹
# ─────────────────────────────────────────────
def upsert_pin_numbers_alert_cache(user: discord.Member, notify: str):
    """
    Insert or update a user's pin_numbers alert in cache.
    """
    user_id = user.id
    user_name = user.name

    pin_numbers_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted pin_numbers alert for {user_name} ({user_id}) → {notify}",
        label="🐾 pin_numbers Alert CACHE",
    )


def upsert_pin_numbers_alert_cache_via_user_id(user_id: int, user_name: str, notify: str):
    """
    Insert or update a user's pin_numbers alert in cache using user ID.
    """
    pin_numbers_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted pin_numbers alert for {user_name} ({user_id}) → {notify}",
        label="🐾 pin_numbers Alert CACHE",
    )


# 🟦────────────────────────────────────────────
#       🔍 Fetch Single pin_numbers Alert 🔍
# ─────────────────────────────────────────────
def fetch_user_pin_numbers_alert_cache(user_id: int) -> dict | None:
    """
    Fetch a single user's pin_numbers alert from cache.
    """
    return pin_numbers_alert_cache.get(user_id)

def fetch_user_pin_numbers_notify_type_cache(user_id: int) -> str | None:
    """
    Fetch a single user's pin_numbers alert notify type from cache.
    """
    user_alert = pin_numbers_alert_cache.get(user_id)
    if user_alert:
        return user_alert.get("notify")
    return None
def fetch_user_pin_numbers_notify_type_cache_by_user_name(user_name: str) -> str | None:
    """
    Fetch a single user's pin_numbers alert notify type from cache using user name.
    """
    for alert in pin_numbers_alert_cache.values():
        if alert.get("user_name") == user_name:
            return alert.get("notify")
    return None

def fetch_user_pin_numbers_alert_cache_by_user_name(user_name: str) -> dict | None:
    """
    Fetch a single user's pin_numbers alert from cache using user name.
    """
    for alert in pin_numbers_alert_cache.values():
        if alert.get("user_name") == user_name:
            return alert
    return None

# 🟦────────────────────────────────────────────
#       📋 Fetch All pin_numbers alerts 📋
# ─────────────────────────────────────────────
def fetch_all_pin_numbers_alert_cache() -> dict[int, dict]:
    """
    Fetch all pin_numbers alerts from cache.
    """
    return pin_numbers_alert_cache


# 🟦────────────────────────────────────────────
#       ❌ Remove pin_numbers alert from Cache ❌
# ─────────────────────────────────────────────
def remove_user_pin_numbers_alert_cache(user: discord.Member):
    """
    Remove a user's pin_numbers alert from cache.
    """
    user_id = user.id
    user_name = user.name
    if user_id in pin_numbers_alert_cache:
        pin_numbers_alert_cache.pop(user_id)
        pretty_log(
            "info",
            f"Removed pin_numbers alert for {user_name} from cache",
            label="🐾 pin_numbers Alert CACHE",
        )


# 🟦────────────────────────────────────────────
#       ✏️ Update Alert Type in Cache ✏️
# ─────────────────────────────────────────────
def update_pin_numbers_alert_notify_type_cache(user: discord.Member, new_notify_type: str):
    """
    Update the alert_type of a user in cache.
    """
    user_id = user.id
    user_name = user.name

    if user_id in pin_numbers_alert_cache:
        pin_numbers_alert_cache[user_id]["notify"] = new_notify_type
        pretty_log(
            "info",
            f"Updated alert_type for {user_name} → {new_notify_type}",
            label="🐾 pin_numbers alert CACHE",
        )
