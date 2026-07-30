from utils.logs.pretty_log import pretty_log

# 🔮────────────────────────────────────────────
#        ⚡ Processed ids Cache
# 👻────────────────────────────────────────────
processed_faction_ball_alerts = set()
processed_caught_messages = set()
not_weakness_chart_user_names = set()
processed_weakness_messages: set[int] = set()
processed_explore_messages = set()
processed_weekly_stats_messages = set()
processed_monthly_stats_messages = set()

LIST_OF_PROCESSED_IDS = [
    processed_faction_ball_alerts,
    processed_caught_messages,
    processed_weakness_messages,
    processed_explore_messages,
    processed_weekly_stats_messages,
    processed_monthly_stats_messages,
]


def clear_processed_ids_cache():
    for id_set in LIST_OF_PROCESSED_IDS:
        id_set.clear()
    pretty_log("cache", "✅ Cleared all processed IDs caches.")


# 🔮────────────────────────────────────────────
#        ⚡ Webhook Url Cache
# 👻────────────────────────────────────────────
webhook_url_cache: dict[tuple[int, int], dict[str, str]] = {}
#     ...
#
# }
# key = (bot_id, channel_id)
# Structure:
# webhook_url_cache = {
# (bot_id, channel_id): {
#     "url": "https://discord.com/api/webhooks/..."
#     "channel_name": "alerts-channel",
# },
# 🔮────────────────────────────────────────────
#        ⚡ Pokemon Cache
# 👻────────────────────────────────────────────
pokemon_cache: dict[str, dict[str, str | int]] = {}
#     ...
#
# }
# Structure:
# pokemon_cache = {
# "pokemon_name": {
#     "dex_number": int,
#     "rarity": str,
#     "current_listing": int,
#     "lowest_market": int,
#     "true_lowest": int,
#     "listing_seen": str,
#     "emoji_id": str,
#     "image_link": str,
#     "last_updated": datetime
# },

# 🔮────────────────────────────────────────────
#        ⚡ Daily Faction Ball Cache
# 👻────────────────────────────────────────────
daily_faction_ball_cache: dict[str, str | None] = {}
# Structure:
# daily_faction_ball_cache = {
#     "aqua": "Some Value or None",
#     "flare": "Some Value or None",
#     "galactic": None,
#     "magma": "Some Value or None",
#     "plasma": None,
#     "rocket": "Some Value or None",
#     "skull": None,
#     "yell": "Some Value or None"
# }

# 🔮────────────────────────────────────────────
#        ⚡ Faction Ball Alert Cache
# 👻────────────────────────────────────────────
faction_ball_alert_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "notify": str
# }
# 🔮────────────────────────────────────────────
#        ⚡ Factions Cache
# 👻────────────────────────────────────────────
faction_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "faction": str
# }

# 🔮────────────────────────────────────────────
#        ⚡ WB Alert Cache
# 👻────────────────────────────────────────────
wb_battle_alert_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "notify": str
# }


# 🔮────────────────────────────────────────────
#        ⚡ Egg Alert Cache
# 👻────────────────────────────────────────────
egg_alert_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "notify": str
# }

# 🔮────────────────────────────────────────────
#        ⚡ Item Alert Cache
# 👻────────────────────────────────────────────
item_alert_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "notify": str
# }
# 🔮────────────────────────────────────────────
#        ⚡ EV Tracker Cache
# 👻────────────────────────────────────────────
ev_tracker_cache: dict[int, dict] = {}
# user_id -> {"user_name": str, "pokemon": str, "dex_number": int, "evs": dict, "goals": dict}
# Structure
# {
#   user_id: {
#       "user_name": str,
#       "pokemon": str,
#       "dex_number": int,
#        "emoji_id": str,
#       "evs": {
#           "hp": int,
#           "atk": int,
#           "def": int,
#           "spa": int,
#           "spd": int,
#           "spe": int,
#       },
#       "goals": {
#           "hp": int,
#           "atk": int,
#           "def": int,
#           "spa": int,
#           "spd": int,
#           "spe": int,
#       },
#   }


# 🧩────────────────────────────────────────────
#        ⚡ Pokémon List Cache
# 🧩────────────────────────────────────────────
pokemon_list_cache: dict[str, int] = {}
# Structure:
# pokemon_list_cache = {
#     "pokemon_name": "dex_number",
#     }

# 🧩────────────────────────────────────────────
#        ⚡ Celestial Members Cache
# 🧩────────────────────────────────────────────
celestial_members_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "pokemeow_name": str,
#   "channel_id": int
#   "actual_perks": str
#   "clan_bank_donation": int
#   "clan_treasury_doantion": int
#   "date_joined": int
# }

# 🧩────────────────────────────────────────────
#        ⚡ Username List Cache
# 🧩────────────────────────────────────────────
timer_users: dict[str, int] = {}
# user_name : user_id
# 🧩────────────────────────────────────────────
#        ⚡ Timers Cache
# 🧩────────────────────────────────────────────
timer_cache: dict[int, dict[str, str]] = {}
# Structure:
# {
#   user_id: {
#     "user_name": str,
#     "pokemon_setting": str,
#     "fish_setting": str,
#     "battle_setting": str
#   },
#   ...


not_battle_timer_user_cache: set[str] = set()
battle_timer_users_cache: dict[str, str] = {}

# Structure:
# battle_timer_users_cache = {
#    "user_name" : str,
#    ...
# }

# 🔮────────────────────────────────────────────
#        ⚡ Utility Cache
# 👻────────────────────────────────────────────
utility_cache: dict[int, dict[str, str | dict[str, str]]] = {}
# Structure:
# {
#   user_id: {
#     "user_name": str,
#     "utilities": {
#       "weakness_chart": str,
#       "fossil_alert": str,
#       ...
#     }
#   },

# 🔮────────────────────────────────────────────
#        ⚡ Research Fossil Alert Cache
# 👻────────────────────────────────────────────
research_fossil_alert_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "notify": str
# }

# 💫━━━━━━━━━━━━━━━━━━━━━━━━━
#       🌸 Weakness Data Cache 🌸
# 💫━━━━━━━━━━━━━━━━━━━━━━━━━
weakness_data_cache: dict[str, dict] = {}
# Structure:
# {
#   pokemon_name: {
# "title": str,
# "description": str,
# "note": str,
# "footer": str,
# "color": int,
#   },
# 💫━━━━━━━━━━━━━━━━━━━━━━━━━
#       🌸 Weekly Goal Cache 🌸
# 💫━━━━━━━━━━━━━━━━━━━━━━━━━
weekly_goal_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "pokemon_caught": int,
#   "fish_caught": int,
#   "battles_won": int,
#   "channel_id": int,
#   "weekly_requirement_mark": bool,
# }
# 💫━━━━━━━━━━━━━━━━━━━━━━━━━
#       🌸 Monthly Goal Cache 🌸
# 💫━━━━━━━━━━━━━━━━━━━━━━━━━
monthly_goal_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "pokemon_caught": int,
#   "fish_caught": int,
#   "battles_won": int,
#   "channel_id": int,
#   "monthly_requirement_mark": bool,
# }
