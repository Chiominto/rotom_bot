import discord
from discord.ext import commands

from constants.celestial_constants import CC_SERVER_ID, POKEMEOW_APPLICATION_ID
from utils.logs.pretty_log import pretty_log
from utils.listener_func.faction_ball_alert import faction_ball_alert
from utils.listener_func.berry_listener import berry_listener
from utils.listener_func.berry_pouch_listener import handle_berry_pouch_message
from utils.listener_func.pokemon_caught_listener import pokemon_caught_listener
from utils.listener_func.wb_reg_listener import handle_wb_register_command

FISHING_COLOR = 0x87CEFA

# 🟣────────────────────────────────────────────
#         💤 Message Edit Listener Cog
# 🟣────────────────────────────────────────────
class OnMessageEditCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🟣────────────────────────────────────────────
    #         💤 Message Listener Event
    # 🟣────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        # ————————————————————————————————
        # 🏰 Guild Check — Route by server
        # ————————————————————————————————
        guild = after.guild
        if not guild:
            return  # Skip DMs

        # ————————————————————————————————
        # 💤 Message Variables
        # ————————————————————————————————
        content = after.content
        first_embed = after.embeds[0] if after.embeds else None
        first_embed_author = (
            first_embed.author.name if first_embed and first_embed.author else ""
        )
        first_embed_description = (
            first_embed.description if first_embed and first_embed.description else ""
        )
        first_embed_footer_text = (
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
            after.author.bot
            and after.author.id != POKEMEOW_APPLICATION_ID
            and not after.webhook_id
        ):
            return
        # ————————————————————————————————
        # ⚡ Pokemon Caught Listener
        # ————————————————————————————————
        # Process Pokemon or fish caught for Weekly Goal Tracker
        if after.embeds:
            embed_description = after.embeds[0].description or ""
            if embed_description and "You caught a" in embed_description:
                await pokemon_caught_listener(
                    bot=self.bot, before_message=before, message=after
                )
        # ————————————————————————————————
        # ⚡ Faction Ball Alert
        # ————————————————————————————————
        if after.embeds:
            desc = after.embeds[0].description
            color = after.embeds[0].color
            if (
                desc
                and "<:team_logo:" in desc
                and "fished a wild" in desc
                and (
                    color == FISHING_COLOR
                    or getattr(color, "value", None) == FISHING_COLOR
                )
            ):
                """pretty_log(
                    "info",
                    f"Detected faction ball alert in fish embed",
                    label="🛡️ FACTION BALL ALERT",
                    bot=self.bot,
                )"""
                await faction_ball_alert(bot=self.bot, before=before, after=after)
        # ————————————————————————————————
        # ⚡ Berry Command Listener
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
                    before_message=before,
                    message=after,
                )
        # ————————————————————————————————
        # ⚡ Berry Pouch Listener
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_footer_text
                and "berry pouch" in first_embed_footer_text.lower()
            ):
                pretty_log(
                    "info",
                    "Detected Berry Pouch embed, processing berry pouch listener...",
                )
                await handle_berry_pouch_message(
                    bot=self.bot,
                    before=before,
                    message=after,
                )
        # ————————————————————————————————
        # ⚡ WB Battle Reminder Registration Listener
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_description
                and "<:checkedbox:752302633141665812> Successfully registered your"
                in first_embed_description
                and first_embed.title
                and "**A World Boss has spawned! Register now!**" in first_embed.title
            ):
                pretty_log(
                    "info",
                    f"Matched World Boss Battle Reminder Registration Confirmation | Message ID: {after.id} | Channel: {after.channel.name}",
                )
                await handle_wb_register_command(
                    bot=self.bot, before_message=before, message=after
                )

# 🟣────────────────────────────────────────────
#         💤 Setup Function
# 🟣────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageEditCog(bot))
