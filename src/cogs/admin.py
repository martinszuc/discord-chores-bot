import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import datetime
from src.utils.strings import BotStrings

logger = logging.getLogger('chores-bot')


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    async def cog_check(self, ctx):
        """Check if the user has admin privileges."""
        # Get admin role ID from config
        admin_role_id = self.config.get("admin_role_id")

        # Check if the user has the admin role
        if admin_role_id and discord.utils.get(ctx.author.roles, id=admin_role_id):
            return True

        # If admin_role_id is not set, fall back to administrator permission
        return ctx.author.guild_permissions.administrator

    choresadmin = app_commands.Group(name="choresadmin", description="Administrative commands for the chores bot")

    @choresadmin.command(name="status")
    async def status(self, interaction: discord.Interaction):
        """Show the bot status."""
        # Get some stats about the bot
        embed = discord.Embed(
            title="📊 Bot Status",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Add system info
        embed.add_field(
            name="🖥️ System Info",
            value=f"Discord.py Version: {discord.__version__}\n"
                  f"Bot Uptime: {datetime.datetime.now() - self.bot.launched_at if hasattr(self.bot, 'launched_at') else 'Unknown'}\n"
                  f"Serving: {len(self.bot.guilds)} guild(s)",
            inline=False
        )

        # Add chores info
        chores_cog = self.bot.get_cog("ChoresCog")
        if chores_cog:
            schedule_manager = chores_cog.schedule_manager
            last_posted = schedule_manager.get_last_posted_date()
            last_posted_str = "Never" if not last_posted else last_posted

            embed.add_field(
                name="📊 Schedule Info",
                value=f"Last Posted: {last_posted_str}\n"
                      f"Chores: {len(self.config.get('chores', []))}\n"
                      f"Flatmates: {len(self.config.get('flatmates', []))}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @choresadmin.command(name="reload_config")
    async def reload_config(self, interaction: discord.Interaction):
        """Reload the bot configuration."""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.bot.config = json.load(f)
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_RELOADED)
        except Exception as e:
            logger.error(f"Failed to reload config: {e}")
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_FAILED.format(error=e))

    @choresadmin.command(name="test_notification")
    @app_commands.describe(chore="The chore to test notifications for (optional)")
    async def test_notification(self, interaction: discord.Interaction, chore: str = None):
        """Test the notification system by sending a test message."""
        chores_cog = self.bot.get_cog("ChoresCog")
        if not chores_cog:
            await interaction.response.send_message("❌ Chores cog not found.")
            return

        await interaction.response.send_message("Sending test notifications...")
        channel = interaction.channel

        if chore:
            # Test notification for specific chore
            assignments = chores_cog.schedule_manager.get_current_assignments()
            if chore not in assignments:
                await interaction.followup.send(f"❌ Chore '{chore}' not found in current assignments.")
                return

            flatmate_name = assignments.get(chore)
            flatmate = chores_cog.config_manager.get_flatmate_by_name(flatmate_name)
            if not flatmate:
                await interaction.followup.send(f"❌ Flatmate '{flatmate_name}' not found.")
                return

            discord_id = flatmate.get("discord_id")

            # Send test notification
            await interaction.followup.send(
                f"{BotStrings.ADMIN_TEST_NOTIFICATION}\n\n"
                f"Hey <@{discord_id}>, this is a test reminder for your chore: **{chore}**\n\n"
                f"Please remember to complete it and mark it as done with ✅"
            )
        else:
            # Test general notification for all chores
            assignments = chores_cog.schedule_manager.get_current_assignments()
            if not assignments:
                await interaction.followup.send(BotStrings.ERR_NO_ASSIGNMENTS)
                return

            # Send test header
            await interaction.followup.send(f"{BotStrings.ADMIN_TEST_NOTIFICATION}")

            # Send test instructions
            await interaction.followup.send(BotStrings.REACTION_INSTRUCTIONS)

            # Send individual test messages
            emojis = chores_cog.config_manager.get_emoji()
            for chore, flatmate_name in assignments.items():
                flatmate = chores_cog.config_manager.get_flatmate_by_name(flatmate_name)
                if not flatmate:
                    continue

                discord_id = flatmate.get("discord_id")

                # Create the test assignment message
                test_msg = BotStrings.TASK_ASSIGNMENT.format(
                    mention=f"<@{discord_id}>",
                    chore=chore
                )

                # Send message with reactions
                message = await channel.send(test_msg)
                await message.add_reaction(emojis["completed"])
                await message.add_reaction(emojis["unavailable"])

    @choresadmin.command(name="settings")
    @app_commands.describe(
        setting="The setting to view or update (optional)",
        value="The new value for the setting (optional)"
    )
    async def edit_settings(self, interaction: discord.Interaction, setting: str = None, value: str = None):
        """View or edit bot settings."""
        if not setting:
            # Show all settings
            embed = discord.Embed(
                title="⚙️ Bot Settings",
                description="Current bot settings. Use `/choresadmin settings setting:name value:new_value` to change a setting.",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )

            # Add general settings
            embed.add_field(
                name="General Settings",
                value=f"prefix: {self.config.get('prefix', '!')}\n"
                      f"chores_channel_id: {self.config.get('chores_channel_id', 'Not set')}\n"
                      f"admin_role_id: {self.config.get('admin_role_id', 'Not set')}",
                inline=False
            )

            # Add schedule settings
            embed.add_field(
                name="Schedule Settings",
                value=f"posting_day: {self.config.get('posting_day', 'Monday')}\n"
                      f"posting_time: {self.config.get('posting_time', '9:00')}\n"
                      f"timezone: {self.config.get('timezone', 'UTC')}",
                inline=False
            )

            await interaction.response.send_message(embed=embed)
            return

        # Check if setting exists
        valid_settings = [
            "prefix", "chores_channel_id", "admin_role_id",
            "posting_day", "posting_time", "timezone"
        ]

        if setting not in valid_settings:
            await interaction.response.send_message(BotStrings.SETTING_INVALID.format(
                setting=setting,
                valid_settings=", ".join(valid_settings)
            ))
            return

        if not value:
            # Show current value
            current_value = self.config.get(setting, "Not set")
            await interaction.response.send_message(BotStrings.SETTING_CURRENT.format(
                setting=setting,
                value=current_value
            ))
            return

        # Validate and convert values
        if setting == "chores_channel_id" or setting == "admin_role_id":
            try:
                value = int(value)
            except ValueError:
                await interaction.response.send_message(BotStrings.SETTING_INVALID_VALUE.format(
                    setting=setting,
                    reason="Must be a number."
                ))
                return

        elif setting == "posting_day":
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if value not in valid_days:
                await interaction.response.send_message(BotStrings.SETTING_INVALID_VALUE.format(
                    setting=setting,
                    reason=f"Must be one of: {', '.join(valid_days)}"
                ))
                return

        elif setting == "posting_time":
            # Validate time format (HH:MM)
            import re
            if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', value):
                await interaction.response.send_message(BotStrings.SETTING_INVALID_VALUE.format(
                    setting=setting,
                    reason="Must be in 24-hour format (HH:MM)."
                ))
                return

        # Update the setting
        try:
            self.config[setting] = value

            # Save the updated config
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            await interaction.response.send_message(BotStrings.SETTING_UPDATED.format(
                setting=setting,
                value=value
            ))

            # If it's a critical setting, suggest restarting the bot
            critical_settings = ["prefix", "chores_channel_id", "admin_role_id"]
            if setting in critical_settings:
                await interaction.followup.send(BotStrings.SETTING_CRITICAL_WARNING)

        except Exception as e:
            logger.error(f"Failed to update setting: {e}")
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_FAILED.format(error=e))


async def setup(bot):
    admin_cog = AdminCog(bot)
    await bot.add_cog(admin_cog)
    bot.tree.add_command(admin_cog.choresadmin)