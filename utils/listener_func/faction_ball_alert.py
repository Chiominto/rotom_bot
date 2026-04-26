import re

import discord

from constants.aesthetics import Emojis
from constants.faction_data import get_faction_by_emoji
from utils.cache.cache_list import (
    daily_faction_ball_cache,
    faction_ball_alert_cache,
    faction_cache,
    processed_faction_ball_alerts,
)
from utils.cache.faction_cache import get_user_id_by_name
from utils.db.faction_ball_alert_db_func import (
    upsert_user_faction_ball_alert_via_user_id,
)
from utils.functions.get_pokemeow_reply import get_pokemeow_reply
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

enable_debug(f"{__name__}.faction_ball_alert")
FISHING_COLOR = 0x87CEFA


def extract_trainer_name_from_description(description: str) -> str | None:
    """
    Extracts the trainer name (e.g. 'khy.09') from a PokéMeow embed description.
    Example line:
    '<:irida:1428149067673767996>  **khy.09** found a wild <:517:721586120692989992><:dexcaught:667082939632189451>**Munna**!'
    """
    match = re.search(r"\*\*(.+?)\*\*\s+found a wild", description)
    if match:
        return match.group(1).strip()
    return None


def extract_member_username_from_embed(embed: discord.Embed) -> str | None:
    """
    Extracts the username from the embed author name, e.g. "Congratulations, frayl!" -> "frayl".
    Returns None if not found.
    """
    if embed.author and embed.author.name:
        # Try 'Congratulations, username!' first
        match = re.search(r"Congratulations, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
        # Fallback: 'Well done, username!'
        match = re.search(r"Well done, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
        # Fallback: 'Great work, username!'
        match = re.search(r"Great work, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
    return None


def get_member_by_username(guild, username):
    """
    Returns the discord.Member object for the given username (case-insensitive).
    Returns None if not found.
    """
    for member in guild.members:
        if member.name.lower() == username.lower():
            return member
    return None


def resolve_user_id(guild, user_name):
    """
    Try to get user ID from cache; if not found, try Discord member list.
    Returns user ID (int) or None.
    """
    user_id = get_user_id_by_name(user_name)
    if user_id is not None:
        return user_id
    member = get_member_by_username(guild, user_name)
    if member:
        return member.id
    return None


# 🛡️────────────────────────────────────────────
#      🛡️ Faction Ball Alert Listener
# 🛡️────────────────────────────────────────────
async def faction_ball_alert(
    bot: discord.Client, before: discord.Message, after: discord.Message
):
    try:
        debug_log("Function called")
        if not after.embeds or not after.embeds[0].description:
            debug_log("No embeds or description found, returning early")
            return

        description_text = after.embeds[0].description
        debug_log(f"Embed description: {description_text!r}")

        if description_text and "<:team_logo:" not in description_text:
            debug_log("No team_logo emoji in description, returning early")
            return
        team_logo_emoji = re.findall(r"<:team_logo:\d+>", description_text)
        debug_log(f"Extracted team_logo emojis: {team_logo_emoji}")

        if len(team_logo_emoji) != 1:
            debug_log(
                f"Expected exactly one team_logo emoji, found {len(team_logo_emoji)}. Returning early."
            )
            return
        if after.id in processed_faction_ball_alerts:
            return
        processed_faction_ball_alerts.add(after.id)

        embed_faction = (
            get_faction_by_emoji(team_logo_emoji[0]) if team_logo_emoji else None
        )
        debug_log(f"Embed faction: {embed_faction}")
        if not embed_faction:
            debug_log("Could not determine faction from emoji, returning early")
            return

        trainer_id = None
        trainer_name = None
        user_id = None
        fishing_user = None

        member = await get_pokemeow_reply(before)
        debug_log(f"Reply member: {member}")
        if not member:
            debug_log("No replied member found, attempting fallback extraction")
            embed_color = after.embeds[0].color
            if embed_color and (
                embed_color.value == FISHING_COLOR or embed_color == FISHING_COLOR
            ):
                debug_log(
                    "Embed color matches fishing color, attempting to extract trainer ID from reference"
                )
                if after.reference and getattr(after.reference, "resolved", None):
                    resolved_author = getattr(after.reference.resolved, "author", None)
                    trainer_id = resolved_author.id if resolved_author else None
                    debug_log(f"Extracted trainer ID from reference: {trainer_id}")

                if not trainer_id and after.embeds[0].description:
                    name_match = re.search(
                        r"\*\*(.+?)\*\*", after.embeds[0].description
                    )
                    if name_match:
                        trainer_name = name_match.group(1)
                        debug_log(f"Extracted trainer name: {trainer_name}")
                        user = discord.utils.find(
                            lambda m: m.display_name == trainer_name,
                            after.guild.members,
                        )
                        fishing_trainer_id = user.id if user else None
                        debug_log(f"Matched trainer name to ID: {fishing_trainer_id}")

                if not trainer_id and not trainer_name:
                    debug_log("Could not extract trainer ID or name, returning early")
                    return

            elif embed_color and embed_color.value != FISHING_COLOR:
                debug_log("No member found, using fallback")
                trainer_name = extract_trainer_name_from_description(description_text)
                if trainer_name is None:
                    trainer_name = extract_member_username_from_embed(after.embeds[0])
                    debug_log(
                        f"Description fallback failed, extracted trainer name from embed author: {trainer_name}"
                    )
                debug_log(f"Fallback extracted trainer name: {trainer_name}")

                user_id = get_user_id_by_name(trainer_name) if trainer_name else None
                debug_log(
                    f"Fallback found user_id: {user_id} from trainer_name: {trainer_name}"
                )
                member = after.guild.get_member(user_id) if user_id else None
                debug_log(f"Fetched member from guild: {member}")
                if not member:

                    # Try to fetch user id via get_user_id_by_name
                    if trainer_name:
                        user_id = get_user_id_by_name(trainer_name)
                        debug_log(f"Fetched user ID from name: {user_id}")
                        if user_id:
                            member = after.guild.get_member(user_id)
                            debug_log(
                                f"Fetched member from guild using user ID: {member}"
                            )

                    if not member:
                        debug_log("No member found for user_id, returning early")
                        return

        #
        if member:
            user_id = member.id
        elif trainer_id:
            user_id = trainer_id
        elif trainer_name:
            user = discord.utils.find(
                lambda m: m.display_name == trainer_name, after.guild.members
            )
            user_id = user.id if user else None

        trainer_mention = f"<@{user_id}>" if user_id else "Trainer"

        user_faction_ball_alert = faction_ball_alert_cache.get(user_id)
        debug_log(f"User faction ball alert settings: {user_faction_ball_alert}")

        if not user_faction_ball_alert:
            # Only upsert when we have a valid user_id
            if user_id is not None:
                await upsert_user_faction_ball_alert_via_user_id(
                    bot=bot,
                    user_id=user_id,
                    user_name=member.name if member else trainer_name,
                    notify="on_no_pings",
                )
                debug_log(
                    "No existing settings found — upserted default faction ball alert settings for user"
                )
                user_faction_ball_alert = faction_ball_alert_cache.get(user_id)
                debug_log(
                    f"Re-fetched user faction ball alert after upsert: {user_faction_ball_alert}"
                )
            else:
                debug_log("No user_id available yet, skipping initial upsert")

            # Still nothing — try fallback via trainer_name
            if not user_faction_ball_alert:
                if trainer_name:
                    user_id = get_user_id_by_name(trainer_name)
                    if user_id:
                        debug_log(
                            f"Fetched user ID from cache by trainer name: {user_id}"
                        )
                        user_faction_ball_alert = faction_ball_alert_cache.get(user_id)
                        fishing_user = after.guild.get_member(user_id)
                        debug_log(f"Fetched fishing user from guild: {fishing_user}")

                        # If fallback resolved user_id but settings still missing, create defaults now.
                        if not user_faction_ball_alert:
                            await upsert_user_faction_ball_alert_via_user_id(
                                bot=bot,
                                user_id=user_id,
                                user_name=(
                                    member.name
                                    if member
                                    else (
                                        fishing_user.name
                                        if fishing_user
                                        else trainer_name
                                    )
                                ),
                                notify="on_no_pings",
                            )
                            debug_log(
                                "Fallback resolved user_id — upserted default faction ball alert settings"
                            )
                            user_faction_ball_alert = faction_ball_alert_cache.get(
                                user_id
                            )
                            debug_log(
                                f"Re-fetched user faction ball alert after fallback upsert: {user_faction_ball_alert}"
                            )
                    else:
                        user_id = None
                        debug_log("No user ID found in cache, returning early")
                        content = f"{trainer_mention} I don't know your faction yet, can you do `;fa`? Thanks!"
                        await after.channel.send(content=content)
                        return

                    if not user_faction_ball_alert:
                        debug_log(
                            "[EXIT-C] No settings after fallback lookup, returning early"
                        )
                        return
                else:
                    debug_log("No trainer name available for fallback, returning early")
                    content = f"{trainer_mention} I don't know your faction yet, can you do `;fa`? Thanks!"
                    await after.channel.send(content=content)
                    return

        user_faction_ball_notify = user_faction_ball_alert.get("notify")
        debug_log(f"User faction ball notify setting: {user_faction_ball_notify}")
        if not user_faction_ball_notify or user_faction_ball_notify.lower() == "off":
            debug_log("User notify setting is off or missing, returning early")
            return

        display_embed_faction_emoji = getattr(Emojis, embed_faction)
        display_embed_faction = (
            f"{display_embed_faction_emoji} {embed_faction.title()}"
            if display_embed_faction_emoji
            else embed_faction.title()
        )

        user_name = (
            member.name if member else fishing_user.name if fishing_user else "Trainer"
        )
        user_mention = (
            member.mention
            if member
            else fishing_user.mention if fishing_user else "Trainer"
        )
        from utils.cache.faction_cache import get_user_faction

        user_faction = get_user_faction(user_id)
        debug_log(f"User faction: {user_faction}")
        if not user_faction:
            debug_log("User has no faction set, returning early")
            content = f"{user_mention} I don't know your faction yet, can you do `;fa`? Thanks!"
            await after.channel.send(content=content)
            return
        from utils.cache.daily_fa_ball_cache import get_faction_ball

        faction_ball = get_faction_ball(user_faction)
        debug_log(f"Faction daily ball: {faction_ball}")
        if not faction_ball:
            content = f"{user_mention} I don't know your faction's daily ball yet, can you do `;fa`? Thanks!."
            await after.channel.send(content=content)
            pretty_log(
                "info",
                f"Could not send faction ball alert to {user_name} ({user_id}) for {embed_faction} daily ball because their faction {user_faction} has no daily ball set.",
            )
            debug_log(
                "No daily ball set for user's faction, sent reminder message and returned early"
            )
            return

        ball_emoji = getattr(Emojis, faction_ball.lower())
        debug_log(f"Ball emoji for daily ball: {ball_emoji}")
        if ball_emoji:
            if user_faction_ball_notify == "on":
                content = f"<@{user_id}>, This Pokemon is a daily {display_embed_faction} hunt! Use {ball_emoji}!"
                await after.channel.send(content)
                pretty_log(
                    "sent",
                    f"Sent faction ball alert to {user_name} ({user_id}) for {embed_faction} daily ball {faction_ball}",
                )
                debug_log("Sent faction ball alert with ping")
            elif user_faction_ball_notify == "on_no_pings":
                content = f"**{user_name}**, This Pokemon is a daily {display_embed_faction} hunt! Use {ball_emoji}!"
                await after.channel.send(content)
                pretty_log(
                    "sent",
                    f"Sent faction ball alert (no ping) to {user_name} ({user_id}) for {embed_faction} daily ball {faction_ball}",
                )
                debug_log("Sent faction ball alert without ping")
            elif user_faction_ball_notify == "react":
                try:
                    await after.add_reaction(ball_emoji)
                    debug_log("Added ball emoji reaction")
                except Exception as e:
                    pretty_log("error", f"Failed to add reaction {ball_emoji}: {e}")
                    debug_log(f"Failed to add reaction: {e}")
        else:
            debug_log("No ball emoji found for daily ball, nothing sent")

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to process faction ball alert: {e}",
            label="FACTION_BALL_ALERT",
        )
        debug_log(f"Exception occurred: {e}", highlight=True)
