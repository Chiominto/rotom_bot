import discord
from discord.ext import commands

from constants.celestial_constants import (
    CC_SERVER_ID,
    CELESTIAL_TEXT_CHANNELS,
    POKEMEOW_APPLICATION_ID,
)
from utils.listener_func.bud_ev_listener import handle_pokemeow_embed_sync
from utils.listener_func.ev_tracker_listener import handle_pokemeow_battle_message
from utils.listener_func.faction_ball_alert import faction_ball_alert
from utils.listener_func.faction_ball_listener import (
    extract_faction_ball_from_daily,
    extract_faction_ball_from_fa,
)
from utils.listener_func.egg_alert_listener import egg_ready_to_hatch_listener, egg_hatched_listener
from utils.logs.pretty_log import pretty_log
from utils.listener_func.market_view_listener import market_view_listener
from utils.listener_func.wb_reg_listener import register_wb_battle_reminder
from utils.listener_func.berry_listener import berry_listener
from utils.listener_func.berry_water_listener import (
    handle_berry_water_message,
    handle_mulch_message,
)
from utils.listener_func.held_item_ping import held_item_ping_handler

FACTIONS = ["aqua", "flare", "galactic", "magma", "plasma", "rocket", "skull", "yell"]

triggers = {"bud_info_trigger": "**Level**:", "ev_training": "won the battle"}


# 🟣────────────────────────────────────────────
#         💤 Message Create Listener Cog
# 🟣────────────────────────────────────────────
class MessageCreateListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🟣────────────────────────────────────────────
    #         💤 Message Listener Event
    # 🟣────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # ————————————————————————————————
        # 🏰 Guild Check — Route by server
        # ————————————————————————————————
        guild = message.guild
        if not guild:
            return  # Skip DMs

        # ————————————————————————————————
        # 💤 Message Variables
        # ————————————————————————————————
        content = message.content
        first_embed = message.embeds[0] if message.embeds else None
        first_embed_author = (
            first_embed.author.name if first_embed and first_embed.author else ""
        )
        first_embed_description = (
            first_embed.description if first_embed and first_embed.description else ""
        )
        first_embed_footer = (
            first_embed.footer.text if first_embed and first_embed.footer else ""
        )
        first_embed_title = (
            first_embed.title if first_embed and first_embed.title else ""
        )

        # ————————————————————————————————
        # 🏰 Ignore non-PokéMeow bot messages
        # ————————————————————————————————
        # 🚫 Ignore all bots except PokéMeow to prevent loops
        if (
            message.author.bot
            and message.author.id != POKEMEOW_APPLICATION_ID
            and not message.webhook_id
        ):
            return
        # ————————————————————————————————
        # ⚡ Faction Ball Alert
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed.description
                and "<:team_logo:" in first_embed.description
                and "found a wild" in first_embed.description
            ):
                await faction_ball_alert(bot=self.bot, before=message, after=message)
        # ————————————————————————————————
        # ⚡ Daily Command Faction Ball Extraction
        # ————————————————————————————————
        if first_embed:
            if first_embed.title and "daily streak" in first_embed.title.lower():
                pretty_log(
                    "info",
                    f"Matched Daily Faction Ball Listener | Message ID: {message.id} | Channel: {message.channel.name}",
                )
                await extract_faction_ball_from_daily(bot=self.bot, message=message)
        # ————————————————————————————————
        # ⚡ Faction Command Faction Ball Extraction
        # ————————————————————————————————
        if first_embed:
            if first_embed.author and any(
                f in first_embed.author.name.lower() for f in FACTIONS
            ):
                await extract_faction_ball_from_fa(bot=self.bot, message=message)
        # ————————————————————————————————
        # ⚡ EV Training Listener
        # ————————————————————————————————
        if content and triggers["ev_training"] in content:
            pretty_log(
                "info",
                f"Matched EV Training Listener | Message ID: {message.id} | Channel: {message.channel.name}",
            )
            try:
                await handle_pokemeow_battle_message(bot=self.bot, message=message)
            except Exception as e:
                pretty_log(
                    "error",
                    f"Error in EV Training Listener for message {message.id}: {e}",
                )

        # ————————————————————————————————
        # ⚡ EV Tracker Bud Info
        # ————————————————————————————————
        if (
            first_embed_description
            and triggers["bud_info_trigger"] in first_embed_description
        ):
            pretty_log(
                "info",
                f"Matched EV Tracker Bud Info Listener | Message ID: {message.id} | Channel: {message.channel.name}",
            )
            try:
                await handle_pokemeow_embed_sync(bot=self.bot, message=message)
            except Exception as e:
                pretty_log(
                    "error",
                    f"Error in EV Tracker Bud Info Listener for message {message.id}: {e}",
                )

        # ————————————————————————————————
        # ⚡ MARKET VIEW LISTENER
        # ————————————————————————————————
        if (
            first_embed
            and "PokeMeow Global Market" in first_embed_author
            and not "Recent" in first_embed_author
            and not "Rarity" in first_embed_author
        ):
            pretty_log(
                tag="info",
                message=f"Processing market view message with embed author: {first_embed_author}",
            )
            await market_view_listener(self.bot, message)

        # ————————————————————————————————
        # ⚡ Egg Ready to Hatch LISTENER
        # ————————————————————————————————
        if message.content and message.author.id == POKEMEOW_APPLICATION_ID:
            if (
                "your egg is ready to hatch! `/egg hatch` to hatch it."
                in message.content
            ):
                await egg_ready_to_hatch_listener(bot=self.bot, message=message)
        # ————————————————————————————————
        # ⚡ Egg Hatched LISTENER
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_footer
                and "PokeMeow | Egg Hatch" in first_embed.footer.text
            ):
                pretty_log(
                    "info",
                    f"🔹 Matched Egg Hatched Listener | message_id={message.id}",
                )
                await egg_hatched_listener(bot=self.bot, message=message)

        # ————————————————————————————————
        # ⚡ Berry Listener
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_description
                and "garden overview" in first_embed_description.lower()
            ):
                pretty_log(
                    "info",
                    "Detected Garden Overview embed, processing berry reminders...",
                )
                await berry_listener(
                    bot=self.bot,
                    before_message=message,
                    message=message,
                )

        # ————————————————————————————————
        # ⚡ Berry Water Listener
        # ————————————————————————————————
        if message.content:
            if "Watered" in message.content and "Next stage" in message.content:
                pretty_log(
                    "info",
                    "Detected Berry Water message, processing berry water reminders...",
                )
                await handle_berry_water_message(bot=self.bot, message=message)

        # ————————————————————————————————
        # ⚡ Berry Mulch Listener
        # ————————————————————————————————
        if message.content:
            if (
                "Applied" in message.content
                and "Mulch" in message.content
                and "to Slot" in message.content
            ):
                pretty_log(
                    "info",
                    "Detected Mulch message, processing growth mulch reminders...",
                )
                await handle_mulch_message(bot=self.bot, message=message)

        # ————————————————————————————————
        # ⚡ WB Battle Reminder Registration Listener
        # ————————————————————————————————
        if first_embed:
            if first_embed_description:
                if (
                    "<:checkedbox:752302633141665812> You are registered for this fight"
                    in first_embed_description
                    and ";wb fight" in first_embed_description
                ):
                    await register_wb_battle_reminder(
                        bot=self.bot, message=message
                    )
        # ————————————————————————————————
        # ⚡ Held Item Ping Listener
        # ————————————————————————————————
        if (
            first_embed_description
            and "<:held_item:" in first_embed_description
        ):
            await held_item_ping_handler(self.bot, message)
            
# 🟣────────────────────────────────────────────
#         ⚡ Setup Function
# 🟣────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCreateListener(bot))
