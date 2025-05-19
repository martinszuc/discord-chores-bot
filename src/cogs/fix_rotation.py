import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('chores-bot')


class FixRotationCog(commands.Cog):
    def __init__(self, bot):
        logger.info("Initializing FixRotationCog")
        self.bot = bot
        self.config = bot.config
        logger.debug("FixRotationCog initialized successfully")

    async def cog_check(self, ctx):
        """Check if the user has admin privileges."""
        logger.debug(f"Checking admin privileges for user: {ctx.author.name} (ID: {ctx.author.id})")

        # Get admin role ID from config
        admin_role_id = self.config.get("admin_role_id")
        logger.debug(f"Admin role ID from config: {admin_role_id}")

        # Check if the user has the admin role
        if admin_role_id and discord.utils.get(ctx.author.roles, id=admin_role_id):
            logger.debug(f"User {ctx.author.name} has admin role")
            return True

        # If admin_role_id is not set, fall back to administrator permission
        has_admin_perm = ctx.author.guild_permissions.administrator
        logger.debug(f"User {ctx.author.name} has administrator permission: {has_admin_perm}")
        return has_admin_perm

    # Create a command group for the fix rotation command
    choresfix = app_commands.Group(name="choresfix", description="Commands to fix rotation issues")

    @choresfix.command(name="one_time_fix")
    async def one_time_fix(self, interaction: discord.Interaction):
        """One-time fix to ensure fair task rotation for next week."""
        logger.info(f"One-time fix command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        # Get the chores cog to access schedule manager
        chores_cog = self.bot.get_cog("ChoresCog")
        if not chores_cog:
            logger.error("Chores cog not found.")
            await interaction.response.send_message("❌ Internal error: Chores cog not found.")
            return

        # Run the one-time fix
        success, message = chores_cog.schedule_manager.special_one_time_rotation_fix()

        if success:
            await interaction.response.send_message(
                f"✅ **Rotation Fix Applied**\n\n{message}\n\nUse `/chores next` to generate the new schedule now.")
            logger.info("One-time rotation fix applied successfully")
        else:
            await interaction.response.send_message(f"❌ **Fix Failed**\n\n{message}")
            logger.warning(f"One-time rotation fix failed: {message}")

    @choresfix.command(name="reassign")
    @app_commands.describe(
        chore="The chore to reassign",
        new_assignee="The flatmate to reassign the chore to"
    )
    async def reassign_chore_no_penalty(self, interaction: discord.Interaction, chore: str, new_assignee: str):
        """Reassign a chore to another flatmate without affecting stats."""
        logger.info(
            f"No-penalty reassign command invoked by {interaction.user.name} (ID: {interaction.user.id}), chore: {chore}, new_assignee: {new_assignee}")

        # Get the chores cog to access schedule manager
        chores_cog = self.bot.get_cog("ChoresCog")
        if not chores_cog:
            logger.error("Chores cog not found.")
            await interaction.response.send_message("❌ Internal error: Chores cog not found.")
            return

        # Check if the chore exists
        current_assignments = chores_cog.schedule_manager.get_current_assignments()
        if chore not in current_assignments:
            await interaction.response.send_message(
                f"❌ Chore '{chore}' not found in current assignments. Available chores: {', '.join(current_assignments.keys())}")
            return

        # Check if the new assignee exists
        flatmate = chores_cog.config_manager.get_flatmate_by_name(new_assignee)
        if not flatmate:
            # Get all flatmates for suggestion
            all_flatmates = chores_cog.config_manager.get_flatmates()
            flatmate_names = [f["name"] for f in all_flatmates]
            await interaction.response.send_message(
                f"❌ Flatmate '{new_assignee}' not found. Available flatmates: {', '.join(flatmate_names)}")
            return

        # Get the current assignee
        current_assignee = current_assignments.get(chore)

        # Perform the reassignment without updating statistics
        success = chores_cog.schedule_manager.reassign_chore_without_penalty(chore, current_assignee, new_assignee)

        if success:
            await interaction.response.send_message(
                f"✅ Chore '{chore}' has been reassigned from {current_assignee} to {new_assignee} without affecting statistics.")

            # Get the chores channel to post notification
            channel_id = chores_cog.config_manager.get_chores_channel_id()
            channel = self.bot.get_channel(channel_id)

            if channel and channel.id != interaction.channel_id:
                # If we're not already in the chores channel, post there too
                discord_id = flatmate.get("discord_id")
                await channel.send(
                    f"⚠️ **Admin Reassignment**\n\nChore '**{chore}**' has been reassigned from {current_assignee} to <@{discord_id}> by {interaction.user.mention}.")

                # Add the standard reactions
                emojis = chores_cog.config_manager.get_emoji()
                message = await channel.send(f"Hey <@{discord_id}>, your chore for this week is: **{chore}**")
                await message.add_reaction(emojis["completed"])
                await message.add_reaction(emojis["unavailable"])

                # Add message to the cache for reaction handling
                chores_cog.message_cache[message.id] = (chore, new_assignee)

            logger.info(f"Chore '{chore}' reassigned from {current_assignee} to {new_assignee} without penalty")
        else:
            await interaction.response.send_message(f"❌ Failed to reassign chore '{chore}'.")
            logger.warning(f"Failed to reassign chore '{chore}' from {current_assignee} to {new_assignee}")


async def setup(bot):
    logger.info("Setting up FixRotationCog")
    fix_rotation_cog = FixRotationCog(bot)
    await bot.add_cog(fix_rotation_cog)
    try:
        logger.debug("Adding choresfix command group to the bot")
        bot.tree.add_command(fix_rotation_cog.choresfix)
        logger.info("FixRotationCog setup completed successfully")
    except Exception as e:
        # Command already registered, skip
        logger.warning(f"Skipping command registration: {e}")