import discord
from discord import app_commands
from discord.ext import commands

from constants.celestial_constants import CELESTIAL_TEXT_CHANNELS
from constants.wb_constants import *
from group_command_func.wb_sub.wb_sub_embed import create_wb_embed
from utils.functions.pretty_defer import pretty_defer
from utils.logs.pretty_log import pretty_log


# 💜────────────────────────────────────────────
#   🟣 REMOVE WB Subscription
# 💜────────────────────────────────────────────
async def wb_sub_remove_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    boss_name: str,
):
    from group_command_func.wb_sub.wb_sync import (
        sync_remove_all_wb_pings,
        sync_remove_wb_ping,
    )

    handler = await pretty_defer(
        interaction=interaction,
        content="Processing your WB unsub...",
        ephemeral=False,
    )
    try:
        user = interaction.user
        guild = interaction.guild

        # 🗺️ Remap aliases
        remap = {
            "uss": "uss",
            "urshifu singlestrike": "uss",
            "urs": "urs",
            "urshifu rapidstrike": "urs",
            "ee": "eternatus",
        }

        # ✅ Check if user wants to remove ALL subscriptions
        if boss_name.lower() == "all":
            removed = await sync_remove_all_wb_pings(bot, user.id)

            # 💠 Espeon Log
            pretty_log(
                tag="db",
                message=f"💜 All WB Subs Removed | User: {user.display_name} ({user.id}) | Rows removed: {removed}",
                label="💠 WB SUB",
            )

            # 📦 User Embed
            embed = discord.Embed(
                title=f"{WBEmojis.WB_Spawn} All WB Pings Removed",
                description=f"{user.mention}, all your WB subscriptions have been removed.",
                color=discord.Color.purple(),
            )
            await handler.success(content="", embed=embed)
            return  # exit early

        # 🗝️ Normal removal: parse selection (boss|variant|mode)
        try:
            boss_name, variant, mode = boss_name.split("|")
        except ValueError:
            await handler.error(
                content="Invalid format. Please provide 'boss|variant|mode' or 'all'."
            )
            return

        lower_boss_name = boss_name.lower()
        key = remap.get(lower_boss_name, lower_boss_name)
        variant = variant.lower()
        mode = mode.lower()

        # Remove from DB/cache
        await sync_remove_wb_ping(bot=bot, user_id=user.id, boss_name=lower_boss_name)

        # 📦 Create User Embed via helper
        embed = create_wb_embed(
            user=user,
            guild=guild,
            boss_name=boss_name,
            variant=variant,
            mode=mode,
            action="removed",
        )
        await handler.success(content="", embed=embed)

        # 📦 Send Log Embed
        log_embed = embed.copy()
        log_embed.set_footer(text=f"User ID: {user.id}", icon_url=guild.icon.url)
        log_channel = guild.get_channel(CELESTIAL_TEXT_CHANNELS.server_logs)
        if log_channel:
            await log_channel.send(embed=log_embed)

        # 💠 Espeon Log
        pretty_log(
            tag="db",
            message=(
                f"💜 WB Sub Removed | User: {user.display_name} ({user.id}) "
                f"| Boss: {boss_name.title()} | Variant: {variant} | Mode: {mode}"
            ),
            label="💠 WB SUB",
        )

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"❌ Failed to remove WB Sub for {interaction.user.id}: {e}",
            exc=e,
            label="💠 WB SUB",
        )
