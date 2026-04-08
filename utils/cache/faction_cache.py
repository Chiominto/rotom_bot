import discord
from utils.cache.cache_list import faction_cache
from utils.db.faction_db import fetch_all_user_factions
from utils.logs.pretty_log import pretty_log


async def load_faction_cache(bot: discord.Client):
    """Load all user factions into memory cache."""
    faction_cache.clear()
    try:
        rows = await fetch_all_user_factions(bot)
        faction_cache.update(rows)
        pretty_log(
            "info",
            f"Loaded {len(faction_cache)} user factions into cache",
            label="🛡️  Faction CACHE",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to load faction cache: {e}",
            label="🛡️  Faction CACHE",
            bot=bot,
        )
    return faction_cache

def upsert_faction_cache(user_id: int, user_name: str, faction: str):
    """Insert or update a user's faction in cache."""
    faction_cache[user_id] = {
        "user_name": user_name,
        "faction": faction,
    }
    pretty_log(
        "info",
        f"Upserted faction for {user_name} ({user_id}) → {faction}",
        label="🛡️  Faction CACHE",
    )

def get_user_faction(user_id: int) -> str | None:
    """Get a user's faction from cache."""
    user_data = faction_cache.get(user_id)
    if user_data:
        return user_data.get("faction")
    return None


def remove_faction_cache(user_id: int):
    """Remove a user's faction from cache."""
    if user_id in faction_cache:
        removed_user = faction_cache.pop(user_id)
        pretty_log(
            "info",
            f"Removed faction for {removed_user['user_name']} ({user_id}) from cache",
            label="🛡️  Faction CACHE",
        )
    else:
        pretty_log(
            "info",
            f"Attempted to remove non-existent user_id {user_id} from faction cache.",
            label="🛡️  Faction CACHE",
        )

def get_user_id_by_name(user_name: str) -> int | None:
    """Get a user's ID from cache by their name."""
    for user_id, data in faction_cache.items():
        if data.get("user_name") == user_name:
            return user_id
    return None

def get_user_faction_cache_by_username(user_name: str) -> str | None:
    """Get a user's faction from cache by their name."""
    for data in faction_cache.values():
        if data.get("user_name") == user_name:
            return data.get("faction")
    return None