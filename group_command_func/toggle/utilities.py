import discord
from discord import ButtonStyle
from discord.ext import commands

from constants.aesthetics import Emojis
from constants.celestial_constants import CELESTIAL_EMOJIS
from utils.db.utilities_db import (
    fetch_user_utility_type_setting,
    upsert_utility_setting,
)
from utils.functions.safe_response import safe_respond
from utils.logs.pretty_log import pretty_log


# 💗────────────────────────────────────────────
# [🎀 FUNCTION] Utility Settings
# 💗────────────────────────────────────────────
async def utilities_settings_func(bot: commands.Bot, interaction: discord.Interaction):
    """Main entry for user utility settings."""
    try:
        await interaction.response.defer()  # Defer immediately
        phone_setting = await fetch_user_utility_type_setting(
            bot, interaction.user.id, "phone"
        )
        battle_weakness_setting = await fetch_user_utility_type_setting(
            bot, interaction.user.id, "battle_weakness"
        )
        phone_setting = phone_setting or {"setting": "iphone"}
        battle_weakness_setting = battle_weakness_setting or {"setting": "off"}

        view = UtilitySettingsView(
            bot,
            interaction.user,
            phone_setting,
            battle_weakness_setting,
        )

        message = await interaction.followup.send(
            content="Modify your Utility Settings:", view=view, ephemeral=True
        )
        view.message = message

        pretty_log(
            "ui",
            f"[Utility Settings] Displayed  utility settings for {interaction.user.display_name}",
        )

    except Exception as e:
        pretty_log("error", f"Failed to load Utility settings: {e}")
        await interaction.followup.send(
            content="⚠️ An error occurred while loading your Utility settings.",
            ephemeral=True,
        )


# 💗────────────────────────────────────────────
# [🌸 VIEW CLASS] Utility Settings View (patched)
# 💗────────────────────────────────────────────
class UtilitySettingsView(discord.ui.View):
    def __init__(
        self,
        bot: commands.Bot,
        user: discord.Member,
        phone_setting,
        battle_weakness_setting,
    ):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.phone_setting = phone_setting
        self.battle_weakness_setting = battle_weakness_setting
        self.message = None  # set later
        self.update_button_styles()

    def _setting_value(self, raw_setting, default_value: str) -> str:
        """Normalize DB/cache setting payloads that may be dicts or plain strings."""
        if isinstance(raw_setting, dict):
            return str(raw_setting.get("setting", default_value)).lower()
        if isinstance(raw_setting, str):
            return raw_setting.lower()
        return default_value

    # 💫────────────────────────────────────
    # [📱 BUTTON] Phone Setting (2-State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="Phone Copy Setting: Iphone",
        style=ButtonStyle.secondary,
        emoji="📱",
    )
    async def phone_copy_settings_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        try:
            current_state = self._setting_value(self.phone_setting, "iphone")

            # 🔹 2-State Cycle: iphone -> android -> iphone
            new_state = "android" if current_state == "iphone" else "iphone"

            await upsert_utility_setting(
                self.bot, self.user.id, self.user.name, "phone", new_state
            )
            self.phone_setting = {"setting": new_state}

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = "IPHONE" if new_state == "iphone" else "ANDROID"

            await interaction.edit_original_response(
                content=f"Modify your Phone Copy Settings:\n📱 Phone Copy Setting set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set Phone Copy Setting to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling Phone Copy Setting: {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "⚠️ An error occurred while updating Phone Copy Setting.",
                ephemeral=True,
            )

    # 💫────────────────────────────────────
    # [🗡️ BUTTON] Battle Weakness Setting (3 -State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="Battle Weakness Setting: OFF",
        style=ButtonStyle.secondary,
        emoji="🗡️",
    )
    async def battle_weakness_setting_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        try:
            current_state = self._setting_value(self.battle_weakness_setting, "off")

            # 🔹 3-State Cycle: off -> full -> truncated -> off
            if current_state == "off":
                new_state = "full"
            elif current_state == "on":
                new_state = "truncated"
            else:  # react or any other state
                new_state = "off"

            await upsert_utility_setting(
                self.bot, self.user.id, self.user.name, "battle_weakness", new_state
            )
            self.battle_weakness_setting = {"setting": new_state}

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = {
                "off": "OFF",
                "full": "FULL",
                "truncated": "TRUNCATED",
            }.get(new_state, "OFF")

            await interaction.edit_original_response(
                content=f"Modify your Utility Settings:\n🗡️ Battle Weakness Setting set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set Battle Weakness Setting to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling Battle Weakness Setting: {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "⚠️ An error occurred while updating Battle Weakness Setting.",
                ephemeral=True,
            )

    # 💫────────────────────────────────────
    # [🎨 STYLE UPDATE FUNCTION]
    # 💫────────────────────────────────────
    def update_button_styles(self):

        # 📱 Phone Copy Setting Button (2 states)
        phone_setting_state = self._setting_value(self.phone_setting, "iphone")
        if phone_setting_state == "iphone":
            self.phone_copy_settings_button.style = ButtonStyle.secondary
            self.phone_copy_settings_button.label = "Phone Copy Setting: IPHONE"
        elif phone_setting_state == "android":
            self.phone_copy_settings_button.style = ButtonStyle.success
            self.phone_copy_settings_button.label = "Phone Copy Setting: ANDROID"
        else:
            self.phone_copy_settings_button.style = ButtonStyle.secondary
            self.phone_copy_settings_button.label = "Phone Copy Setting: IPHONE"

        # 🗡️ Battle Weakness Setting Button (3 states)
        battle_weakness_state = self._setting_value(self.battle_weakness_setting, "off")
        if battle_weakness_state == "off":
            self.battle_weakness_setting_button.style = ButtonStyle.secondary
            self.battle_weakness_setting_button.label = "Battle Weakness Setting: OFF"
        elif battle_weakness_state == "full":
            self.battle_weakness_setting_button.style = ButtonStyle.success
            self.battle_weakness_setting_button.label = "Battle Weakness Setting: FULL"
        elif battle_weakness_state == "truncated":
            self.battle_weakness_setting_button.style = ButtonStyle.primary
            self.battle_weakness_setting_button.label = (
                "Battle Weakness Setting: TRUNCATED"
            )
        else:
            self.battle_weakness_setting_button.style = ButtonStyle.secondary
            self.battle_weakness_setting_button.label = "Battle Weakness Setting: OFF"

    # 💫────────────────────────────────────
    # [⏰ TIMEOUT HANDLER]
    # 💫────────────────────────────────────
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            if self.message:
                await self.message.edit(
                    content="⏰ Utility Settings timed out — reopen the menu to modify again.",
                    view=self,
                )
        except Exception:
            pass
