import logging
import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import uuid
from config.settings import config

logger = logging.getLogger(__name__)

# --- Database Functions for Appeals ---

async def _log_appeal_related_action(db_conn, action_id: str, guild_id: int, user_id: int, action_type: str, reason: str = None, moderator_id: int = None, target_user_id: int = None, related_appeal_id: int = None):
    """Logs an appeal-related action to the action_logs table."""
    try:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        full_reason = reason
        if related_appeal_id:
            full_reason = f"{reason} (Appeal ID: {related_appeal_id})"

        await db_conn.execute(
            """INSERT INTO action_logs (action_id, guild_id, timestamp, user_id, action_type, reason, moderator_id, target_user_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (action_id, guild_id, timestamp, user_id, action_type, full_reason, moderator_id, target_user_id)
        )
        await db_conn.commit()
        logger.info(f"Logged appeal action {action_type} (ID: {action_id}) for user {target_user_id or user_id} in guild {guild_id}.")
    except Exception as e:
        logger.error(f"Error logging appeal action {action_type} (ID: {action_id}): {e}", exc_info=True)

async def log_appeal_submission(db_conn, user_id: int, guild_id: int, action_id_appealed: str, original_action_type: str, reason: str) -> tuple[int | None, str | None]:
    appeal_submission_log_uuid = str(uuid.uuid4())
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    try:
        cursor = await db_conn.execute(
            """INSERT INTO appeals (user_id, guild_id, action_id_appealed, original_action_type, reason, status, timestamp, appeal_submission_log_id)
               VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?)""",
            (user_id, guild_id, action_id_appealed, original_action_type, reason, timestamp, appeal_submission_log_uuid)
        )
        await db_conn.commit()
        appeal_id = cursor.lastrowid
        logger.info(f"New appeal (ID: {appeal_id}) submitted by user {user_id} for action {action_id_appealed} in guild {guild_id}.")
        await _log_appeal_related_action(
            db_conn, action_id=appeal_submission_log_uuid, guild_id=guild_id, user_id=user_id,
            action_type='APPEAL_SUBMITTED', reason=f"User submitted appeal for action: {action_id_appealed}. Reason: {reason}",
            target_user_id=user_id, related_appeal_id=appeal_id
        )
        return appeal_id, appeal_submission_log_uuid
    except Exception as e:
        logger.error(f"Database error logging appeal submission for user {user_id}, action {action_id_appealed}: {e}", exc_info=True)
        await db_conn.rollback()
        return None, None

async def get_appeal_by_id(db_conn, appeal_id: int, guild_id: int):
    try:
        async with db_conn.execute(
            "SELECT * FROM appeals WHERE appeal_id = ? AND guild_id = ?",
            (appeal_id, guild_id)
        ) as cursor:
            return await cursor.fetchone()
    except Exception as e:
        logger.error(f"Error retrieving appeal {appeal_id} for guild {guild_id}: {e}", exc_info=True)
        return None

async def get_user_open_appeals(db_conn, user_id: int, guild_id: int) -> list:
    try:
        async with db_conn.execute(
            "SELECT * FROM appeals WHERE user_id = ? AND guild_id = ? AND status = 'PENDING'",
            (user_id, guild_id)
        ) as cursor:
            return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Error retrieving open appeals for user {user_id} in guild {guild_id}: {e}", exc_info=True)
        return []

async def update_appeal_status(db_conn, appeal_id: int, guild_id: int, new_status: str, moderator_id: int) -> bool:
    try:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        await db_conn.execute(
            "UPDATE appeals SET status = ?, moderator_id = ?, appeal_decision_timestamp = ? WHERE appeal_id = ? AND guild_id = ?",
            (new_status, moderator_id, timestamp, appeal_id, guild_id)
        )
        await db_conn.commit()
        logger.info(f"Appeal ID {appeal_id} in guild {guild_id} status updated to {new_status} by moderator {moderator_id}.")
        return True
    except Exception as e:
        logger.error(f"Error updating status for appeal {appeal_id} in guild {guild_id}: {e}", exc_info=True)
        await db_conn.rollback()
        return False

async def get_pending_appeals(db_conn, guild_id: int, limit: int = 20) -> list:
    try:
        async with db_conn.execute(
            "SELECT * FROM appeals WHERE guild_id = ? AND status = 'PENDING' ORDER BY timestamp ASC LIMIT ?",
            (guild_id, limit)
        ) as cursor:
            return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Error retrieving pending appeals for guild {guild_id}: {e}", exc_info=True)
        return []

async def expire_old_appeals(db_conn, guild_id: int, days_old: int = 7) -> int:
    expired_count = 0
    try:
        cutoff_timestamp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_old)
        # First, select appeals to expire to log them individually
        async with db_conn.execute(
            "SELECT appeal_id, user_id FROM appeals WHERE guild_id = ? AND status = 'PENDING' AND timestamp < ?",
            (guild_id, cutoff_timestamp)
        ) as cursor:
            appeals_to_expire = await cursor.fetchall()

        if not appeals_to_expire:
            return 0

        for appeal_row in appeals_to_expire:
            appeal_id = appeal_row['appeal_id']
            user_id = appeal_row['user_id']

            await db_conn.execute(
                "UPDATE appeals SET status = 'EXPIRED' WHERE appeal_id = ? AND guild_id = ?",
                (appeal_id, guild_id)
            )
            # Log expiration to action_logs
            log_id = str(uuid.uuid4())
            await _log_appeal_related_action(
                db_conn, action_id=log_id, guild_id=guild_id, user_id=0, # System action, user_id 0 or bot.user.id
                action_type='APPEAL_EXPIRED', reason=f"Appeal ID {appeal_id} for user {user_id} auto-expired after {days_old} days.",
                target_user_id=user_id, related_appeal_id=appeal_id
            )
            expired_count += 1

        await db_conn.commit()
        if expired_count > 0:
            logger.info(f"Auto-expired {expired_count} appeals older than {days_old} days in guild {guild_id}.")
        return expired_count
    except Exception as e:
        logger.error(f"Error expiring old appeals in guild {guild_id}: {e}", exc_info=True)
        await db_conn.rollback()
        return 0

# --- AppealCog Class ---

class AppealCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = self.bot.db_conn # Assuming db_conn is set on bot instance
        self.auto_expire_appeals.start()

    def cog_unload(self):
        self.auto_expire_appeals.cancel()

    @tasks.loop(hours=24)
    async def auto_expire_appeals(self):
        logger.info("Starting daily check for old appeals to expire...")
        if not self.db_conn:
            logger.error("Auto-expire appeals: Database connection not available.")
            return

        for guild in self.bot.guilds:
            try:
                expired_count = await expire_old_appeals(self.db_conn, guild.id, days_old=7)
                if expired_count > 0:
                    logger.info(f"Auto-expired {expired_count} appeals in guild {guild.name} ({guild.id}).")
            except Exception as e:
                logger.error(f"Error during auto-expiration for guild {guild.id}: {e}", exc_info=True)
        logger.info("Finished daily check for old appeals.")

    @auto_expire_appeals.before_loop
    async def before_auto_expire_appeals(self):
        await self.bot.wait_until_ready()


    appeals_group = app_commands.Group(name="appeals", description="Manage moderation appeals.")

    @app_commands.command(name="appeal", description="Submit an appeal for a recent moderation action against you.")
    @app_commands.describe(
        action_id_appealed="The ID of the warning or action you are appealing (e.g., warn_123 or a longer UUID).",
        original_action_type="The type of action you are appealing (e.g., 'warning', 'timeout', 'ban').",
        reason="Briefly explain why you are appealing this action."
    )
    @app_commands.choices(original_action_type=[
        app_commands.Choice(name="Warning", value="warning"),
        app_commands.Choice(name="Timeout", value="timeout"),
        app_commands.Choice(name="Ban", value="ban"),
        app_commands.Choice(name="Other", value="other"),
    ])
    async def appeal_command(self, interaction: discord.Interaction, action_id_appealed: str, original_action_type: str, reason: str):
        # (Implementation from previous step, assumed to be correct and present)
        if not interaction.guild:
            await interaction.response.send_message("Appeals can only be made within a server.", ephemeral=True)
            return

        if not self.db_conn:
            logger.error("Database connection not available on bot object for appeal command.")
            await interaction.response.send_message("An internal error occurred. Please try again later.", ephemeral=True)
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:
            open_appeals = await get_user_open_appeals(self.db_conn, user_id, guild_id)
            if open_appeals:
                await interaction.response.send_message(
                    f"You already have an open appeal (ID: {open_appeals[0]['appeal_id']}). "
                    "Please wait for it to be processed before submitting another.",
                    ephemeral=True
                )
                return

            if len(reason) < 20 or len(reason) > 1024:
                await interaction.response.send_message("Your appeal reason must be between 20 and 1024 characters.", ephemeral=True)
                return

            appeal_id, appeal_submission_log_uuid = await log_appeal_submission(
                self.db_conn, user_id, guild_id, action_id_appealed, original_action_type, reason
            )

            if appeal_id and appeal_submission_log_uuid:
                await interaction.response.send_message(
                    f"Your appeal (ID: {appeal_id}) regarding action '{action_id_appealed}' has been submitted successfully. "
                    "Moderators will review it. You will be notified of the decision.",
                    ephemeral=True
                )
                mod_alert_channel_id = config.moderation.alert_channel_id
                if mod_alert_channel_id:
                    mod_channel = interaction.guild.get_channel(mod_alert_channel_id)
                    if mod_channel and isinstance(mod_channel, discord.TextChannel):
                        embed = discord.Embed(title="📢 New Appeal Submitted", description=f"A new appeal has been submitted by {interaction.user.mention} (`{user_id}`).", color=discord.Color.blue(), timestamp=datetime.datetime.now(datetime.timezone.utc))
                        embed.add_field(name="Appeal ID", value=str(appeal_id), inline=True)
                        embed.add_field(name="Action Appealed ID", value=action_id_appealed, inline=True)
                        embed.add_field(name="Action Type", value=original_action_type.capitalize(), inline=True)
                        embed.add_field(name="Reason Provided", value=reason, inline=False)
                        embed.set_footer(text=f"Guild ID: {guild_id}")
                        try:
                            await mod_channel.send(embed=embed)
                            mod_notify_log_id = str(uuid.uuid4())
                            await _log_appeal_related_action(self.db_conn, action_id=mod_notify_log_id, guild_id=guild_id, user_id=self.bot.user.id, action_type='APPEAL_MOD_NOTIFIED', reason=f"Moderators notified about new appeal ID {appeal_id} for user {user_id}.", target_user_id=user_id, related_appeal_id=appeal_id)
                        except discord.Forbidden: logger.error(f"Failed to send appeal notification to mod channel {mod_alert_channel_id} in guild {guild_id}: Missing permissions.")
                        except Exception as e: logger.error(f"Error sending appeal notification to mod channel {mod_alert_channel_id}: {e}", exc_info=True)
                    else: logger.warning(f"Moderator alert channel {mod_alert_channel_id} not found or not a text channel in guild {guild_id} for appeal notification.")
                else: logger.info(f"Moderator alert channel not configured. Skipping mod notification for appeal {appeal_id}.")
            else: await interaction.response.send_message("There was an error submitting your appeal. Please try again later or contact a moderator.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in /appeal command for user {user_id} in guild {guild_id}: {e}", exc_info=True)
            if not interaction.response.is_done(): await interaction.response.send_message("An unexpected error occurred while processing your appeal.", ephemeral=True)

    @appeals_group.command(name="list", description="List pending appeals for review.")
    @app_commands.checks.has_permissions(manage_messages=True) # Moderator check
    async def list_appeals(self, interaction: discord.Interaction):
        if not self.db_conn:
            await interaction.response.send_message("Database not connected.", ephemeral=True); return

        pending_list = await get_pending_appeals(self.db_conn, interaction.guild_id, limit=20)
        if not pending_list:
            await interaction.response.send_message("No pending appeals found.", ephemeral=True)
            return

        embed = discord.Embed(title="📝 Pending Appeals for Review", color=discord.Color.yellow(), timestamp=datetime.datetime.now(datetime.timezone.utc))
        embed.set_footer(text=f"Guild ID: {interaction.guild_id}")

        for appeal in pending_list:
            user = await self.bot.fetch_user(appeal['user_id']) # Fetch user for display name
            user_display = f"{user.name}#{user.discriminator}" if user else f"ID: {appeal['user_id']}"
            reason_preview = (appeal['reason'][:75] + '...') if len(appeal['reason']) > 75 else appeal['reason']
            embed.add_field(
                name=f"Appeal ID: {appeal['appeal_id']} (User: {user_display})",
                value=f"Action ID: `{appeal['action_id_appealed']}` (Type: {appeal['original_action_type']})\n"
                      f"Reason: *{reason_preview}*\n"
                      f"Submitted: {discord.utils.format_dt(appeal['timestamp'], style='R')}",
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @appeals_group.command(name="approve", description="Approve a pending appeal.")
    @app_commands.describe(appeal_id="The ID of the appeal to approve.", decision_reason="Optional reason for the approval decision.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def approve_appeal(self, interaction: discord.Interaction, appeal_id: int, decision_reason: str = "No specific reason provided by moderator."):
        if not self.db_conn: await interaction.response.send_message("Database not connected.", ephemeral=True); return

        appeal = await get_appeal_by_id(self.db_conn, appeal_id, interaction.guild_id)
        if not appeal: await interaction.response.send_message(f"Appeal ID {appeal_id} not found.", ephemeral=True); return
        if appeal['status'] != 'PENDING': await interaction.response.send_message(f"Appeal ID {appeal_id} is not pending (Status: {appeal['status']}).", ephemeral=True); return

        updated = await update_appeal_status(self.db_conn, appeal_id, interaction.guild_id, 'APPROVED', interaction.user.id)
        if not updated: await interaction.response.send_message("Failed to update appeal status in database.", ephemeral=True); return

        target_user_id = appeal['user_id']
        target_user = await self.bot.fetch_user(target_user_id)
        action_reversed_details = "No specific Discord action was automatically reversed."
        log_action_type_suffix = "_NO_AUTO_REVERSAL"

        # Attempt to reverse original action
        if appeal['original_action_type'] == 'timeout':
            try:
                member_to_untimeout = await interaction.guild.fetch_member(target_user_id) # Needs member object
                if member_to_untimeout:
                    await member_to_untimeout.timeout(None, reason=f"Appeal ID {appeal_id} approved by {interaction.user.name}.")
                    action_reversed_details = "User's timeout has been removed."
                    log_action_type_suffix = "_TIMEOUT_REMOVED"
                    logger.info(f"Timeout removed for user {target_user_id} due to approved appeal {appeal_id}.")
            except discord.Forbidden: action_reversed_details = "Failed to remove timeout: Bot lacks permissions."; logger.error(f"Failed to remove timeout for {target_user_id} (Appeal {appeal_id}): Forbidden.")
            except discord.HTTPException as e: action_reversed_details = f"Failed to remove timeout: API Error ({e.status})."; logger.error(f"Failed to remove timeout for {target_user_id} (Appeal {appeal_id}): HTTP {e.status} {e.text}")
            except Exception as e: action_reversed_details = "Failed to remove timeout: Unknown error."; logger.error(f"Failed to remove timeout for {target_user_id} (Appeal {appeal_id}): {e}", exc_info=True)
        elif appeal['original_action_type'] == 'ban':
            try:
                await interaction.guild.unban(discord.Object(id=target_user_id), reason=f"Appeal ID {appeal_id} approved by {interaction.user.name}.")
                action_reversed_details = "User has been unbanned."
                log_action_type_suffix = "_USER_UNBANNED"
                logger.info(f"User {target_user_id} unbanned due to approved appeal {appeal_id}.")
            except discord.Forbidden: action_reversed_details = "Failed to unban user: Bot lacks permissions."; logger.error(f"Failed to unban {target_user_id} (Appeal {appeal_id}): Forbidden")
            except discord.HTTPException as e: action_reversed_details = f"Failed to unban user: API Error ({e.status})."; logger.error(f"Failed to unban {target_user_id} (Appeal {appeal_id}): HTTP {e.status} {e.text}")
            except Exception as e: action_reversed_details = "Failed to unban user: Unknown error."; logger.error(f"Failed to unban {target_user_id} (Appeal {appeal_id}): {e}", exc_info=True)

        # Log approval and reversal attempt
        approval_log_id = str(uuid.uuid4())
        await _log_appeal_related_action(
            self.db_conn, action_id=approval_log_id, guild_id=interaction.guild_id, user_id=interaction.user.id,
            action_type=f'APPEAL_APPROVED{log_action_type_suffix}',
            reason=f"Moderator approved appeal for action {appeal['action_id_appealed']}. Decision: {decision_reason}. Reversal: {action_reversed_details}",
            moderator_id=interaction.user.id, target_user_id=target_user_id, related_appeal_id=appeal_id
        )

        # Notify user
        if target_user:
            try:
                dm_embed = discord.Embed(title="✅ Your Appeal Was Approved", color=discord.Color.green(), timestamp=datetime.datetime.now(datetime.timezone.utc))
                dm_embed.add_field(name="Appeal ID", value=str(appeal_id), inline=True)
                dm_embed.add_field(name="Original Action ID", value=appeal['action_id_appealed'], inline=True)
                dm_embed.add_field(name="Moderator's Reason", value=decision_reason, inline=False)
                dm_embed.add_field(name="Outcome", value=action_reversed_details, inline=False)
                dm_embed.set_footer(text=f"Guild: {interaction.guild.name}")
                await target_user.send(embed=dm_embed)
            except discord.Forbidden: logger.warning(f"Could not DM user {target_user_id} about appeal approval for appeal {appeal_id}.")
            except Exception as e: logger.error(f"Error DMing user {target_user_id} about appeal approval {appeal_id}: {e}", exc_info=True)

        await interaction.response.send_message(f"Appeal ID {appeal_id} approved. User notified. {action_reversed_details}", ephemeral=True)

    @appeals_group.command(name="deny", description="Deny a pending appeal.")
    @app_commands.describe(appeal_id="The ID of the appeal to deny.", decision_reason="Reason for the denial decision.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def deny_appeal(self, interaction: discord.Interaction, appeal_id: int, decision_reason: str):
        if not self.db_conn: await interaction.response.send_message("Database not connected.", ephemeral=True); return
        if not decision_reason or len(decision_reason) < 10: await interaction.response.send_message("Please provide a clear decision reason (min 10 characters).", ephemeral=True); return


        appeal = await get_appeal_by_id(self.db_conn, appeal_id, interaction.guild_id)
        if not appeal: await interaction.response.send_message(f"Appeal ID {appeal_id} not found.", ephemeral=True); return
        if appeal['status'] != 'PENDING': await interaction.response.send_message(f"Appeal ID {appeal_id} is not pending (Status: {appeal['status']}).", ephemeral=True); return

        updated = await update_appeal_status(self.db_conn, appeal_id, interaction.guild_id, 'DENIED', interaction.user.id)
        if not updated: await interaction.response.send_message("Failed to update appeal status in database.", ephemeral=True); return

        target_user_id = appeal['user_id']
        target_user = await self.bot.fetch_user(target_user_id)

        # Log denial
        denial_log_id = str(uuid.uuid4())
        await _log_appeal_related_action(
            self.db_conn, action_id=denial_log_id, guild_id=interaction.guild_id, user_id=interaction.user.id,
            action_type='APPEAL_DENIED', reason=f"Moderator denied appeal for action {appeal['action_id_appealed']}. Decision: {decision_reason}",
            moderator_id=interaction.user.id, target_user_id=target_user_id, related_appeal_id=appeal_id
        )

        # Notify user
        if target_user:
            try:
                dm_embed = discord.Embed(title="❌ Your Appeal Was Denied", color=discord.Color.red(), timestamp=datetime.datetime.now(datetime.timezone.utc))
                dm_embed.add_field(name="Appeal ID", value=str(appeal_id), inline=True)
                dm_embed.add_field(name="Original Action ID", value=appeal['action_id_appealed'], inline=True)
                dm_embed.add_field(name="Moderator's Reason", value=decision_reason, inline=False)
                dm_embed.set_footer(text=f"Guild: {interaction.guild.name}")
                await target_user.send(embed=dm_embed)
            except discord.Forbidden: logger.warning(f"Could not DM user {target_user_id} about appeal denial for appeal {appeal_id}.")
            except Exception as e: logger.error(f"Error DMing user {target_user_id} about appeal denial {appeal_id}: {e}", exc_info=True)

        await interaction.response.send_message(f"Appeal ID {appeal_id} denied. User notified.", ephemeral=True)


async def setup(bot):
    cog = AppealCog(bot)
    await bot.add_cog(cog)
    logger.info("AppealCog loaded successfully, including moderator commands and auto-expiration task.")
