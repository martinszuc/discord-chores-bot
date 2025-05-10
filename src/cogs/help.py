import discord
from discord import app_commands
from discord.ext import commands
import datetime
from src.utils.strings import BotStrings


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    choreshelp = app_commands.Group(name="choreshelp", description="Help commands for the chores bot")

    @choreshelp.command(name="show")
    @app_commands.describe(command="The specific command to get help with (optional)")
    async def help_command(self, interaction: discord.Interaction, command: str = None):
        """Show help information for the bot."""
        if command:
            # Call the appropriate help function based on the command parameter
            if command == "chores":
                await self.help_chores(interaction)
            elif command == "choresadmin":
                await self.help_admin(interaction)
            elif command == "reactions":
                await self.help_reactions(interaction)
            elif command == "status":
                await self.help_status(interaction)
            else:
                await interaction.response.send_message(f"No help available for command: {command}")
            return

        # General help
        embed = discord.Embed(
            title="🤖 Chores Bot Help",
            description=f"Welcome to the Chores Bot! Here's how to use me:",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Basic commands
        embed.add_field(
            name="📋 Basic Commands",
            value=f"`/chores` - Show the current chore schedule\n"
                  f"`/chores schedule` - Show the current chore schedule\n"
                  f"`/chores config` - Show the current configuration\n",
            inline=False
        )

        # Admin commands
        embed.add_field(
            name="⚙️ Admin Commands",
            value=f"`/choresadmin status` - Show bot status\n"
                  f"`/choresadmin reload_config` - Reload the configuration\n"
                  f"`/choresadmin test_notification` - Test notification system\n"
                  f"`/choresadmin settings` - View or edit bot settings\n",
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
                  f"Available command names: chores, choresadmin, reactions, status",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    async def help_chores(self, interaction: discord.Interaction):
        """Show help for chores commands."""
        embed = discord.Embed(
            title="📋 Chores Commands Help",
            description="Commands for managing chores and the chore schedule.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Basic commands
        embed.add_field(
            name="/chores",
            value="Show the current chore schedule.",
            inline=False
        )

        embed.add_field(
            name="/chores schedule",
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
            name="/chores add_chore name:chore_name",
            value="Add a new chore. (Admin only)",
            inline=False
        )

        embed.add_field(
            name="/chores remove_chore name:chore_name",
            value="Remove a chore. (Admin only)",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    async def help_admin(self, interaction: discord.Interaction):
        """Show help for admin commands."""
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

    async def help_reactions(self, interaction: discord.Interaction):
        """Show help for reaction usage."""
        emojis = self.config.get("emoji", {"completed": "✅", "unavailable": "❌"})

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

    async def help_status(self, interaction: discord.Interaction):
        """Show help for the status command."""
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
                  "- Number of chores and flatmates configured",
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


async def setup(bot):
    help_cog = HelpCog(bot)
    await bot.add_cog(help_cog)
    bot.tree.add_command(help_cog.choreshelp)