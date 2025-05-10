import discord
from discord import app_commands
from discord.ext import commands
import datetime
import logging
from src.utils.strings import BotStrings

logger = logging.getLogger('chores-bot')


class HelpCog(commands.Cog):
    def __init__(self, bot):
        logger.info("Initializing HelpCog")
        self.bot = bot
        self.config = bot.config
        logger.debug("HelpCog initialized successfully")

    choreshelp = app_commands.Group(name="choreshelp", description="Help commands for the chores bot")

    @choreshelp.command(name="show")
    @app_commands.describe(command="The specific command to get help with (optional)")
    async def help_command(self, interaction: discord.Interaction, command: str = None):
        """Show help information for the bot."""
        logger.info(f"Help command invoked by {interaction.user.name} (ID: {interaction.user.id}), command: {command}")

        if command:
            # Call the appropriate help function based on the command parameter
            logger.debug(f"Help requested for specific command: {command}")
            if command == "chores":
                await self.help_chores(interaction)
            elif command == "choresadmin":
                await self.help_admin(interaction)
            elif command == "reactions":
                await self.help_reactions(interaction)
            elif command == "status":
                await self.help_status(interaction)
            elif command == "vacation":
                await self.help_vacation(interaction)
            elif command == "statistics":
                await self.help_statistics(interaction)
            elif command == "difficulty":
                await self.help_difficulty(interaction)
            elif command == "reminders":
                await self.help_reminders(interaction)
            elif command == "next_week":
                await self.help_next_week(interaction)
            else:
                logger.warning(f"Help requested for unknown command: {command}")
                await interaction.response.send_message(f"No help available for command: {command}")
            return

        # General help
        logger.debug("Showing general help information")
        embed = discord.Embed(
            title="🤖 Chores Bot Help",
            description=f"Welcome to the Chores Bot! Here's how to use me:",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Basic commands
        embed.add_field(
            name="📋 Basic Commands",
            value=f"`/chores show` - Show the current chore schedule\n"
                  f"`/chores config` - Show the current configuration\n"
                  f"`/chores vacation status:True/False [user:@user]` - Enable/disable vacation mode for yourself or someone else\n"
                  f"`/chores next_week` - Plan who will be included in next week's chore rotation\n"
                  f"`/chores stats [name]` - Show your statistics or another flatmate's",
            inline=False
        )

        # Admin commands
        embed.add_field(
            name="⚙️ Admin Commands",
            value=f"`/choresadmin status` - Show bot status\n"
                  f"`/choresadmin reminders` - Configure reminder settings\n"
                  f"`/choresadmin test_reminder` - Test the reminder system\n"
                  f"`/choresadmin stats_summary` - Show statistics for all flatmates\n"
                  f"`/chores set_difficulty chore:X difficulty:Y` - Set difficulty for chore\n"
                  f"`/chores vote_difficulty chore:X` - Start a vote on chore difficulty",
            inline=False
        )

        # Reactions
        emojis = self.config.get("emoji", {"completed": "✅", "unavailable": "❌"})
        embed.add_field(
            name="👍 Reaction Usage",
            value=f"{emojis['completed']} - Mark a chore as completed\n"
                  f"{emojis['unavailable']} - Indicate you cannot complete a chore (will be randomly reassigned)\n",
            inline=False
        )

        # Instructions for more help
        embed.add_field(
            name="📚 More Help",
            value=f"For more detailed help on a specific command, use `/choreshelp show command:command_name`.\n"
                  f"Available command names: chores, choresadmin, reactions, status, vacation, statistics, difficulty, reminders, next_week",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("General help information displayed")

    async def help_chores(self, interaction: discord.Interaction):
        """Show help for chores commands."""
        logger.info(f"Chores help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="📋 Chores Commands Help",
            description="Commands for managing chores and the chore schedule.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Basic commands
        embed.add_field(
            name="/chores show",
            value="Show the current chore schedule.",
            inline=False
        )

        embed.add_field(
            name="/chores next",
            value="Post the next chore schedule immediately. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores reset",
            value="Reset the chore rotation. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores config",
            value="Show the current configuration.",
            inline=False
        )

        embed.add_field(
            name="/chores add_flatmate name:name discord_id:id",
            value="Add a new flatmate. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores remove_flatmate name:name",
            value="Remove a flatmate. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores add_chore name:chore_name difficulty:1-5",
            value="Add a new chore with optional difficulty level. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores remove_chore name:chore_name",
            value="Remove a chore. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores vacation status:True/False [user:@user]",
            value="Enable or disable vacation mode for yourself or another flatmate.",
            inline=False
        )

        embed.add_field(
            name="/chores stats name:flatmate_name",
            value="Show statistics for yourself or another flatmate.",
            inline=False
        )

        embed.add_field(
            name="/chores set_difficulty chore:chore_name difficulty:1-5",
            value="Set the difficulty level for a chore. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores vote_difficulty chore:chore_name",
            value="Start a vote on the difficulty of a chore.",
            inline=False
        )

        embed.add_field(
            name="/chores next_week",
            value="Show and plan who will be included in next week's chore rotation. React with numbers to toggle inclusion/exclusion.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Chores commands help displayed")

    async def help_admin(self, interaction: discord.Interaction):
        """Show help for admin commands."""
        logger.info(f"Admin help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="⚙️ Admin Commands Help",
            description="Administrative commands for managing the bot.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Admin commands
        embed.add_field(
            name="/choresadmin status",
            value="Show the bot status.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin reload_config",
            value="Reload the bot configuration.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin test_notification chore:chore_name",
            value="Test the notification system by sending a test message. "
                  "If a chore is specified, it will only test that chore.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin test_reminder",
            value="Test the reminder system by sending reminders for all pending chores.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin reminders",
            value="Show the current reminder settings.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin reminders status:True/False day:Day time:HH:MM",
            value="Configure the reminder system.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin stats_summary",
            value="Show a summary of statistics for all flatmates.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin settings",
            value="View all bot settings.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin settings setting:setting_name",
            value="View the value of a specific setting.",
            inline=False
        )

        embed.add_field(
            name="/choresadmin settings setting:setting_name value:new_value",
            value="Change the value of a specific setting.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Admin commands help displayed")

    async def help_reactions(self, interaction: discord.Interaction):
        """Show help for reaction usage."""
        logger.info(f"Reactions help requested by {interaction.user.name} (ID: {interaction.user.id})")

        emojis = self.config.get("emoji", {"completed": "✅", "unavailable": "❌"})
        logger.debug(f"Using emojis: {emojis}")

        embed = discord.Embed(
            title="👍 Reaction Usage Help",
            description="How to use reactions with the chore schedule.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Reactions
        embed.add_field(
            name=f"{emojis['completed']} Mark as Completed",
            value="React with this emoji to mark your assigned chore as completed.",
            inline=False
        )

        embed.add_field(
            name=f"{emojis['unavailable']} Cannot Complete",
            value="React with this emoji to indicate you cannot complete your assigned chore. "
                  "The chore will be automatically reassigned to a random flatmate who hasn't voted this week.",
            inline=False
        )

        # Add some examples
        embed.add_field(
            name="📝 Examples",
            value="1. The bot will send you a personal message with your assigned chore.\n"
                  "2. After completing the chore, react with ✅ to mark it as done.\n"
                  "3. If you're unable to complete the chore (e.g., you're away), react with ❌.\n"
                  "4. When you react with ❌, the bot will automatically assign the chore to someone else who hasn't already completed or declined a task this week.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Reactions help displayed")

    async def help_status(self, interaction: discord.Interaction):
        """Show help for the status command."""
        logger.info(f"Status help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="📊 Status Command Help",
            description="The `/choresadmin status` command displays information about the bot's current state.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="What it shows",
            value="- Discord.py Version\n"
                  "- Bot Uptime\n"
                  "- Number of servers the bot is in\n"
                  "- When the chore schedule was last posted\n"
                  "- Number of chores and flatmates configured\n"
                  "- Number of pending and completed chores\n"
                  "- Number of active flatmates (not on vacation)\n"
                  "- Current reminder settings",
            inline=False
        )

        embed.add_field(
            name="Usage",
            value="Simply type `/choresadmin status` to see the current bot status.",
            inline=False
        )

        embed.add_field(
            name="Permissions",
            value="This command requires administrator permissions or the configured admin role.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Status help displayed")

    async def help_vacation(self, interaction: discord.Interaction):
        """Show help for vacation mode."""
        logger.info(f"Vacation help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="🏖️ Vacation Mode Help",
            description="Vacation mode allows flatmates to be excluded from chore assignments when they are away.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="Enabling vacation mode for yourself",
            value="`/chores vacation status:True`\n\n"
                  "When you enable vacation mode, you will not be assigned any chores in the next schedule generation.",
            inline=False
        )

        embed.add_field(
            name="Disabling vacation mode for yourself",
            value="`/chores vacation status:False`\n\n"
                  "When you disable vacation mode, you will be included in the next schedule generation.\n"
                  "Additionally, you will be given higher priority to be assigned chores when you return.",
            inline=False
        )

        embed.add_field(
            name="Setting vacation mode for others",
            value="`/chores vacation status:True user:@username`\n\n"
                  "You can set vacation mode for other flatmates by mentioning them with the user parameter.\n"
                  "This is useful when someone forgets to set their own status before going away.",
            inline=False
        )

        embed.add_field(
            name="Checking vacation status",
            value="Use `/chores config` to see which flatmates are currently on vacation.",
            inline=False
        )

        embed.add_field(
            name="Temporary exclusion from rotation",
            value="If you want to exclude someone from just the next rotation (not full vacation mode),\n"
                  "use `/chores next_week` and react to toggle their inclusion status.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Vacation help displayed")

    async def help_statistics(self, interaction: discord.Interaction):
        """Show help for statistics commands."""
        logger.info(f"Statistics help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="📊 Statistics Commands Help",
            description="Commands for viewing chore completion statistics.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="Viewing your own statistics",
            value="`/chores stats`\n\n"
                  "Shows your personal statistics including completed chores, reassigned chores, skipped chores, and completion rate.",
            inline=False
        )

        embed.add_field(
            name="Viewing another flatmate's statistics",
            value="`/chores stats name:flatmate_name`\n\n"
                  "Shows statistics for the specified flatmate.",
            inline=False
        )

        embed.add_field(
            name="Viewing all flatmates' statistics",
            value="`/choresadmin stats_summary`\n\n"
                  "Shows a summary of statistics for all flatmates. This command requires admin permissions.",
            inline=False
        )

        embed.add_field(
            name="How statistics affect chore assignment",
            value="The bot uses statistics to prioritize chore assignments:\n\n"
                  "- Flatmates who skip chores often are more likely to be assigned chores\n"
                  "- Flatmates who complete chores regularly are less likely to be assigned difficult chores\n"
                  "- Flatmates who just returned from vacation are given priority for easier chores",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Statistics help displayed")

    async def help_difficulty(self, interaction: discord.Interaction):
        """Show help for chore difficulty commands."""
        logger.info(f"Difficulty help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="⭐ Chore Difficulty Help",
            description="Commands for managing chore difficulty ratings.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="Setting difficulty directly (Admin)",
            value="`/chores set_difficulty chore:chore_name difficulty:1-5`\n\n"
                  "Sets the difficulty level for a chore from 1 (easiest) to 5 (hardest).",
            inline=False
        )

        embed.add_field(
            name="Voting on chore difficulty",
            value="`/chores vote_difficulty chore:chore_name`\n\n"
                  "Starts a vote where flatmates can react with 1️⃣ to 5️⃣ to indicate how difficult they think the chore is.\n"
                  "After 5 minutes, the average vote will be used as the new difficulty level.",
            inline=False
        )

        embed.add_field(
            name="Viewing chore difficulties",
            value="Use `/chores config` to see the difficulty levels for all chores.\n"
                  "Each ⭐ represents one level of difficulty.",
            inline=False
        )

        embed.add_field(
            name="How difficulty affects assignments",
            value="Chores are assigned in order of difficulty (highest first) with the bot trying to balance the total difficulty each flatmate receives.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Difficulty help displayed")

    async def help_reminders(self, interaction: discord.Interaction):
        """Show help for reminder commands."""
        logger.info(f"Reminders help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="⏰ Reminders Help",
            description="Commands for managing the chore reminder system.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="Viewing reminder settings",
            value="`/choresadmin reminders`\n\n"
                  "Shows the current reminder settings including whether reminders are enabled, and when they are sent.",
            inline=False
        )

        embed.add_field(
            name="Enabling/disabling reminders",
            value="`/choresadmin reminders status:True/False`\n\n"
                  "Enables or disables the reminder system.",
            inline=False
        )

        embed.add_field(
            name="Changing reminder day",
            value="`/choresadmin reminders day:DayName`\n\n"
                  "Sets the day of the week when reminders are sent (e.g., Friday).",
            inline=False
        )

        embed.add_field(
            name="Changing reminder time",
            value="`/choresadmin reminders time:HH:MM`\n\n"
                  "Sets the time when reminders are sent in 24-hour format.",
            inline=False
        )

        embed.add_field(
            name="Testing reminders",
            value="`/choresadmin test_reminder`\n\n"
                  "Sends test reminders for all pending chores immediately.",
            inline=False
        )

        embed.add_field(
            name="How reminders work",
            value="The bot will automatically send reminders to flatmates who haven't completed their chores yet.\n"
                  "By default, reminders are sent on Friday at 18:00.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Reminders help displayed")

    async def help_next_week(self, interaction: discord.Interaction):
        """Show help for next week planning command."""
        logger.info(f"Next week planning help requested by {interaction.user.name} (ID: {interaction.user.id})")

        embed = discord.Embed(
            title="🗓️ Next Week Planning Help",
            description="The next week planning feature allows you to manage who will be included in the next chore rotation.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="Viewing next week's rotation plan",
            value="`/chores next_week`\n\n"
                  "Shows all active flatmates (those not on vacation) and whether they're included or excluded from the next rotation.",
            inline=False
        )

        embed.add_field(
            name="Excluding a flatmate from next rotation",
            value="React with the number emoji next to a flatmate's name to toggle their exclusion status.\n"
                  "This is a temporary exclusion just for the next schedule generation, not the same as vacation mode.",
            inline=False
        )

        embed.add_field(
            name="Including a previously excluded flatmate",
            value="React with the number emoji next to a flatmate who is currently marked as excluded to include them again.",
            inline=False
        )

        embed.add_field(
            name="Important notes",
            value="- Exclusions from next week's rotation are cleared after the schedule is generated\n"
                  "- This feature is best used right before a new schedule is generated\n"
                  "- All flatmates can use this feature, not just admins\n"
                  "- You can see who's currently excluded in the `/chores config` command",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info("Next week planning help displayed")


async def setup(bot):
    logger.info("Setting up HelpCog")
    help_cog = HelpCog(bot)
    await bot.add_cog(help_cog)
    try:
        logger.debug("Adding choreshelp command group to the bot")
        bot.tree.add_command(help_cog.choreshelp)
        logger.info("HelpCog setup completed successfully")
    except Exception as e:
        # Command already registered, skip
        logger.warning(f"Skipping command registration: {e}")