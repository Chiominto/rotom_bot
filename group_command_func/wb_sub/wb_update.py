import discord
from discord import app_commands
from discord.ext import commands

from constants.celestial_constants import CELESTIAL_TEXT_CHANNELS
from constants.wb_constants import *
from group_command_func.wb_sub.wb_sub_embed import create_wb_embed
from utils.functions.pretty_defer import pretty_defer
from utils.logs.pretty_log import pretty_log


# 💜────────────────────────────────────────────
#   🟣 UPDATE WB Subscription
# 💜────────────────────────────────────────────
async def wb_sub_update_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    boss_name: str,  # comes from autocomplete (boss|variant|mode)
    new_variant: str,
    new_mode: str,
):
    from group_command_func.wb_sub.wb_sync import sync_update_variant_mode

    handler = await pretty_defer(
        interaction=interaction,
        content="Updating your WB subscription...",
        ephemeral=False,
    )
    try:
        user = interaction.user
        guild = interaction.guild

        # Parse selection (boss|variant|mode)
        boss_name, old_variant, old_mode = boss_name.split("|")
        boss_name = boss_name.lower()

        # Normalize inputs
        new_variant = new_variant.lower()
        new_mode = new_mode.lower()

        # 🔹 Update DB without overwriting channel_id
        updated = await sync_update_variant_mode(
            bot=bot,
            user_id=user.id,
            boss_name=boss_name,
            new_variant=new_variant,
            new_mode=new_mode,
        )

        if not updated:
            await handler.fail(
                content=f"Could not update your subscription for **{boss_name.title()}**."
            )
            return

        # 📦 Create User Embed using helper
        # We'll add old→new info in the description
        embed = create_wb_embed(
            user=user,
            guild=guild,
            boss_name=boss_name,
            variant=new_variant,
            mode=new_mode,
            action="updated",
        )
        # Append old variant/mode info to description
        embed.description += f"\n\n**Old:** {old_variant} / {old_mode}"

        await handler.success(content="", embed=embed)

        # 📦 Create Log Embed
        log_embed = embed.copy()
        log_embed.set_footer(text=f"User ID: {user.id}", icon_url=guild.icon.url)
        log_channel = guild.get_channel(CELESTIAL_TEXT_CHANNELS.server_logs)
        if log_channel:
            await log_channel.send(embed=log_embed)

        # 📝 Espeon Log
        pretty_log(
            tag="db",
            message=(
                f"🔄 WB Sub Updated | User: {user.display_name} ({user.id}) | "
                f"Boss: {boss_name} | {old_variant}/{old_mode} → {new_variant}/{new_mode}"
            ),
        )

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"❌ Failed to update WB Sub for {interaction.user.id}: {e}",
            exc=e,
        )
