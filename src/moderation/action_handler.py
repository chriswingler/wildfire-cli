import logging
import datetime
from datetime import timedelta
import discord
import uuid
from config.settings import config
from typing import Tuple, Optional, Union # For type hinting

# Action constants
ACTION_DM_WARNING = "DM_WARNING"
ACTION_TIMEOUT_1H = "TIMEOUT_1H"
ACTION_TIMEOUT_24H = "TIMEOUT_24H"
ACTION_BAN_PERMANENT = "BAN_PERMANENT"
ACTION_MESSAGE_DELETED = "MESSAGE_DELETED"

TIMEOUT_DURATIONS = {
    ACTION_TIMEOUT_1H: timedelta(hours=1),
    ACTION_TIMEOUT_24H: timedelta(days=1),
}

logger = logging.getLogger(__name__)

async def get_user_warnings(db_conn, user_id: int, guild_id: int):
    """Retrieves a user's warning history from the database, ordered by timestamp."""
    try:
        async with db_conn.execute(
            "SELECT warning_id, timestamp, rule_id, severity, reason, moderator_id, action_taken FROM warnings WHERE user_id = ? AND guild_id = ? ORDER BY timestamp ASC",
            (user_id, guild_id)
        ) as cursor:
            warnings_list = await cursor.fetchall()
            return warnings_list
    except Exception as e:
        logger.error(f"Error retrieving warnings for user {user_id} in guild {guild_id}: {e}", exc_info=True)
        return []

async def log_new_warning(db_conn, user_id: int, guild_id: int, rule_id: str, severity: str, reason: str, moderator_id: int = None, action_taken: str = None):
    """Logs a new warning to the database."""
    try:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        cursor = await db_conn.execute(
            "INSERT INTO warnings (user_id, guild_id, timestamp, rule_id, severity, reason, moderator_id, action_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, guild_id, timestamp, rule_id, severity, reason, moderator_id, action_taken)
        )
        await db_conn.commit()
        new_warning_id = cursor.lastrowid
        logger.info(f"Logged new warning for user {user_id} in guild {guild_id}. Rule: {rule_id}, Severity: {severity}, Action: {action_taken}, ID: {new_warning_id}")
        return new_warning_id
    except Exception as e:
        logger.error(f"Error logging warning for user {user_id} in guild {guild_id}: {e}", exc_info=True)
        return None

async def log_action(db_conn, action_id: str, guild_id: int, user_id: int, action_type: str, reason: str = None, moderator_id: int = None, target_user_id: int = None, channel_id: int = None, message_id: int = None, duration_seconds: int = None):
    """Logs a moderation action to the action_logs table."""
    try:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        await db_conn.execute(
            """INSERT INTO action_logs (action_id, guild_id, timestamp, user_id, action_type, reason, moderator_id, target_user_id, channel_id, message_id, duration_seconds)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (action_id, guild_id, timestamp, user_id, action_type, reason, moderator_id, target_user_id, channel_id, message_id, duration_seconds)
        )
        await db_conn.commit()
        logger.info(f"Logged action {action_type} (ID: {action_id}) for target user {target_user_id or 'N/A'} in guild {guild_id}, initiated by user {moderator_id or user_id}.")
    except Exception as e:
        logger.error(f"Error logging action {action_type} (ID: {action_id}): {e}", exc_info=True)

# --- Helper Functions for Discord Actions ---

async def send_dm_warning(target_user: discord.Member, guild_name: str, rule_id: str, reason_for_action: str, warning_id: int, severity: str, action_taken_summary: str = None):
    # ... (implementation unchanged)
    try:
        dm_message_content = (
            f"You have received a warning in **{guild_name}** (Warning ID: {warning_id}).\n"
            f"**Rule Broken:** {rule_id}\n"
            f"**Severity:** {severity}\n"
            f"**Reason:** {reason_for_action}\n"
        )
        if action_taken_summary:
            dm_message_content += f"**Action Taken:** {action_taken_summary}\n\n"

        dm_message_content += "Please review the server rules. Repeated violations may lead to further disciplinary actions."

        await target_user.send(dm_message_content)
        logger.info(f"Successfully sent DM warning to user {target_user.id} for warning ID {warning_id}.")
        return True
    except discord.Forbidden:
        logger.warning(f"Could not send DM to user {target_user.id} (ID: {warning_id}). They may have DMs disabled or blocked the bot.")
        return False
    except Exception as e:
        logger.error(f"Error sending DM warning to user {target_user.id} (ID: {warning_id}): {e}", exc_info=True)
        return False


async def apply_discord_timeout(bot: discord.Client, target_user: discord.Member, duration: timedelta, reason: str):
    # ... (implementation unchanged)
    try:
        await target_user.timeout(duration, reason=reason)
        logger.info(f"Successfully applied {duration} timeout to user {target_user.id} in guild {target_user.guild.id}. Reason: {reason}")
        return True
    except discord.Forbidden:
        logger.error(f"Failed to apply timeout to {target_user.id} in guild {target_user.guild.id}: Bot lacks permissions.")
        return False
    except discord.HTTPException as e:
        logger.error(f"Failed to apply timeout to {target_user.id} in guild {target_user.guild.id} due to API error: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while applying timeout to {target_user.id}: {e}", exc_info=True)
        return False

async def apply_discord_ban(bot: discord.Client, target_user: discord.Member, reason: str, delete_message_days: int = 0):
    # ... (implementation unchanged)
    try:
        await target_user.ban(reason=reason, delete_message_days=delete_message_days)
        logger.info(f"Successfully banned user {target_user.id} from guild {target_user.guild.id}. Reason: {reason}")
        return True
    except discord.Forbidden:
        logger.error(f"Failed to ban {target_user.id} from guild {target_user.guild.id}: Bot lacks permissions.")
        return False
    except discord.HTTPException as e:
        logger.error(f"Failed to ban {target_user.id} from guild {target_user.guild.id} due to API error: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while banning {target_user.id}: {e}", exc_info=True)
        return False

async def notify_moderators_action(bot: discord.Client, guild: discord.Guild, target_user: discord.Member, action_taken_display_name: str, full_reason: str, rule_id: str, warning_id: int, severity: str, reporter: discord.User):
    # ... (implementation unchanged)
    alert_channel_id_from_config = None
    if config.moderation and config.moderation.alert_channel_id is not None:
        alert_channel_id_from_config = config.moderation.alert_channel_id
    else:
        logger.info(f"Moderator alert_channel_id not found or is None in config.moderation (guild {guild.id}). Skipping moderator notification for action on {target_user.id}.")
        return

    if not alert_channel_id_from_config:
        logger.info(f"Moderator alert channel ID not configured (is None or 0) for guild {guild.id}. Skipping notification for {target_user.id}.")
        return

    channel = guild.get_channel(alert_channel_id_from_config)
    if not channel or not isinstance(channel, discord.TextChannel): # type: ignore
        logger.warning(f"Moderator alert channel {alert_channel_id_from_config} not found or not a text channel in guild {guild.id}.")
        return

    try:
        embed = discord.Embed(
            title=f"Moderation Action Alert: {action_taken_display_name}",
            description=f"Action taken against **{target_user.name}#{target_user.discriminator}** (`{target_user.id}`)",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="User", value=f"{target_user.mention} (`{target_user.id}`)", inline=False)
        embed.add_field(name="Action Taken", value=action_taken_display_name, inline=True)
        embed.add_field(name="Severity", value=severity, inline=True)
        embed.add_field(name="Rule Broken", value=rule_id, inline=True)
        embed.add_field(name="Reason", value=full_reason, inline=False)
        embed.add_field(name="Warning ID", value=str(warning_id), inline=True)
        embed.add_field(name="Reported By", value=f"{reporter.mention} (`{reporter.id}`)", inline=True)

        await channel.send(embed=embed)
        logger.info(f"Sent moderator alert to channel {alert_channel_id_from_config} for action on {target_user.id}.")
    except discord.Forbidden:
        logger.error(f"Bot lacks permission to send messages to moderator alert channel {alert_channel_id_from_config} in guild {guild.id}.")
    except Exception as e:
        logger.error(f"Error sending moderator alert for action on {target_user.id}: {e}", exc_info=True)

# --- Refactored Helper Functions for handle_violation ---

async def _check_user_exemption(
    target_user: discord.Member,
    guild: discord.Guild,
    reporter: discord.User,
    db_conn,
    bot_user_id: int,
    channel_id_for_log: Optional[int]
) -> Tuple[bool, str]:
    """Checks if a user is exempt from moderation actions."""
    is_exempt = False
    exempt_reason = ""

    if target_user.bot:
        is_exempt = True
        exempt_reason = "Target is a bot."
    elif target_user.guild_permissions.manage_messages:
        is_exempt = True
        exempt_reason = "Target has 'manage_messages' permission."
    else:
        if config.moderation and config.moderation.exempt_role_ids:
            target_user_role_ids = {role.id for role in target_user.roles}
            for exempt_role_id in config.moderation.exempt_role_ids:
                if exempt_role_id in target_user_role_ids:
                    is_exempt = True
                    exempt_reason = f"Target has exempt role ID {exempt_role_id}."
                    break

    if is_exempt:
        logger.info(f"User {target_user.id} is exempt from moderation action. Reason: {exempt_reason}")
        await log_action(
            db_conn=db_conn, action_id=f"exempt_{str(uuid.uuid4())[:8]}", guild_id=guild.id,
            user_id=bot_user_id, action_type="MODERATION_ACTION_EXEMPTED",
            reason=f"Moderation action against {target_user.display_name} ({target_user.id}) was exempted. Reason: {exempt_reason}. Requested by {reporter.display_name} ({reporter.id}).",
            moderator_id=reporter.id, target_user_id=target_user.id, channel_id=channel_id_for_log
        )
    return is_exempt, exempt_reason

async def _determine_action_details(
    current_offense_number: int,
    bot: discord.Client,
    target_user: discord.Member,
    guild: discord.Guild,
    rule_id: str,
    reporter_display_name: str
) -> Tuple[Optional[str], str, str, bool, bool, Optional[int], str]:
    """Determines the moderation action based on offense number and bot permissions."""
    action_code = None
    action_display = "Unknown Action"
    dm_summary_note = ""
    mod_alert = False
    action_successful = False
    duration_seconds = None
    warning_action_taken_code_suffix = "ERROR" # Default for unexpected issues

    if current_offense_number == 1:
        action_code = ACTION_DM_WARNING
        action_display = "DM Warning"
        dm_summary_note = "Formal warning issued via DM."
        action_successful = True
        warning_action_taken_code_suffix = "SUCCESS" # DM is always "processed"
    elif current_offense_number == 2:
        action_code = ACTION_TIMEOUT_1H
        action_display = "1-Hour Timeout"
        duration = TIMEOUT_DURATIONS[ACTION_TIMEOUT_1H]
        duration_seconds = int(duration.total_seconds())
        if not guild.me.guild_permissions.moderate_members:
            logger.error(f"Bot lacks 'moderate_members' permission in guild {guild.id} for {action_display} on {target_user.id}.")
            warning_action_taken_code_suffix = "SKIPPED_PERMISSIONS"
            action_display += " (FAILED - Missing Bot Permissions)"
            dm_summary_note = "A 1-hour timeout was attempted but could not be applied due to missing bot permissions."
        else:
            if await apply_discord_timeout(bot, target_user, duration, reason=f"Rule {rule_id} violation (2nd offense). Reported by {reporter_display_name}."):
                action_successful = True
                warning_action_taken_code_suffix = "SUCCESS"
                dm_summary_note = "You have been timed out for 1 hour due to repeated violations."
            else:
                warning_action_taken_code_suffix = "FAILED"
                action_display += " (FAILED - Check Logs)"
                dm_summary_note = "A 1-hour timeout was attempted but failed. Please contact staff if this seems incorrect."
    elif current_offense_number == 3:
        action_code = ACTION_TIMEOUT_24H
        action_display = "24-Hour Timeout"
        mod_alert = True
        duration = TIMEOUT_DURATIONS[ACTION_TIMEOUT_24H]
        duration_seconds = int(duration.total_seconds())
        if not guild.me.guild_permissions.moderate_members:
            logger.error(f"Bot lacks 'moderate_members' permission in guild {guild.id} for {action_display} on {target_user.id}.")
            warning_action_taken_code_suffix = "SKIPPED_PERMISSIONS"
            action_display += " (FAILED - Missing Bot Permissions)"
            dm_summary_note = "A 24-hour timeout was attempted but could not be applied due to missing bot permissions. Moderators have been alerted."
        else:
            if await apply_discord_timeout(bot, target_user, duration, reason=f"Rule {rule_id} violation (3rd offense). Reported by {reporter_display_name}."):
                action_successful = True
                warning_action_taken_code_suffix = "SUCCESS"
                dm_summary_note = "You have been timed out for 24 hours. Moderators have been alerted."
            else:
                warning_action_taken_code_suffix = "FAILED"
                action_display += " (FAILED - Check Logs)"
                dm_summary_note = "A 24-hour timeout was attempted but failed. Moderators have been alerted. Please contact staff if this seems incorrect."
    else: # 4th+ offense
        action_code = ACTION_BAN_PERMANENT
        action_display = "Permanent Ban"
        mod_alert = True
        if not guild.me.guild_permissions.ban_members:
            logger.error(f"Bot lacks 'ban_members' permission in guild {guild.id} to ban {target_user.id}.")
            warning_action_taken_code_suffix = "SKIPPED_PERMISSIONS"
            action_display += " (FAILED - Missing Bot Permissions)"
            dm_summary_note = "A permanent ban was attempted but could not be applied due to missing bot permissions. Moderators have been alerted."
        else:
            if await apply_discord_ban(bot, target_user, reason=f"Rule {rule_id} violation ({current_offense_number}th offense). Reported by {reporter_display_name}."):
                action_successful = True
                warning_action_taken_code_suffix = "SUCCESS"
                dm_summary_note = "You have been permanently banned from the server due to repeated violations. Moderators have been alerted."
            else:
                warning_action_taken_code_suffix = "FAILED"
                action_display += " (FAILED - Check Logs)"
                dm_summary_note = "A permanent ban was attempted but failed. Moderators have been alerted. Please contact staff if this seems incorrect."

    return action_code, action_display, dm_summary_note, mod_alert, action_successful, duration_seconds, warning_action_taken_code_suffix

async def _delete_offending_message_if_needed(
    severity: str,
    offending_message_id: Optional[int],
    actual_channel_for_actions: Optional[discord.TextChannel],
    guild: discord.Guild,
    db_conn,
    bot_user_id: int,
    reporter_id: int,
    target_user_id: int,
    rule_id: str
) -> Tuple[bool, str]:
    """Deletes the offending message if severity and conditions are met. Returns (deletion_success, note_for_dm)."""
    message_deleted_successfully = False
    dm_note_suffix = ""
    severities_for_deletion = ["high", "critical"]

    if severity.lower() in severities_for_deletion and offending_message_id and actual_channel_for_actions:
        if guild.me.permissions_in(actual_channel_for_actions).manage_messages:
            try:
                message_to_delete = await actual_channel_for_actions.fetch_message(offending_message_id)
                await message_to_delete.delete()
                message_deleted_successfully = True
                logger.info(f"Successfully deleted offending message {offending_message_id} in channel {actual_channel_for_actions.id}")
                delete_action_log_id = f"{ACTION_MESSAGE_DELETED.lower()}_{offending_message_id}_{str(uuid.uuid4())[:8]}"
                await log_action(
                    db_conn, action_id=delete_action_log_id, guild_id=guild.id, user_id=bot_user_id,
                    action_type=ACTION_MESSAGE_DELETED,
                    reason=f"Automatic deletion for severity '{severity}' violation (Rule: {rule_id}). Original message ID: {offending_message_id}",
                    moderator_id=reporter_id, target_user_id=target_user_id,
                    channel_id=actual_channel_for_actions.id, message_id=offending_message_id
                )
                dm_note_suffix = " The offending message was also deleted."
            except discord.NotFound:
                logger.warning(f"Message {offending_message_id} not found in channel {actual_channel_for_actions.id}. Already deleted?")
                dm_note_suffix = " (Offending message was not found for deletion, possibly already removed)."
            except discord.Forbidden:
                logger.error(f"Bot lacks permission to delete message {offending_message_id} in {actual_channel_for_actions.id} despite check passing (race condition?).")
                dm_note_suffix = " (Failed to delete message due to permissions)."
            except Exception as e:
                logger.error(f"Error deleting message {offending_message_id}: {e}", exc_info=True)
                dm_note_suffix = " (Error occurred during message deletion)."
        else:
            logger.warning(f"Bot lacks 'manage_messages' permission in channel {actual_channel_for_actions.id} to delete message {offending_message_id}.")
            dm_note_suffix = " (Message deletion skipped due to missing bot permissions)."
    return message_deleted_successfully, dm_note_suffix


# --- Main Violation Handler ---

async def handle_violation(bot,
                           interaction: discord.Interaction,
                           target_user: discord.Member,
                           rule_id: str,
                           severity: str,
                           reason: str = "No specific reason provided.",
                           message_context: str = None,
                           offending_message_id: Optional[int] = None,
                           channel_for_actions: Optional[discord.TextChannel] = None):
    if not hasattr(bot, 'db_conn') or not bot.db_conn:
        logger.error("Database connection not found on bot object. Cannot handle violation.")
        await interaction.response.send_message("An internal error occurred: Database not available.", ephemeral=True)
        return

    db_conn = bot.db_conn
    guild = interaction.guild
    reporter = interaction.user

    actual_channel_for_actions = channel_for_actions if channel_for_actions else interaction.channel
    # Ensure actual_channel_for_actions is a TextChannel for logging purposes, can be None if interaction.channel is not TextChannel
    log_channel_id: Optional[int] = None
    if isinstance(actual_channel_for_actions, discord.TextChannel):
        log_channel_id = actual_channel_for_actions.id
    elif actual_channel_for_actions: # If it's some other channel type from interaction.channel
        log_channel_id = actual_channel_for_actions.id # type: ignore
        logger.warning(f"actual_channel_for_actions (ID: {log_channel_id}) is not a TextChannel (type: {type(actual_channel_for_actions)}). Some operations like message deletion might fail if it's not explicitly passed as TextChannel.")


    is_exempt, exempt_reason = await _check_user_exemption(target_user, guild, reporter, db_conn, bot.user.id, log_channel_id) # type: ignore
    if is_exempt:
        await interaction.response.send_message(f"{target_user.mention} is exempt from this moderation action. Reason: {exempt_reason}", ephemeral=True)
        return

    logger.info(f"Handling violation for user {target_user.id} in guild {guild.id}. Rule: {rule_id}, Severity: {severity}. Reported by: {reporter.id}. Context: {message_context or 'N/A'}")

    user_warnings = await get_user_warnings(db_conn, target_user.id, guild.id)
    current_offense_number = len(user_warnings) + 1

    action_code, action_display, dm_summary_note, mod_alert, action_successful, duration_seconds, warning_action_taken_code_suffix = await _determine_action_details(
        current_offense_number, bot, target_user, guild, rule_id, reporter.display_name
    )

    if not action_code:
        logger.error(f"Unexpected issue: _determine_action_details did not return an action_code for user {target_user.id}, offense {current_offense_number}.")
        await interaction.response.send_message("Internal error: Could not determine appropriate action.", ephemeral=True)
        return

    full_reason_for_action = (
        f"Rule: {rule_id} (Severity: {severity}). Offense #{current_offense_number}. "
        f"Action: {action_display}. Reported by: {reporter.display_name} ({reporter.id}). "
        f"Original reason: {reason}. Message Context: {message_context or 'N/A'}."
    )

    # Ensure actual_channel_for_actions is TextChannel for deletion, otherwise it won't work.
    text_channel_for_deletion: Optional[discord.TextChannel] = None
    if isinstance(actual_channel_for_actions, discord.TextChannel):
        text_channel_for_deletion = actual_channel_for_actions

    message_deleted_successfully, deletion_dm_note = await _delete_offending_message_if_needed(
        severity, offending_message_id, text_channel_for_deletion, guild, db_conn, bot.user.id, reporter.id, target_user.id, rule_id # type: ignore
    )
    if deletion_dm_note: # Append deletion note to existing DM summary
        dm_summary_note = f"{dm_summary_note.rstrip('.')}.{deletion_dm_note}"


    final_warning_action_code = f"{action_code}_{warning_action_taken_code_suffix}"
    warning_id = await log_new_warning(
        db_conn, user_id=target_user.id, guild_id=guild.id, rule_id=rule_id, severity=severity,
        reason=full_reason_for_action, moderator_id=reporter.id, action_taken=final_warning_action_code
    )

    if warning_id is None:
        logger.error(f"Failed to log warning for {target_user.id} after determining action {action_code}. Aborting further actions.")
        response_message_on_fail = f"CRITICAL ERROR: Failed to log warning to database for {target_user.mention}. Action '{action_display}' status: {'Processed' if action_successful else 'Failed/Skipped'}. Please check logs."
        await interaction.response.send_message(response_message_on_fail, ephemeral=True)
        return

    if (action_successful or action_code == ACTION_DM_WARNING or warning_action_taken_code_suffix == "SKIPPED_PERMISSIONS") and dm_summary_note:
        await send_dm_warning(target_user, guild.name, rule_id, full_reason_for_action, warning_id, severity, action_taken_summary=dm_summary_note)

    action_log_id = f"{action_code.lower()}_{target_user.id}_{warning_id}_{str(uuid.uuid4())[:8]}"
    await log_action(
        db_conn, action_id=action_log_id, guild_id=guild.id, user_id=bot.user.id,
        action_type=final_warning_action_code, reason=full_reason_for_action,
        moderator_id=reporter.id, target_user_id=target_user.id, channel_id=log_channel_id,
        duration_seconds=duration_seconds if action_successful and duration_seconds else None
    )

    if mod_alert:
        await notify_moderators_action(bot, guild, target_user, action_display, full_reason_for_action, rule_id, warning_id, severity, reporter)

    response_message = (
        f"Action '{action_display}' for {target_user.mention} (Warning ID: {warning_id}) has been processed.\n"
        f"User has {len(user_warnings) + 1} total warnings (including this one).\n"
        f"Details: {dm_summary_note}"
    )
    if message_deleted_successfully: # This was set by the helper
        response_message += "\nOffending message was deleted."
    elif severity.lower() in ["high", "critical"] and offending_message_id and not message_deleted_successfully : # Check if deletion was attempted but failed
        response_message += "\nNote: Offending message deletion was attempted but failed or was skipped (see logs/DM notes)."

    if not action_successful and action_code != ACTION_DM_WARNING:
         response_message += f"\n**Important: The Discord action part ('{action_code}') may have failed or was skipped. Please check bot permissions and logs.**"

    await interaction.response.send_message(response_message, ephemeral=True)
