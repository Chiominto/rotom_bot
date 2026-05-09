import discord

from utils.db.utilities_db import fetch_all_utility_settings
from utils.logs.pretty_log import pretty_log

from .cache_list import utility_cache, weakness_data_cache


async def load_utility_cache(bot: discord.Client):
    utility_settings = await fetch_all_utility_settings(bot)
    utility_cache.clear()
    for setting in utility_settings:
        user_id = setting["user_id"]
        if user_id not in utility_cache:
            utility_cache[user_id] = {
                "user_name": setting["user_name"],
                "utilities": {},
            }
        utility_cache[user_id]["utilities"][setting["utility_type"]] = setting[
            "setting"
        ]

def upsert_utility_setting_cache(
    user_id: int, user_name: str, utility_type: str, setting: str
):
    if user_id not in utility_cache:
        utility_cache[user_id] = {
            "user_name": user_name,
            "utilities": {},
        }
    utility_cache[user_id]["utilities"][utility_type] = setting

def fetch_user_utility_setting_cache(user_id: int, utility_type: str) -> str | None:
    user_cache = utility_cache.get(user_id)
    if user_cache:
        return user_cache["utilities"].get(utility_type)
    return None

def fetch_user_utility_setting_cache_by_user_name(user_name: str, utility_type: str) -> str | None:
    for user_id, user_cache in utility_cache.items():
        if user_cache["user_name"] == user_name:
            return user_cache["utilities"].get(utility_type)
    return None

def fetch_user_utility_type_setting_cache(user_id: int, utility_type: str) -> str | None:
    user_cache = utility_cache.get(user_id)
    if user_cache:
        return user_cache["utilities"].get(utility_type)
    return None


def _normalize_pokemon_cache_key(pokemon_name: str) -> str:
    """Return a canonical key so cache lookups are case/space-insensitive."""
    return pokemon_name.strip().lower()


def upsert_weakness_data_cache(
    pokemon_name: str, title: str, description: str, note: str, footer: str, color
):
    """Insert or update weakness data for a Pokemon in the cache."""
    cache_key = _normalize_pokemon_cache_key(pokemon_name)
    weakness_data_cache[cache_key] = {
        "title": title,
        "description": description,
        "note": note,
        "footer": footer,
        "color": color,
    }
    pretty_log(
        tag="",
        label="🌸 WEAKNESS DATA CACHE",
        message=f"Upserted weakness data for '{pokemon_name}' into cache (cache now {len(weakness_data_cache)} entries)",

    )


def get_weakness_data(pokemon_name: str) -> dict[str, str] | None:
    """Get weakness data for a Pokemon from the cache, or None if not found."""
    cache_key = _normalize_pokemon_cache_key(pokemon_name)
    return weakness_data_cache.get(cache_key)
