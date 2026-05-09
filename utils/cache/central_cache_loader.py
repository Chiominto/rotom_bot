import discord

from utils.logs.pretty_log import pretty_log

from .pokemon_cache import load_pokemon_cache

from .webhook_url_cache import load_webhook_url_cache
from .daily_fa_ball_cache import load_daily_faction_ball_cache
from .faction_ball_alert_cache import load_faction_ball_alert_cache
from .wb_battle_alert_cache import load_wb_battle_alert_cache
from .faction_cache import load_faction_cache
from .ev_tracker_cache import load_ev_tracker_cache
from .egg_alert_cache import load_egg_alert_cache
from .item_alert_cache import load_item_alert_cache
from .celestial_members_cache import load_celestial_members_cache
from .timers_cache import load_timer_cache
from .utilities_cache import load_utility_cache
from .research_fossil_alert_cache import load_research_fossil_alert_cache

async def load_all_cache(bot: discord.Client):
    """
    Loads all caches used by the bot.
    """
    try:

        # Load Pokémon Cache
        await load_pokemon_cache(bot)

        # Load Webhook URL Cache
        await load_webhook_url_cache(bot)

        # Load Celestial Members Cache
        await load_celestial_members_cache(bot)

        # Load Timer Settings Cache
        await load_timer_cache(bot)

        # Load Faction Cache
        await load_faction_cache(bot)

        # Load Daily Faction Ball Cache
        await load_daily_faction_ball_cache(bot)

        # Load Faction Ball Alert Cache
        await load_faction_ball_alert_cache(bot)

        # Load World Boss Battle Alert Cache
        await load_wb_battle_alert_cache(bot)

        # Load EV Tracker Cache
        await load_ev_tracker_cache(bot)

        # Egg Alert Cache
        await load_egg_alert_cache(bot)

        # Item Alert Cache
        await load_item_alert_cache(bot)

        # Load Research Fossil Alert Cache
        await load_research_fossil_alert_cache(bot)

        # Load Utility Cache
        try:
            await load_utility_cache(bot)
        except Exception as util_e:
            pretty_log(
                message=f"⚠️ Utility cache failed to load: {util_e}",
                tag="cache",
            )

    except Exception as e:
        pretty_log(
            message=f"❌ Error loading caches: {e}",
            tag="cache",
        )
        return
    pretty_log(
        message="✅ All caches loaded successfully.",
        tag="cache",
    )
