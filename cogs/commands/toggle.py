# 🟣────────────────────────────────────────────
#           💜 Toggle Command Group 💜
# ─────────────────────────────────────────────
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from group_command_func.toggle import *

from utils.functions.command_safe import run_command_safe


# 🟣────────────────────────────────────────────
#     💜 Toggle Command Group Cog Setup 💜
# ─────────────────────────────────────────────
class ToggleGroup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🟣────────────────────────────────────────────
    #    💜 Toggle Top Level Command Group 💜
    # 🟣────────────────────────────────────────────
    toggle_group = app_commands.Group(name="toggle", description="Toggle Command Group")

    # 🟣────────────────────────────────────────────
    #     💜 /toggle alerts 💜
    # 🟣────────────────────────────────────────────
    @toggle_group.command(
        name="alerts",
        description="Modifies your alerts' settings",
    )
    async def toggle_alerts(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "toggle alerts"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=alert_settings_func,
        )

    toggle_alerts.extras = {"category": "Public"}

    # 🟣────────────────────────────────────────────
    #     💜 /toggle timers
    # 🟣────────────────────────────────────────────
    @toggle_group.command(
        name="timers",
        description="Modifies your timers' settings",
    )
    async def toggle_timers(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "toggle timers"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=timer_settings_func,
        )
    toggle_timers.extras = {"category": "Public"}


# 🟣────────────────────────────────────────────
#           💜 Cog Setup Function 💜
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = ToggleGroup(bot)
    await bot.add_cog(cog)
