import discord
from discord import app_commands
from discord.ext import commands

from constants.celestial_constants import CELESTIAL_TEXT_CHANNELS
from constants.wb_constants import *
from group_command_func.wb_sub.wb_sub_embed import create_wb_embed
from utils.functions.pretty_defer import pretty_defer
from utils.logs.pretty_log import pretty_log


# 💜────────────────────────────────────────────
#   🟣 Add WB Subscription
# 💜────────────────────────────────────────────
async def wb_sub_add_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    boss_name: str,
    variant: str,
    mode: str,
    channel: discord.TextChannel | None = None,
):
    from group_command_func.wb_sub.wb_sync import sync_upsert_wb_ping

    handler = await pretty_defer(
        interaction=interaction,
        content=f"Processing your {boss_name} subscription...",
        ephemeral=False,
    )

    try:
        user = interaction.user
        guild = interaction.guild

        # Normalize variant/mode
        variant = variant.lower()
        mode = mode.lower()

        if mode == "channel":
            if channel is None:
                await handler.error(
                    content="You must specify a channel when mode is 'Channel'."
                )
                return
            ping_channel_id = channel.id
        else:
            ping_channel_id = None

        # Insert/update subscription
        await sync_upsert_wb_ping(
            bot=bot,
            user_id=user.id,
            user_name=user.display_name,
            variant=variant,
            boss_name=boss_name.lower(),
            mode=mode,
            channel_id=ping_channel_id,
        )

        # 📦 Create User Embed via helper
        embed = create_wb_embed(
            user=user,
            guild=guild,
            boss_name=boss_name,
            variant=variant,
            mode=mode,
            action="added",
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
                f"💜 WB Sub Added | User: {user.display_name} ({user.id}) "
                f"| Boss: {boss_name.title()} | Variant: {variant} | Mode: {mode}"
            ),
            label="💠 WB SUB",
        )

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"❌ Failed to add WB Sub for {interaction.user.id}: {e}",
            exc=e,
            label="💠 WB SUB",
        )
