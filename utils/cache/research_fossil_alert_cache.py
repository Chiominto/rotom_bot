# 🟦────────────────────────────────────────────
#       🐾 User research_fossil alert Cache Loader 🐾
# ─────────────────────────────────────────────

import time

import discord

from utils.logs.pretty_log import pretty_log

from utils.cache.cache_list import research_fossil_alert_cache


async def load_research_fossil_alert_cache(bot):
    """
    Load all research_fossil alerts into memory cache.
    """
    from utils.db.research_fossil_alert_db_func import fetch_all_research_fossil_alerts

    research_fossil_alert_cache.clear()
    rows = await fetch_all_research_fossil_alerts(bot)
    for row in rows:
        research_fossil_alert_cache[row["user_id"]] = {
            "user_name": row.get("user_name"),
            "notify": row.get("notify"),
        }

    try:
        pretty_log(
            "info",
            f"Loaded {len(research_fossil_alert_cache)} research_fossil alert entries into cache",
            label="🛡️ research_fossil Alert CACHE",
            bot=bot,
        )
    except Exception as e:
        # fallback to console if Discord logging fails
        pretty_log(
            "error",
            f"Failed to log research_fossil alert cache load: {e}",
            label="🛡️ research_fossil Alert CACHE",
        )
    return research_fossil_alert_cache


# 🟦────────────────────────────────────────────
#       🔹 Upsert research_fossil Alert in Cache 🔹
# ─────────────────────────────────────────────
def upsert_research_fossil_alert_cache(user: discord.Member, notify: str):
    """
    Insert or update a user's research_fossil alert in cache.
    """
    user_id = user.id
    user_name = user.name

    research_fossil_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted research_fossil alert for {user_name} ({user_id}) → {notify}",
        label="🐾 research_fossil Alert CACHE",
    )


def upsert_research_fossil_alert_cache_via_user_id(user_id: int, user_name: str, notify: str):
    """
    Insert or update a user's research_fossil alert in cache using user ID.
    """
    research_fossil_alert_cache[user_id] = {
        "user_name": user_name,
        "notify": notify,
    }
    pretty_log(
        "info",
        f"Upserted research_fossil alert for {user_name} ({user_id}) → {notify}",
        label="🐾 research_fossil Alert CACHE",
    )


# 🟦────────────────────────────────────────────
#       🔍 Fetch Single research_fossil Alert 🔍
# ─────────────────────────────────────────────
def fetch_user_research_fossil_alert_cache(user_id: int) -> dict | None:
    """
    Fetch a single user's research_fossil alert from cache.
    """
    return research_fossil_alert_cache.get(user_id)

def fetch_user_research_fossil_notify_type_cache(user_id: int) -> str | None:
    """
    Fetch a single user's research_fossil alert notify type from cache.
    """
    user_alert = research_fossil_alert_cache.get(user_id)
    if user_alert:
        return user_alert.get("notify")
    return None
def fetch_user_research_fossil_notify_type_cache_by_user_name(user_name: str) -> str | None:
    """
    Fetch a single user's research_fossil alert notify type from cache using user name.
    """
    for alert in research_fossil_alert_cache.values():
        if alert.get("user_name") == user_name:
            return alert.get("notify")
    return None

def fetch_user_research_fossil_alert_cache_by_user_name(user_name: str) -> dict | None:
    """
    Fetch a single user's research_fossil alert from cache using user name.
    """
    for alert in research_fossil_alert_cache.values():
        if alert.get("user_name") == user_name:
            return alert
    return None

# 🟦────────────────────────────────────────────
#       📋 Fetch All research_fossil alerts 📋
# ─────────────────────────────────────────────
def fetch_all_research_fossil_alert_cache() -> dict[int, dict]:
    """
    Fetch all research_fossil alerts from cache.
    """
    return research_fossil_alert_cache


# 🟦────────────────────────────────────────────
#       ❌ Remove research_fossil alert from Cache ❌
# ─────────────────────────────────────────────
def remove_user_research_fossil_alert_cache(user: discord.Member):
    """
    Remove a user's research_fossil alert from cache.
    """
    user_id = user.id
    user_name = user.name
    if user_id in research_fossil_alert_cache:
        research_fossil_alert_cache.pop(user_id)
        pretty_log(
            "info",
            f"Removed research_fossil alert for {user_name} from cache",
            label="🐾 research_fossil Alert CACHE",
        )


# 🟦────────────────────────────────────────────
#       ✏️ Update Alert Type in Cache ✏️
# ─────────────────────────────────────────────
def update_research_fossil_alert_notify_type_cache(user: discord.Member, new_notify_type: str):
    """
    Update the alert_type of a user in cache.
    """
    user_id = user.id
    user_name = user.name

    if user_id in research_fossil_alert_cache:
        research_fossil_alert_cache[user_id]["notify"] = new_notify_type
        pretty_log(
            "info",
            f"Updated alert_type for {user_name} → {new_notify_type}",
            label="🐾 research_fossil alert CACHE",
        )
