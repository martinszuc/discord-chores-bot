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