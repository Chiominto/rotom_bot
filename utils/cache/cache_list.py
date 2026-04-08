from utils.logs.pretty_log import pretty_log
# 🔮────────────────────────────────────────────
#        ⚡ Processed ids Cache
# 👻────────────────────────────────────────────
processed_faction_ball_alerts = set()
LIST_OF_PROCESSED_IDS = [
    processed_faction_ball_alerts,
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
