import re
from email.mime import message

import discord
from discord.ext import commands

from constants.celestial_constants import CC_SERVER_ID, POKEMEOW_APPLICATION_ID
from utils.listener_func.berry_listener import berry_listener
from utils.listener_func.berry_pouch_listener import handle_berry_pouch_message
from utils.listener_func.explore_caught_listener import explore_caught_listener
from utils.listener_func.faction_ball_alert import faction_ball_alert
from utils.listener_func.fish_timer import fish_timer_handler
from utils.listener_func.monthly_stats_listener import monthly_stats_listener
from utils.listener_func.pin_timer_listener import pin_timer_listener
from utils.listener_func.pokemon_caught_listener import pokemon_caught_listener
from utils.listener_func.pokemon_pin_numbers_listener import \
    pokemon_pin_numbers_listener
from utils.listener_func.wb_reg_listener import handle_wb_register_command
from utils.listener_func.weekly_stats_listener import weekly_stats_listener
from utils.logs.pretty_log import pretty_log


def get_number_after_exclamation(text):
    match = re.search(r'!\s*(\d+)', text)
    return match.group(1) if match else None
FISHING_COLOR = 0x87CEFA
# ️────────────────────────────────────────────
#        ⚔️ Message Triggers
# ️────────────────────────────────────────────
triggers = {
    "weekly_stats_command": "**Clan Weekly Stats — Celestial**",
    "monthly_stats_command": "**Clan Monthly Stats — Celestial**",
    "explore_listener": ":stopwatch: Your explore session has ended!",
    "caught_listener": "You caught a",
}


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
        # ⚡ Fish Timer
        # ————————————————————————————————
        if (
            first_embed_description
            and "cast a" in first_embed_description
            and "into the water" in first_embed_description
        ):
            await fish_timer_handler(after)

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
        # ⚡ Fish Pin Alert
        # ————————————————————————————————
        if after.embeds:
           if first_embed_author and "a wild pokemon appeared" in first_embed_author.lower():
               pin_number = get_number_after_exclamation(first_embed_author)
               if pin_number:
                   await pokemon_pin_numbers_listener(
                       bot=self.bot,
                       message=after,
                       pin_number=pin_number,
                       source="fish",
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
        # 🩵 Weekly Stats Listener
        # ————————————————————————————————
        if first_embed:
            if triggers["weekly_stats_command"] in first_embed_title:
                await weekly_stats_listener(self.bot, before, after)
        # ————————————————————————————————
        # 🩵 Monthly Stats Listener
        # ————————————————————————————————
        if first_embed:
            if triggers["monthly_stats_command"] in first_embed_title:
                await monthly_stats_listener(self.bot, before, after)

        # ————————————————————————————————
        # 🩵 Explore Caught Listener
        # ————————————————————————————————
        if content:
            if triggers["explore_listener"] in content:
                await explore_caught_listener(self.bot, before, after)

        # ————————————————————————————————
        # ⚡ Berry Command Listener
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_description
                and "garden overview" in first_embed_description.lower()
            ):
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
                await handle_wb_register_command(
                    bot=self.bot, before_message=before, message=after
                )
        # ————————————————————————————————
        # ⚡ Safari Zone Pin Alert Listener
        # ————————————————————————————————
        if first_embed:
            if first_embed_footer_text and "use a safari ball to catch it" in first_embed_footer_text.lower():
                if first_embed_author:
                    pin_number = get_number_after_exclamation(first_embed_author)
                    if pin_number:
                        await pokemon_pin_numbers_listener(
                            bot=self.bot,
                            message=after,
                            pin_number=pin_number,
                            source="safari",
                        )
        # ————————————————————————————————
        # ⚡ Missing Number Quest Timer
        # ————————————————————————————————
        if first_embed:
            if first_embed_title and "the missing numbers" in first_embed_title.lower():
                if first_embed_description and "you can submit another pin" in first_embed_description.lower():
                    pretty_log(tag="info", message=f"Missing Number Quest Timer triggered in {after.channel.name}")
                    await pin_timer_listener(
                        bot=self.bot,
                        message=after,
                    )

# 🟣────────────────────────────────────────────
#         💤 Setup Function
# 🟣────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageEditCog(bot))
