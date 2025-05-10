import discord
from discord.ext import commands
import datetime
from src.utils.strings import BotStrings


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.group(name="help", invoke_without_command=True)
    async def help_command(self, ctx):
        """Show help information for the bot."""
        prefix = self.config.get("prefix", "!")

        embed = discord.Embed(
            title="🤖 Chores Bot Help",
            description=f"Welcome to the Chores Bot! Here's how to use me:",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Basic commands
        embed.add_field(
            name="📋 Basic Commands",
            value=f"`{prefix}chores` - Show the current chore schedule\n"
                  f"`{prefix}chores schedule` - Show the current chore schedule\n"
                  f"`{prefix}chores config` - Show the current configuration\n",
            inline=False
        )

        # Admin commands
        embed.add_field(
            name="⚙️ Admin Commands",
            value=f"`{prefix}chores next` - Post the next chore schedule\n"
                  f"`{prefix}chores reset` - Reset the chore rotation\n"
                  f"`{prefix}chores add_flatmate <name> <discord_id>` - Add a new flatmate\n"
                  f"`{prefix}chores remove_flatmate <name>` - Remove a flatmate\n"
                  f"`{prefix}chores add_chore <chore_name>` - Add a new chore\n"
                  f"`{prefix}chores remove_chore <chore_name>` - Remove a chore\n",
            inline=False
        )

        # Advanced admin commands
        embed.add_field(
            name="🛠️ Advanced Admin Commands",
            value=f"`{prefix}admin status` - Show bot status\n"
                  f"`{prefix}admin reload` - Reload the configuration\n"
                  f"`{prefix}admin test [chore]` - Test notification system\n"
                  f"`{prefix}admin settings [setting] [value]` - View or edit bot settings\n",
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
            value=f"For more detailed help on a specific command, use `{prefix}help <command>`.",
            inline=False
        )

        await ctx.send(embed=embed)

    @help_command.command(name="chores")
    async def help_chores(self, ctx):
        """Show help for chores commands."""
        prefix = self.config.get("prefix", "!")

        embed = discord.Embed(
            title="📋 Chores Commands Help",
            description="Commands for managing chores and the chore schedule.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Basic commands
        embed.add_field(
            name=f"{prefix}chores",
            value="Show the current chore schedule.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores schedule",
            value="Show the current chore schedule.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores next",
            value="Post the next chore schedule immediately. (Admin only)",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores reset",
            value="Reset the chore rotation. (Admin only)",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores config",
            value="Show the current configuration.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores add_flatmate <name> <discord_id>",
            value="Add a new flatmate. (Admin only)",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores remove_flatmate <name>",
            value="Remove a flatmate. (Admin only)",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores add_chore <chore_name>",
            value="Add a new chore. (Admin only)",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}chores remove_chore <chore_name>",
            value="Remove a chore. (Admin only)",
            inline=False
        )

        await ctx.send(embed=embed)

    @help_command.command(name="admin")
    async def help_admin(self, ctx):
        """Show help for admin commands."""
        prefix = self.config.get("prefix", "!")

        embed = discord.Embed(
            title="⚙️ Admin Commands Help",
            description="Administrative commands for managing the bot.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Admin commands
        embed.add_field(
            name=f"{prefix}admin status",
            value="Show the bot status.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}admin reload",
            value="Reload the bot configuration.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}admin test [chore]",
            value="Test the notification system by sending a test message. "
                  "If a chore is specified, it will only test that chore.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}admin settings",
            value="View all bot settings.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}admin settings <setting>",
            value="View the value of a specific setting.",
            inline=False
        )

        embed.add_field(
            name=f"{prefix}admin settings <setting> <value>",
            value="Change the value of a specific setting.",
            inline=False
        )

        await ctx.send(embed=embed)

    @help_command.command(name="reactions")
    async def help_reactions(self, ctx):
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

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))