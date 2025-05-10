import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import datetime
import re
from src.utils.strings import BotStrings

logger = logging.getLogger('chores-bot')


class AdminCog(commands.Cog):
    def __init__(self, bot):
        logger.info("Initializing AdminCog")
        self.bot = bot
        self.config = bot.config
        logger.debug("AdminCog initialized")

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

    choresadmin = app_commands.Group(name="choresadmin", description="Administrative commands for the chores bot")

    @choresadmin.command(name="status")
    async def status(self, interaction: discord.Interaction):
        """Show the bot status."""
        logger.info(f"Admin status command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        # Get some stats about the bot
        embed = discord.Embed(
            title="📊 Bot Status",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Add system info
        uptime = datetime.datetime.now() - self.bot.launched_at if hasattr(self.bot, 'launched_at') else 'Unknown'
        guilds_count = len(self.bot.guilds)

        logger.debug(f"Bot uptime: {uptime}, Serving {guilds_count} guild(s)")

        embed.add_field(
            name="🖥️ System Info",
            value=f"Discord.py Version: {discord.__version__}\n"
                  f"Bot Uptime: {uptime}\n"
                  f"Serving: {guilds_count} guild(s)",
            inline=False
        )

        # Add chores info
        chores_cog = self.bot.get_cog("ChoresCog")
        if chores_cog:
            logger.debug("Getting schedule info from ChoresCog")
            schedule_manager = chores_cog.schedule_manager
            last_posted = schedule_manager.get_last_posted_date()
            last_posted_str = "Never" if not last_posted else last_posted
            logger.debug(f"Last posted: {last_posted_str}")

            # Get count of active flatmates (not on vacation)
            active_flatmates = chores_cog.config_manager.get_active_flatmates()
            total_flatmates = chores_cog.config_manager.get_flatmates()
            logger.debug(f"Active flatmates: {len(active_flatmates)}/{len(total_flatmates)}")

            # Get pending chores
            pending_chores = schedule_manager.get_pending_chores()
            pending_count = len(pending_chores)
            total_chores = len(self.config.get('chores', []))
            completed_count = total_chores - pending_count
            logger.debug(f"Chores - Total: {total_chores}, Completed: {completed_count}, Pending: {pending_count}")

            embed.add_field(
                name="📊 Schedule Info",
                value=f"Last Posted: {last_posted_str}\n"
                      f"Chores: {total_chores} (Completed: {completed_count}, Pending: {pending_count})\n"
                      f"Flatmates: {len(total_flatmates)} (Active: {len(active_flatmates)})",
                inline=False
            )

            # Add reminder status
            reminder_settings = chores_cog.config_manager.get_reminder_settings()
            reminder_status = "Enabled" if reminder_settings.get("enabled", True) else "Disabled"
            logger.debug(f"Reminder status: {reminder_status}")

            embed.add_field(
                name="⏰ Reminder Settings",
                value=f"Status: {reminder_status}\n"
                      f"Day: {reminder_settings.get('day', 'Friday')}\n"
                      f"Time: {reminder_settings.get('time', '18:00')}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)
        logger.info("Status command executed successfully")

    @choresadmin.command(name="reload_config")
    async def reload_config(self, interaction: discord.Interaction):
        """Reload the bot configuration."""
        logger.info(f"Reload config command invoked by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            logger.debug("Attempting to reload config from config.json")
            with open('config.json', 'r', encoding='utf-8') as f:
                self.bot.config = json.load(f)
            logger.info("Config reloaded successfully")
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_RELOADED)
        except FileNotFoundError:
            error_msg = "Config file not found"
            logger.error(error_msg)
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_FAILED.format(error=error_msg))
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in config file: {e}"
            logger.error(error_msg)
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_FAILED.format(error=error_msg))
        except Exception as e:
            logger.error(f"Failed to reload config: {e}", exc_info=True)
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_FAILED.format(error=e))

    @choresadmin.command(name="test_notification")
    @app_commands.describe(chore="The chore to test notifications for (optional)")
    async def test_notification(self, interaction: discord.Interaction, chore: str = None):
        """Test the notification system by sending a test message."""
        logger.info(
            f"Test notification command invoked by {interaction.user.name} (ID: {interaction.user.id}), chore: {chore}")

        chores_cog = self.bot.get_cog("ChoresCog")
        if not chores_cog:
            logger.error("Chores cog not found.")
            await interaction.response.send_message("❌ Chores cog not found.")
            return

        await interaction.response.send_message("Sending test notifications...")
        channel = interaction.channel
        logger.debug(f"Using channel: {channel.name} (ID: {channel.id})")

        if chore:
            logger.debug(f"Testing notification for specific chore: {chore}")
            # Test notification for specific chore
            assignments = chores_cog.schedule_manager.get_current_assignments()
            if chore not in assignments:
                logger.warning(f"Chore '{chore}' not found in current assignments")
                await interaction.followup.send(f"❌ Chore '{chore}' not found in current assignments.")
                return

            flatmate_name = assignments.get(chore)
            flatmate = chores_cog.config_manager.get_flatmate_by_name(flatmate_name)
            if not flatmate:
                logger.warning(f"Flatmate '{flatmate_name}' not found")
                await interaction.followup.send(f"❌ Flatmate '{flatmate_name}' not found.")
                return

            discord_id = flatmate.get("discord_id")
            logger.debug(f"Sending test notification to {flatmate_name} (ID: {discord_id}) for chore: {chore}")

            # Send test notification
            await interaction.followup.send(
                f"{BotStrings.ADMIN_TEST_NOTIFICATION}\n\n"
                f"Hey <@{discord_id}>, this is a test reminder for your chore: **{chore}**\n\n"
                f"Please remember to complete it and mark it as done with ✅"
            )
            logger.info(f"Test notification sent for chore '{chore}' to {flatmate_name}")
        else:
            logger.debug("Testing general notification for all chores")
            # Test general notification for all chores
            assignments = chores_cog.schedule_manager.get_current_assignments()
            if not assignments:
                logger.warning("No current assignments found")
                await interaction.followup.send(BotStrings.ERR_NO_ASSIGNMENTS)
                return

            # Send test header
            await interaction.followup.send(f"{BotStrings.ADMIN_TEST_NOTIFICATION}")
            logger.debug("Sent test notification header")

            # Send test instructions
            await interaction.followup.send(BotStrings.REACTION_INSTRUCTIONS)
            logger.debug("Sent reaction instructions")

            # Send individual test messages
            emojis = chores_cog.config_manager.get_emoji()
            for chore, flatmate_name in assignments.items():
                flatmate = chores_cog.config_manager.get_flatmate_by_name(flatmate_name)
                if not flatmate:
                    logger.warning(f"Flatmate '{flatmate_name}' not found for chore: {chore}")
                    continue

                discord_id = flatmate.get("discord_id")
                logger.debug(f"Sending test assignment for '{chore}' to {flatmate_name} (ID: {discord_id})")

                # Create the test assignment message
                test_msg = BotStrings.TASK_ASSIGNMENT.format(
                    mention=f"<@{discord_id}>",
                    chore=chore
                )

                # Send message with reactions
                message = await channel.send(test_msg)
                await message.add_reaction(emojis["completed"])
                await message.add_reaction(emojis["unavailable"])
                logger.debug(f"Sent test message ID: {message.id} for chore '{chore}'")

            logger.info("All test notifications sent successfully")

    @choresadmin.command(name="test_reminder")
    async def test_reminder(self, interaction: discord.Interaction):
        """Test the reminder system by sending reminders for all pending chores."""
        logger.info(f"Test reminder command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        chores_cog = self.bot.get_cog("ChoresCog")
        if not chores_cog:
            logger.error("Chores cog not found.")
            await interaction.response.send_message("❌ Chores cog not found.")
            return

        await interaction.response.send_message("Sending test reminders...")
        logger.debug(f"Using channel: {interaction.channel.name} (ID: {interaction.channel.id})")

        await chores_cog.send_reminders(interaction.channel)
        logger.info("Test reminders sent successfully")

    @choresadmin.command(name="reminders")
    @app_commands.describe(
        status="Enable or disable reminders",
        day="Day to send reminders (optional)",
        time="Time to send reminders (HH:MM) (optional)"
    )
    async def configure_reminders(self, interaction: discord.Interaction, status: bool = None,
                                  day: str = None, time: str = None):
        """Configure the reminder system."""
        logger.info(
            f"Configure reminders command invoked by {interaction.user.name} (ID: {interaction.user.id}), status: {status}, day: {day}, time: {time}")

        chores_cog = self.bot.get_cog("ChoresCog")
        if not chores_cog:
            logger.error("Chores cog not found.")
            await interaction.response.send_message("❌ Chores cog not found.")
            return

        # If no parameters provided, show current settings
        if status is None and day is None and time is None:
            logger.debug("No parameters provided, showing current settings")
            reminder_settings = chores_cog.config_manager.get_reminder_settings()
            reminder_status = "Enabled" if reminder_settings.get("enabled", True) else "Disabled"
            logger.debug(f"Current reminder settings: {reminder_settings}")

            embed = discord.Embed(
                title="⏰ Reminder Settings",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )

            embed.add_field(
                name="Current Settings",
                value=f"Status: {reminder_status}\n"
                      f"Day: {reminder_settings.get('day', 'Friday')}\n"
                      f"Time: {reminder_settings.get('time', '18:00')}",
                inline=False
            )

            embed.add_field(
                name="Usage",
                value=f"To update settings, use:\n"
                      f"`/choresadmin reminders status:True/False day:Day time:HH:MM`",
                inline=False
            )

            await interaction.response.send_message(embed=embed)
            logger.info("Displayed current reminder settings")
            return

        # Validate day if provided
        if day is not None:
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if day not in valid_days:
                logger.warning(f"Invalid day provided: {day}")
                await interaction.response.send_message(f"❌ Invalid day. Must be one of: {', '.join(valid_days)}")
                return

        # Validate time if provided
        if time is not None:
            if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time):
                logger.warning(f"Invalid time format provided: {time}")
                await interaction.response.send_message("❌ Invalid time format. Must be in 24-hour format (HH:MM).")
                return

        # Update reminder settings
        logger.debug(f"Updating reminder settings: status={status}, day={day}, time={time}")
        success, message = chores_cog.config_manager.update_reminder_settings(
            enabled=status,
            day=day,
            time=time
        )

        if success:
            logger.info("Reminder settings updated successfully")
            reminder_settings = chores_cog.config_manager.get_reminder_settings()
            if status is not None:
                if status:
                    logger.debug("Reminders enabled")
                    await interaction.response.send_message(
                        BotStrings.REMINDER_ENABLED.format(
                            day=reminder_settings.get('day', 'Friday'),
                            time=reminder_settings.get('time', '11:00')
                        )
                    )
                else:
                    logger.debug("Reminders disabled")
                    await interaction.response.send_message(BotStrings.REMINDER_DISABLED)
            else:
                await interaction.response.send_message(BotStrings.REMINDER_SETTINGS_UPDATED)
        else:
            logger.error(f"Failed to update reminder settings: {message}")
            await interaction.response.send_message(f"❌ Failed to update reminder settings: {message}")

    @choresadmin.command(name="settings")
    @app_commands.describe(
        setting="The setting to view or update (optional)",
        value="The new value for the setting (optional)"
    )
    async def edit_settings(self, interaction: discord.Interaction, setting: str = None, value: str = None):
        """View or edit bot settings."""
        logger.info(
            f"Edit settings command invoked by {interaction.user.name} (ID: {interaction.user.id}), setting: {setting}, value: {value}")

        if not setting:
            # Show all settings
            logger.debug("No setting specified, showing all settings")
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

            # Add reminder settings
            reminder_settings = self.config.get('reminders', {
                'enabled': True,
                'day': 'Friday',
                'time': '18:00'
            })
            embed.add_field(
                name="Reminder Settings",
                value=f"reminders.enabled: {reminder_settings.get('enabled', True)}\n"
                      f"reminders.day: {reminder_settings.get('day', 'Friday')}\n"
                      f"reminders.time: {reminder_settings.get('time', '18:00')}",
                inline=False
            )

            await interaction.response.send_message(embed=embed)
            logger.info("Displayed all settings")
            return

        # Check if setting exists
        valid_settings = [
            "prefix", "chores_channel_id", "admin_role_id",
            "posting_day", "posting_time", "timezone"
        ]

        if setting not in valid_settings:
            logger.warning(f"Invalid setting: {setting}")
            await interaction.response.send_message(BotStrings.SETTING_INVALID.format(
                setting=setting,
                valid_settings=", ".join(valid_settings)
            ))
            return

        if not value:
            # Show current value
            logger.debug(f"Showing current value for setting: {setting}")
            current_value = self.config.get(setting, "Not set")
            await interaction.response.send_message(BotStrings.SETTING_CURRENT.format(
                setting=setting,
                value=current_value
            ))
            return

        # Validate and convert values
        if setting == "chores_channel_id" or setting == "admin_role_id":
            try:
                logger.debug(f"Converting {setting} value to integer: {value}")
                value = int(value)
            except ValueError:
                logger.warning(f"Invalid value for {setting}: {value} - must be a number")
                await interaction.response.send_message(BotStrings.SETTING_INVALID_VALUE.format(
                    setting=setting,
                    reason="Must be a number."
                ))
                return

        elif setting == "posting_day":
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if value not in valid_days:
                logger.warning(f"Invalid value for {setting}: {value} - must be a valid day")
                await interaction.response.send_message(BotStrings.SETTING_INVALID_VALUE.format(
                    setting=setting,
                    reason=f"Must be one of: {', '.join(valid_days)}"
                ))
                return

        elif setting == "posting_time":
            # Validate time format (HH:MM)
            if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', value):
                logger.warning(f"Invalid value for {setting}: {value} - must be in HH:MM format")
                await interaction.response.send_message(BotStrings.SETTING_INVALID_VALUE.format(
                    setting=setting,
                    reason="Must be in 24-hour format (HH:MM)."
                ))
                return

        # Update the setting
        try:
            logger.info(f"Updating setting {setting} to {value}")
            old_value = self.config.get(setting, "Not set")
            self.config[setting] = value

            # Save the updated config
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Setting updated and saved to config file: {setting} = {value}")

            await interaction.response.send_message(BotStrings.SETTING_UPDATED.format(
                setting=setting,
                value=value
            ))

            # If it's a critical setting, suggest restarting the bot
            critical_settings = ["prefix", "chores_channel_id", "admin_role_id"]
            if setting in critical_settings:
                logger.warning(f"Critical setting {setting} changed from {old_value} to {value}")
                await interaction.followup.send(BotStrings.SETTING_CRITICAL_WARNING)

        except Exception as e:
            logger.error(f"Failed to update setting: {e}", exc_info=True)
            await interaction.response.send_message(BotStrings.ADMIN_CONFIG_FAILED.format(error=e))

    @choresadmin.command(name="stats_summary")
    async def stats_summary(self, interaction: discord.Interaction):
        """Show a summary of stats for all flatmates."""
        logger.info(f"Stats summary command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        chores_cog = self.bot.get_cog("ChoresCog")
        if not chores_cog:
            logger.error("Chores cog not found.")
            await interaction.response.send_message("❌ Chores cog not found.")
            return

        # Get all flatmates
        flatmates = chores_cog.config_manager.get_flatmates()
        logger.debug(f"Found {len(flatmates)} flatmates")

        embed = discord.Embed(
            title="📊 Statistics Summary",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        for flatmate in flatmates:
            stats = chores_cog.config_manager.get_flatmate_stats(flatmate["name"])
            if not stats:
                logger.warning(f"No stats found for flatmate: {flatmate['name']}")
                continue

            # Calculate completion rate
            total_chores = stats["completed"] + stats["skipped"]
            completion_rate = 0
            if total_chores > 0:
                completion_rate = round((stats["completed"] / total_chores) * 100, 1)

            logger.debug(
                f"Stats for {flatmate['name']}: completed={stats['completed']}, reassigned={stats['reassigned']}, skipped={stats['skipped']}, rate={completion_rate}%")

            # Add field for this flatmate
            embed.add_field(
                name=flatmate["name"],
                value=f"Completed: {stats['completed']}\n"
                      f"Reassigned: {stats['reassigned']}\n"
                      f"Skipped: {stats['skipped']}\n"
                      f"Completion Rate: {completion_rate}%",
                inline=True
            )

        if len(embed.fields) == 0:
            logger.warning("No statistics available for any flatmates")
            embed.description = "No statistics available yet."

        await interaction.response.send_message(embed=embed)
        logger.info("Stats summary displayed successfully")


async def setup(bot):
    logger.info("Setting up AdminCog")
    admin_cog = AdminCog(bot)
    await bot.add_cog(admin_cog)
    try:
        logger.debug("Adding adminchores command group to the bot")
        bot.tree.add_command(admin_cog.choresadmin)
        logger.info("AdminCog setup completed successfully")
    except Exception as e:
        # Command already registered, skip
        logger.warning(f"Skipping command registration: {e}")