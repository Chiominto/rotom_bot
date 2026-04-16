import discord
from discord import ButtonStyle
from discord.ext import commands

from utils.db.faction_ball_alert_db_func import (
    fetch_user_faction_ball_alert,
    upsert_user_faction_ball_alert,
)
from utils.db.egg_alert_db_func import (
    fetch_user_egg_alert,
    upsert_user_egg_alert,
)
from utils.db.item_alert_db_func import (
    upsert_user_item_alert,
    fetch_user_item_alert,
)
from utils.db.wb_fight_db import fetch_user_wb_battle_alert, upsert_user_wb_battle_alert
from utils.functions.safe_response import safe_respond
from utils.logs.pretty_log import pretty_log
from constants.celestial_constants import CELESTIAL_EMOJIS
from constants.aesthetics import Emojis
# 💗────────────────────────────────────────────
# [🎀 FUNCTION] Alert Settings
# 💗────────────────────────────────────────────
async def alert_settings_func(bot: commands.Bot, interaction: discord.Interaction):
    """Main entry for user alert settings."""
    try:
        await interaction.response.defer()  # Defer immediately
        wb_battle_alert = await fetch_user_wb_battle_alert(bot, interaction.user.id)
        faction_ball_alert = await fetch_user_faction_ball_alert(
            bot, interaction.user.id
        )
        egg_alert = await fetch_user_egg_alert(bot, interaction.user.id)
        item_alert = await fetch_user_item_alert(bot, interaction.user.id)

        faction_ball_alert = faction_ball_alert or {"notify": "off"}
        wb_battle_alert = wb_battle_alert or {"notify": "off"}
        egg_alert = egg_alert or {"notify": "off"}
        item_alert = item_alert or {"notify": "off"}

        view = AlertSettingsView(
            bot,
            interaction.user,
            faction_ball_alert,
            wb_battle_alert,
            egg_alert=egg_alert,
            item_alert=item_alert,
        )

        message = await interaction.followup.send(
            content="Modify your Alert Settings:", view=view, ephemeral=True
        )
        view.message = message

        pretty_log(
            "ui",
            f"[Alert Settings] Displayed alert settings for {interaction.user.display_name}",
        )

    except Exception as e:
        pretty_log("error", f"Failed to load alert settings: {e}")
        await interaction.followup.send(
            content="⚠️ An error occurred while loading your alert settings.",
            ephemeral=True,
        )

# 💗────────────────────────────────────────────
# [🌸 VIEW CLASS] Alert Settings View (patched)
# 💗────────────────────────────────────────────
class AlertSettingsView(discord.ui.View):
    def __init__(
        self,
        bot: commands.Bot,
        user: discord.Member,
        faction_ball_alert,
        wb_battle_alert,
        egg_alert,
        item_alert,
    ):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.faction_ball_alert = faction_ball_alert
        self.wb_battle_alert = wb_battle_alert
        self.egg_alert = egg_alert
        self.item_alert = item_alert
        self.message = None  # set later
        self.update_button_styles()

    # 💫────────────────────────────────────
    # [🎯 BUTTON] Faction Ball Alert (4-State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="Faction Ball Alert: OFF", style=ButtonStyle.secondary, emoji="🎯"
    )
    async def faction_ball_alert_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        try:
            current_state = (
                str(self.faction_ball_alert.get("notify", "off")).lower()
                if self.faction_ball_alert
                else "off"
            )

            # 🔹 4-State Cycle: off → on → on_no_pings → react → off
            if current_state == "off":
                new_state = "on"
            elif current_state == "on":
                new_state = "on_no_pings"
            elif current_state == "on_no_pings":
                new_state = "react"
            else:  # react or any other state
                new_state = "off"

            await upsert_user_faction_ball_alert(self.bot, self.user, new_state)
            self.faction_ball_alert = {"notify": new_state}

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = {
                "off": "Off",
                "on": "On",
                "on_no_pings": "On (No Pings)",
                "react": "React",
            }.get(new_state, "OFF")

            await interaction.edit_original_response(
                content=f"Modify your Alert Settings:\n🎯 Faction Ball Alert set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set Faction Ball Alert to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling Faction Ball Alert: {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "⚠️ An error occurred while updating Faction Ball Alert.",
                ephemeral=True,
            )

    # 💫────────────────────────────────────
    # [🎯 BUTTON] WB Battle Alert (2-State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="World Boss Battle Alert: OFF",
        style=ButtonStyle.secondary,
        emoji=Emojis.wb_spawn,
    )
    async def wb_battle_alert_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        try:
            current_state = (
                str(self.wb_battle_alert.get("notify", "off")).lower()
                if self.wb_battle_alert
                else "off"
            )

            # 🔹 2-State Cycle: off → on → off
            new_state = "on" if current_state == "off" else "off"

            await upsert_user_wb_battle_alert(self.bot, self.user, new_state)
            self.wb_battle_alert = {"notify": new_state}

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = "ON" if new_state == "on" else "OFF"

            await interaction.edit_original_response(
                content=f"Modify your World Boss Battle Alert Settings:\n🛡️ World Boss Battle Alert set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set World Boss Battle Alert to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling World Boss Battle Alert: {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "⚠️ An error occurred while updating World Boss Battle Alert.",
                ephemeral=True,
            )
    # 💫────────────────────────────────────
    # [🥚 BUTTON] Egg Hatch/Hold Alert (3 -State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="Egg Hatch/Hold Alert: OFF",
        style=ButtonStyle.secondary,
        emoji="🥚",
    )
    async def egg_alert_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        try:
            current_state = (
                str(self.egg_alert.get("notify", "off")).lower()
                if self.egg_alert
                else "off"
            )

            # 🔹 3-State Cycle: off → on → on_no_pings → off
            if current_state == "off":
                new_state = "on"
            elif current_state == "on":
                new_state = "on_no_pings"
            else:  # react or any other state
                new_state = "off"

            await upsert_user_egg_alert(self.bot, self.user, new_state)
            self.egg_alert = {"notify": new_state}

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = {
                "off": "OFF",
                "on": "ON",
                "on_no_pings": "ON (No Pings)",
            }.get(new_state, "OFF")

            await interaction.edit_original_response(
                content=f"Modify your Alert Settings:\n🥚 Egg Hatch/Hold Alert set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set Egg Hatch/Hold Alert to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling Egg Hatch/Hold Alert: {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "⚠️ An error occurred while updating Egg Hatch/Hold Alert.",
                ephemeral=True,
            )
    # 💫────────────────────────────────────
    # [🛡️ BUTTON] Item Alert (3-State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="Item Alert: OFF",
        style=ButtonStyle.secondary,
        emoji=Emojis.held_item,
    )
    async def item_alert_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        try:
            current_state = (
                str(self.item_alert.get("notify", "off")).lower()
                if self.item_alert
                else "off"
            )

            # 🔹 3-State Cycle: off → on → on_no_pings → off
            if current_state == "off":
                new_state = "on"
            elif current_state == "on":
                new_state = "on_no_pings"
            else:  # react or any other state
                new_state = "off"

            await upsert_user_item_alert(self.bot, self.user, new_state)
            self.item_alert = {"notify": new_state}

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = {
                "off": "OFF",
                "on": "ON",
                "on_no_pings": "ON (No Pings)",
            }.get(new_state, "OFF")

            await interaction.edit_original_response(
                content=f"Modify your Alert Settings:\n{Emojis.held_item} Item Alert set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set Item Alert to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling Item Alert: {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "⚠️ An error occurred while updating Item Alert.",
                ephemeral=True,
            )
    # 💫────────────────────────────────────
    # [🎨 STYLE UPDATE FUNCTION]
    # 💫────────────────────────────────────
    def update_button_styles(self):

        # 🎯 Faction Ball Alert Button (4 states)
        faction_ball_alert_state = (
            str(self.faction_ball_alert.get("notify", "off")).lower()
            if self.faction_ball_alert
            else "off"
        )

        if faction_ball_alert_state == "off":
            self.faction_ball_alert_button.style = ButtonStyle.secondary
            self.faction_ball_alert_button.label = "Faction Ball Alert: OFF"
        elif faction_ball_alert_state == "on":
            self.faction_ball_alert_button.style = ButtonStyle.success
            self.faction_ball_alert_button.label = "Faction Ball Alert: ON"
        elif faction_ball_alert_state == "on_no_pings":
            self.faction_ball_alert_button.style = ButtonStyle.primary
            self.faction_ball_alert_button.label = "Faction Ball Alert: ON (No Pings)"
        elif faction_ball_alert_state == "react":
            self.faction_ball_alert_button.style = ButtonStyle.danger
            self.faction_ball_alert_button.label = "Faction Ball Alert: REACT"
        else:
            self.faction_ball_alert_button.style = ButtonStyle.secondary
            self.faction_ball_alert_button.label = "Faction Ball Alert: OFF"

        # 🛡️ WB Battle Alert Button (2 states)
        wb_battle_alert_state = (
            str(self.wb_battle_alert.get("notify", "off")).lower()
            if self.wb_battle_alert
            else "off"
        )
        if wb_battle_alert_state == "off":
            self.wb_battle_alert_button.style = ButtonStyle.secondary
            self.wb_battle_alert_button.label = "World Boss Battle Alert: OFF"
        elif wb_battle_alert_state == "on":
            self.wb_battle_alert_button.style = ButtonStyle.success
            self.wb_battle_alert_button.label = "World Boss Battle Alert: ON"
        else:
            self.wb_battle_alert_button.style = ButtonStyle.secondary
            self.wb_battle_alert_button.label = "World Boss Battle Alert: OFF"

        # 🥚 Egg Alert Button (3 states)
        egg_alert_state = (
            str(self.egg_alert.get("notify", "off")).lower()
            if self.egg_alert
            else "off"
        )
        if egg_alert_state == "off":
            self.egg_alert_button.style = ButtonStyle.secondary
            self.egg_alert_button.label = "Egg Hatch/Hold Alert: OFF"
        elif egg_alert_state == "on":
            self.egg_alert_button.style = ButtonStyle.success
            self.egg_alert_button.label = "Egg Hatch/Hold Alert: ON"
        elif egg_alert_state == "on_no_pings":
            self.egg_alert_button.style = ButtonStyle.primary
            self.egg_alert_button.label = "Egg Hatch/Hold Alert: ON (No Pings)"
        else:
            self.egg_alert_button.style = ButtonStyle.secondary
            self.egg_alert_button.label = "Egg Hatch/Hold Alert: OFF"

        # 🛡️ Item Alert Button (3 states)
        item_alert_state = (
            str(self.item_alert.get("notify", "off")).lower()
            if self.item_alert
            else "off"
        )
        if item_alert_state == "off":
            self.item_alert_button.style = ButtonStyle.secondary
            self.item_alert_button.label = "Item Alert: OFF"
        elif item_alert_state == "on":
            self.item_alert_button.style = ButtonStyle.success
            self.item_alert_button.label = "Item Alert: ON"
        elif item_alert_state == "on_no_pings":
            self.item_alert_button.style = ButtonStyle.primary
            self.item_alert_button.label = "Item Alert: ON (No Pings)"
        else:
            self.item_alert_button.style = ButtonStyle.secondary
            self.item_alert_button.label = "Item Alert: OFF"

    # 💫────────────────────────────────────
    # [⏰ TIMEOUT HANDLER]
    # 💫────────────────────────────────────
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            if self.message:
                await self.message.edit(
                    content="⏰ Alert Settings timed out — reopen the menu to modify again.",
                    view=self,
                )
        except Exception:
            pass
