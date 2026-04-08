import discord
from discord.ext import commands

from constants.celestial_constants import (
    CC_SERVER_ID,
    CELESTIAL_TEXT_CHANNELS,
    POKEMEOW_APPLICATION_ID,

)
from utils.logs.pretty_log import pretty_log
from utils.listener_func.faction_ball_alert import faction_ball_alert
from utils.listener_func.faction_ball_listener import extract_faction_ball_from_daily, extract_faction_ball_from_fa
FACTIONS = ["aqua", "flare", "galactic", "magma", "plasma", "rocket", "skull", "yell"]

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
            if (
                first_embed.title
                and "daily streak" in first_embed.title.lower()
            ):
                pretty_log(
                    "info",
                    f"Matched Daily Faction Ball Listener | Message ID: {message.id} | Channel: {message.channel.name}",
                )
                await extract_faction_ball_from_daily(
                    bot=self.bot, message=message
                )
        # ————————————————————————————————
        # ⚡ Faction Command Faction Ball Extraction
        # ————————————————————————————————
        if first_embed:
            if first_embed.author and any(
                f in first_embed.author.name.lower() for f in FACTIONS
            ):
                await extract_faction_ball_from_fa(
                    bot=self.bot, message=message
                )

# 🟣────────────────────────────────────────────
#         ⚡ Setup Function
# 🟣────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCreateListener(bot))
