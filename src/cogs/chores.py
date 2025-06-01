import asyncio
import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands

from src.utils.config_manager import ConfigManager
from src.utils.schedule_manager import ScheduleManager
from src.utils.strings import BotStrings

logger = logging.getLogger('chores-bot')


class ChoresCog(commands.Cog):
    def __init__(self, bot):
        logger.info("Initializing ChoresCog")
        self.bot = bot
        self.config_manager = ConfigManager()
        self.schedule_manager = ScheduleManager(self.config_manager)

        # Cache message IDs for reactions (maps message_id -> (chore, flatmate_name))
        self.message_cache = {}

        # Cache for difficulty voting messages (maps message_id -> chore_name)
        self.difficulty_vote_cache = {}

        # Cache for next week planning (will be initialized when command is used)
        # Format: {"message_id": id, "flatmates": [(name, index)]}
        self.next_week_planning_cache = None

        # Track if instructions have been sent
        self.instructions_sent = False
        logger.debug("ChoresCog initialized successfully")

    def cog_check(self, ctx):
        """Check if the command is being used in the chores channel."""
        logger.debug(
            f"Checking if command is in chores channel. User: {ctx.author.name}, Channel: {ctx.channel.name} (ID: {ctx.channel.id})")
        chores_channel_id = self.config_manager.get_chores_channel_id()
        result = ctx.channel.id == chores_channel_id
        logger.debug(f"Command channel check result: {result}")
        return result

    chores = app_commands.Group(name="chores", description="Commands for managing chores")

    @chores.command(name="show")
    @app_commands.describe(detailed="Show detailed view with individual assignment messages (default: False)")
    async def show_schedule(self, interaction: discord.Interaction, detailed: bool = False):
        """Show the current chore schedule. Use detailed=True for a more detailed view with reaction buttons."""
        logger.info(
            f"Show schedule command invoked by {interaction.user.name} (ID: {interaction.user.id}), detailed: {detailed}")

        assignments = self.schedule_manager.get_current_assignments()
        if not assignments:
            logger.warning("No current chore assignments found")
            await interaction.response.send_message(BotStrings.CMD_NO_SCHEDULE)
            return

        # Create an embed to display the schedule
        logger.debug(f"Creating schedule embed with {len(assignments)} assignments")
        embed = self._create_schedule_embed(assignments)
        await interaction.response.send_message(embed=embed)
        logger.info("Schedule displayed successfully")

        # If detailed is True, also post individual assignment messages with reactions
        if detailed:
            logger.debug("Posting detailed schedule with individual messages")
            await interaction.followup.send("Posting detailed assignment messages...")

            # Get the chores channel to post in
            channel = interaction.channel
            logger.debug(f"Using channel for detailed messages: {channel.name} (ID: {channel.id})")

            # Post instructions
            await channel.send(BotStrings.REACTION_INSTRUCTIONS)

            # Send individual messages for each assignment with reaction emojis
            emojis = self.config_manager.get_emoji()
            msg_count = 0

            for chore, flatmate_name in assignments.items():
                flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
                if not flatmate:
                    logger.warning(f"Flatmate not found for assignment: {chore} -> {flatmate_name}")
                    continue

                discord_id = flatmate["discord_id"]
                logger.debug(
                    f"Creating assignment message for '{chore}' assigned to {flatmate_name} (ID: {discord_id})")

                # Create the assignment message
                task_message = BotStrings.TASK_ASSIGNMENT.format(
                    mention=f"<@{discord_id}>",
                    chore=chore
                )

                # Send message with reactions
                message = await channel.send(task_message)
                await message.add_reaction(emojis["completed"])
                await message.add_reaction(emojis["unavailable"])
                msg_count += 1

                # Cache the message ID for reaction handling
                self.message_cache[message.id] = (chore, flatmate_name)

            logger.info(f"Posted detailed schedule with {msg_count} individual messages")
            await interaction.followup.send(f"✅ Posted {msg_count} assignment messages with reaction buttons")

    @chores.command(name="next")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def next_schedule(self, interaction: discord.Interaction):
        """Generate and post the next chore schedule."""
        logger.info(f"Next schedule command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        # Store old assignments to show what changed
        old_assignments = self.schedule_manager.get_current_assignments()
        old_assignments_str = ", ".join(
            [f"{chore}: {name}" for chore, name in old_assignments.items()]) if old_assignments else "None"

        await interaction.response.send_message("Generating new chore schedule...")
        logger.debug(f"Posting new schedule in channel: {interaction.channel.name} (ID: {interaction.channel.id})")

        await self.post_schedule(interaction.channel)
        logger.info("New schedule posted successfully with summary")

    @chores.command(name="reset")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_schedule(self, interaction: discord.Interaction):
        """Reset the chore rotation."""
        logger.info(f"Reset schedule command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        success, message = self.schedule_manager.reset_schedule()
        await interaction.response.send_message(message)

        # Reset the message cache and instructions flag
        logger.debug("Resetting message cache and instructions flag")
        self.message_cache = {}
        self.instructions_sent = False
        logger.info("Schedule reset successfully")

    @chores.command(name="config")
    async def show_config(self, interaction: discord.Interaction):
        """Show the current configuration."""
        logger.info(f"Show config command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        flatmates = self.config_manager.get_flatmates()
        chores_data = self.config_manager.get_chores_data()
        schedule = self.config_manager.get_posting_schedule()
        reminder_settings = self.config_manager.get_reminder_settings()

        logger.debug(f"Found {len(flatmates)} flatmates, {len(chores_data)} chores")
        logger.debug(f"Posting schedule: {schedule}")
        logger.debug(f"Reminder settings: {reminder_settings}")

        embed = discord.Embed(
            title="Chores Bot Configuration",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Add flatmates
        flatmates_str = "\n".join([
            f"• {f['name']} (<@{f['discord_id']}>) {'🏖️ On Vacation' if f.get('on_vacation', False) else ''}"
            for f in flatmates
        ])
        embed.add_field(name="Flatmates", value=flatmates_str or "None", inline=False)

        # Add chores with frequency - Fixed to avoid nested f-string with same quote type
        chores_list = []
        for chore in chores_data:
            freq = chore.get('frequency', 1)
            if freq == 1:
                freq_text = "weekly"
            else:
                freq_text = f"every {freq} weeks"
            chores_list.append(f"• {chore['name']} ({freq}x/{freq_text})")

        chores_str = "\n".join(chores_list)
        embed.add_field(name="Chores", value=chores_str or "None", inline=False)

        # Add schedule
        embed.add_field(
            name="Posting Schedule",
            value=f"Day: {schedule['day']}\nTime: {schedule['time']}\nTimezone: {schedule['timezone']}",
            inline=False
        )

        # Add reminder settings
        reminder_status = "Enabled" if reminder_settings.get("enabled", True) else "Disabled"
        embed.add_field(
            name="Reminder Settings",
            value=f"Status: {reminder_status}\nDay: {reminder_settings.get('day', 'Friday')}\nTime: {reminder_settings.get('time', '11:00')}",
            inline=False
        )

        # Add next week exclusions
        excluded_flatmates = self.schedule_manager.get_excluded_for_next_rotation()
        if excluded_flatmates:
            exclusions_str = "\n".join([f"• {name}" for name in excluded_flatmates])
            embed.add_field(
                name="Excluded from Next Rotation",
                value=exclusions_str,
                inline=False
            )

        await interaction.response.send_message(embed=embed)
        logger.info("Config displayed successfully")

    @chores.command(name="add_flatmate")
    @app_commands.describe(name="Flatmate name", discord_id="Discord user ID")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_flatmate(self, interaction: discord.Interaction, name: str, discord_id: str):
        """Add a new flatmate."""
        logger.info(
            f"Add flatmate command invoked by {interaction.user.name} (ID: {interaction.user.id}), name: {name}, discord_id: {discord_id}")

        try:
            discord_id_int = int(discord_id)
            logger.debug(f"Converting discord_id to integer: {discord_id} -> {discord_id_int}")

            success, message = self.config_manager.add_flatmate(name, discord_id_int)
            await interaction.response.send_message(message)
            logger.info(f"Add flatmate result: {success}, message: {message}")
        except ValueError:
            logger.warning(f"Invalid Discord ID format: {discord_id}")
            await interaction.response.send_message("Invalid Discord ID. Please provide a valid numeric ID.")

    @chores.command(name="remove_flatmate")
    @app_commands.describe(name="Flatmate name to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_flatmate(self, interaction: discord.Interaction, name: str):
        """Remove a flatmate."""
        logger.info(
            f"Remove flatmate command invoked by {interaction.user.name} (ID: {interaction.user.id}), name: {name}")

        success, message = self.config_manager.remove_flatmate(name)
        await interaction.response.send_message(message)
        logger.info(f"Remove flatmate result: {success}, message: {message}")

    @chores.command(name="remove_chore")
    @app_commands.describe(name="Chore name to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_chore(self, interaction: discord.Interaction, name: str):
        """Remove a chore."""
        logger.info(
            f"Remove chore command invoked by {interaction.user.name} (ID: {interaction.user.id}), name: {name}")

        success, message = self.config_manager.remove_chore(name)
        await interaction.response.send_message(message)
        logger.info(f"Remove chore result: {success}, message: {message}")

    @chores.command(name="vacation")
    @app_commands.describe(
        status="Enable or disable vacation mode",
        user="The user to set vacation mode for (optional, defaults to yourself)"
    )
    async def toggle_vacation(self, interaction: discord.Interaction, status: bool = True, user: discord.User = None):
        """Enable or disable vacation mode for yourself or another flatmate."""
        logger.info(
            f"Vacation command invoked by {interaction.user.name} (ID: {interaction.user.id}), status: {status}, user: {user.name if user else 'self'}")

        # If no user specified, use the command invoker
        target_user = user or interaction.user
        logger.debug(f"Target user: {target_user.name} (ID: {target_user.id})")

        # Get the flatmate based on Discord ID
        flatmate = self.config_manager.get_flatmate_by_discord_id(target_user.id)
        if not flatmate:
            logger.warning(f"User {target_user.name} (ID: {target_user.id}) is not registered as a flatmate")
            await interaction.response.send_message(f"{target_user.display_name} is not registered as a flatmate.")
            return

        # Update vacation status
        success, message = self.config_manager.set_flatmate_vacation(flatmate["name"], status)
        logger.debug(f"Vacation status update result: {success}, message: {message}")

        # If turning off vacation mode, set the "recently returned" flag
        if success and not status:
            logger.debug(f"Setting 'recently_returned' flag for {flatmate['name']}")
            flatmate["recently_returned"] = True
            self.config_manager.save_config()

            if target_user.id == interaction.user.id:
                logger.info(f"{flatmate['name']} disabled their own vacation mode")
                await interaction.response.send_message(BotStrings.VACATION_DISABLED.format(name=flatmate["name"]))
            else:
                logger.info(f"{interaction.user.name} disabled vacation mode for {flatmate['name']}")
                await interaction.response.send_message(BotStrings.VACATION_DISABLED_OTHER.format(
                    name=flatmate["name"],
                    setter=interaction.user.display_name
                ))
        elif success:
            if target_user.id == interaction.user.id:
                logger.info(f"{flatmate['name']} enabled their own vacation mode")
                await interaction.response.send_message(BotStrings.VACATION_ENABLED.format(name=flatmate["name"]))
            else:
                logger.info(f"{interaction.user.name} enabled vacation mode for {flatmate['name']}")
                await interaction.response.send_message(BotStrings.VACATION_ENABLED_OTHER.format(
                    name=flatmate["name"],
                    setter=interaction.user.display_name
                ))
        else:
            logger.warning(f"Failed to update vacation status: {message}")
            await interaction.response.send_message(message)

    @chores.command(name="stats")
    @app_commands.describe(name="Flatmate name to view stats for (optional)")
    async def show_stats(self, interaction: discord.Interaction, name: str = None):
        """Show statistics for yourself or another flatmate."""
        logger.info(f"Show stats command invoked by {interaction.user.name} (ID: {interaction.user.id}), name: {name}")

        # If no name is provided, use the requestor's name
        if not name:
            logger.debug(f"No name provided, using requestor: {interaction.user.name} (ID: {interaction.user.id})")
            flatmate = self.config_manager.get_flatmate_by_discord_id(interaction.user.id)
            if not flatmate:
                logger.warning(
                    f"User {interaction.user.name} (ID: {interaction.user.id}) is not registered as a flatmate")
                await interaction.response.send_message("You are not registered as a flatmate.")
                return
            name = flatmate["name"]
            logger.debug(f"Using flatmate name: {name}")

        # Get the stats for the specified flatmate
        stats = self.config_manager.get_flatmate_stats(name)
        if not stats:
            logger.warning(f"No statistics found for flatmate: {name}")
            await interaction.response.send_message(f"No statistics found for {name}.")
            return

        # Calculate completion rate
        total_chores = stats["completed"] + stats["skipped"]
        completion_rate = 0
        if total_chores > 0:
            completion_rate = round((stats["completed"] / total_chores) * 100, 1)

        logger.debug(
            f"Stats for {name}: completed={stats['completed']}, reassigned={stats['reassigned']}, skipped={stats['skipped']}, rate={completion_rate}%")

        # Create an embed to display the stats
        embed = discord.Embed(
            title=BotStrings.STATS_HEADER.format(name=name),
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="Chores",
            value=BotStrings.STATS_COMPLETED.format(count=stats["completed"]) + "\n" +
                  BotStrings.STATS_REASSIGNED.format(count=stats["reassigned"]) + "\n" +
                  BotStrings.STATS_SKIPPED.format(count=stats["skipped"]),
            inline=False
        )

        embed.add_field(
            name="Performance",
            value=BotStrings.STATS_COMPLETION_RATE.format(rate=completion_rate),
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        logger.info(f"Stats displayed successfully for {name}")

    @chores.command(name="set_difficulty")
    @app_commands.describe(chore="Chore name", difficulty="Difficulty level (1-5)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_difficulty(self, interaction: discord.Interaction, chore: str, difficulty: int):
        """Set the difficulty level for a chore."""
        logger.info(
            f"Set difficulty command invoked by {interaction.user.name} (ID: {interaction.user.id}), chore: {chore}, difficulty: {difficulty}")

        # Validate difficulty level
        if difficulty < 1 or difficulty > 5:
            logger.warning(f"Invalid difficulty level: {difficulty}")
            await interaction.response.send_message("Difficulty must be between 1 and 5.")
            return

        success, message = self.config_manager.set_chore_difficulty(chore, difficulty)
        if success:
            logger.info(f"Difficulty for chore '{chore}' set to {difficulty}")
            await interaction.response.send_message(BotStrings.DIFFICULTY_SET.format(chore=chore, level=difficulty))
        else:
            logger.warning(f"Failed to set difficulty: {message}")
            await interaction.response.send_message(message)

    @chores.command(name="vote_difficulty")
    @app_commands.describe(chore="Chore to vote on difficulty")
    async def vote_difficulty(self, interaction: discord.Interaction, chore: str):
        """Start a vote on the difficulty level of a chore."""
        logger.info(
            f"Vote difficulty command invoked by {interaction.user.name} (ID: {interaction.user.id}), chore: {chore}")

        # Check if the chore exists
        if chore not in self.config_manager.get_chores():
            logger.warning(f"Chore not found: {chore}")
            await interaction.response.send_message("Chore not found.")
            return

        # Create an embed for the vote
        embed = discord.Embed(
            title=BotStrings.DIFFICULTY_VOTE_HEADER,
            description=BotStrings.DIFFICULTY_VOTE_INSTRUCTIONS.format(chore=chore) + "\n\n" +
                        BotStrings.DIFFICULTY_VOTE_SCALE,
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )

        await interaction.response.send_message(embed=embed)
        logger.debug(f"Vote difficulty instructions sent for chore: {chore}")

        # Send a message that users can react to
        message = await interaction.channel.send(f"Vote on the difficulty of **{chore}**:")
        logger.debug(f"Vote message sent, ID: {message.id}")

        # Add reaction emojis
        emojis = self.config_manager.get_emoji()
        for i in range(1, 6):
            emoji_key = f"difficulty_{i}"
            await message.add_reaction(emojis[emoji_key])
            logger.debug(f"Added reaction {emojis[emoji_key]} for difficulty {i}")

        # Store the message ID for later processing
        self.difficulty_vote_cache[message.id] = chore
        logger.debug(f"Added message ID {message.id} to difficulty vote cache for chore: {chore}")

        # Wait for 5 minutes then tally the votes
        logger.info(f"Starting 5-minute timer for difficulty vote on chore: {chore}")
        await asyncio.sleep(300)  # 5 minutes
        logger.info(f"Vote time expired for chore: {chore}")

        try:
            # Fetch the updated message with reactions
            logger.debug(f"Fetching updated message: {message.id}")
            updated_message = await interaction.channel.fetch_message(message.id)

            # Count votes
            vote_counts = {i: 0 for i in range(1, 6)}
            logger.debug("Counting votes")

            for reaction in updated_message.reactions:
                # Skip reactions that aren't difficulty ratings
                if str(reaction.emoji) not in [emojis[f"difficulty_{i}"] for i in range(1, 6)]:
                    logger.debug(f"Skipping non-difficulty reaction: {reaction.emoji}")
                    continue

                # Figure out which difficulty this reaction represents
                for i in range(1, 6):
                    if str(reaction.emoji) == emojis[f"difficulty_{i}"]:
                        # Count non-bot votes
                        users = [user async for user in reaction.users() if not user.bot]
                        vote_counts[i] = len(users)
                        logger.debug(f"Difficulty {i} received {vote_counts[i]} votes")
                        break

            # Calculate the average difficulty (weighted average)
            total_votes = sum(vote_counts.values())
            logger.debug(f"Total votes: {total_votes}")

            if total_votes > 0:
                weighted_sum = sum(level * count for level, count in vote_counts.items())
                average_difficulty = round(weighted_sum / total_votes)
                logger.debug(f"Weighted sum: {weighted_sum}, Average difficulty: {average_difficulty}")

                # Ensure it's between 1-5
                average_difficulty = max(1, min(5, average_difficulty))
                logger.debug(f"Clamped average difficulty: {average_difficulty}")

                # Update the chore difficulty
                self.config_manager.set_chore_difficulty(chore, average_difficulty)
                logger.info(
                    f"Updated difficulty for chore '{chore}' to {average_difficulty} based on {total_votes} votes")

                # Announce the result
                await interaction.channel.send(
                    BotStrings.DIFFICULTY_VOTE_RESULT.format(chore=chore, level=average_difficulty)
                )
            else:
                logger.warning(f"No votes were cast for chore: {chore}")
                await interaction.channel.send(f"No votes were cast for **{chore}**.")

            # Remove from cache
            self.difficulty_vote_cache.pop(message.id, None)
            logger.debug(f"Removed message ID {message.id} from difficulty vote cache")

        except discord.errors.NotFound:
            logger.error(f"Message {message.id} not found, possibly deleted")
            await interaction.channel.send(f"The vote message for **{chore}** was deleted.")
        except Exception as e:
            logger.error(f"Error processing difficulty vote: {e}", exc_info=True)
            await interaction.channel.send(f"There was an error processing the vote for **{chore}**.")

    @chores.command(name="next_week")
    async def next_week_planning(self, interaction: discord.Interaction):
        """Show and plan who will be included in next week's chore rotation."""
        logger.info(f"Next week planning command invoked by {interaction.user.name} (ID: {interaction.user.id})")

        # Get all flatmates who are not on vacation
        active_flatmates = self.config_manager.get_active_flatmates()
        if not active_flatmates:
            logger.warning("No active flatmates found for planning")
            await interaction.response.send_message(BotStrings.ERR_NEXT_WEEK_NO_ACTIVE)
            return

        # Get excluded flatmates for next rotation
        excluded_flatmates = self.schedule_manager.get_excluded_for_next_rotation()
        logger.debug(f"Currently excluded flatmates: {excluded_flatmates}")

        # Create embed for display
        embed = discord.Embed(
            title="🗓️ Next Week's Chore Rotation Planning",
            description="Below are the flatmates who will be included in next week's chore rotation.\n"
                        "React with the number beside a flatmate to toggle their inclusion/exclusion.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Number emojis for selection
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # Add fields for each flatmate
        for i, flatmate in enumerate(active_flatmates):
            if i >= len(number_emojis):
                logger.warning(f"More flatmates than available emojis, skipping flatmate: {flatmate['name']}")
                break

            # Check if flatmate is already excluded for next rotation
            is_excluded = flatmate["name"] in excluded_flatmates

            # For each flatmate, show their status
            status = "❌ Excluded from next rotation" if is_excluded else "✅ Included in next rotation"
            logger.debug(f"Flatmate {flatmate['name']} status: {status}")

            embed.add_field(
                name=f"{number_emojis[i]} {flatmate['name']}",
                value=f"<@{flatmate['discord_id']}>\n{status}",
                inline=True
            )

        # Add instructions
        embed.add_field(
            name="Instructions",
            value="React with the number next to a flatmate to toggle their inclusion/exclusion.\n"
                  "Changes will apply to the next schedule generation.",
            inline=False
        )

        # Send the message
        await interaction.response.send_message(embed=embed)
        logger.debug("Next week planning embed sent")

        # Get the sent message for adding reactions
        message = await interaction.original_response()
        logger.debug(f"Planning message ID: {message.id}")

        # Add reactions for each flatmate
        for i, flatmate in enumerate(active_flatmates):
            if i < len(number_emojis):
                await message.add_reaction(number_emojis[i])
                logger.debug(f"Added reaction {number_emojis[i]} for flatmate {flatmate['name']}")

        # Store message ID and flatmates in cache for reaction handling
        self.next_week_planning_cache = {
            "message_id": message.id,
            "flatmates": [(f["name"], i) for i, f in enumerate(active_flatmates) if i < len(number_emojis)]
        }
        logger.debug(
            f"Stored planning cache for message ID {message.id} with {len(self.next_week_planning_cache['flatmates'])} flatmates")
        logger.info("Next week planning setup completed")

    @chores.command(name="set_frequency")
    @app_commands.describe(chore="Chore name", frequency="Frequency (1=weekly, 2=bi-weekly, etc.)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_frequency(self, interaction: discord.Interaction, chore: str, frequency: int):
        """Set how often a chore appears in the rotation."""
        logger.info(
            f"Set frequency command invoked by {interaction.user.name} (ID: {interaction.user.id}), chore: {chore}, frequency: {frequency}")

        # Validate frequency
        if frequency < 1:
            logger.warning(f"Invalid frequency: {frequency}")
            await interaction.response.send_message("Frequency must be at least 1.")
            return

        success, message = self.config_manager.set_chore_frequency(chore, frequency)
        if success:
            freq_text = "weekly" if frequency == 1 else f"every {frequency} weeks"
            logger.info(f"Frequency for chore '{chore}' set to {frequency} ({freq_text})")
            await interaction.response.send_message(f"Frequency for '{chore}' set to {frequency} ({freq_text}).")
        else:
            logger.warning(f"Failed to set frequency: {message}")
            await interaction.response.send_message(message)

    @chores.command(name="add_chore")
    @app_commands.describe(name="Chore name to add",
                          frequency="How often this chore appears (1=weekly, 2=bi-weekly, etc.)")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_chore(self, interaction: discord.Interaction, name: str, frequency: int = 1):
        """Add a new chore with frequency."""
        logger.info(
            f"Add chore command invoked by {interaction.user.name} (ID: {interaction.user.id}), name: {name}, frequency: {frequency}")

        # Validate frequency
        if frequency < 1:
            logger.warning(f"Invalid frequency: {frequency}")
            await interaction.response.send_message("Frequency must be at least 1.")
            return

        success, message = self.config_manager.add_chore(name, frequency)
        if success:
            freq_text = "weekly" if frequency == 1 else f"every {frequency} weeks"
            logger.info(f"Added chore '{name}' with frequency {frequency} ({freq_text})")
            await interaction.response.send_message(f"Chore '{name}' added successfully. It will appear {freq_text}.")
        else:
            logger.warning(f"Failed to add chore: {message}")
            await interaction.response.send_message(message)

    async def post_schedule(self, channel=None):
        """Post the weekly chore schedule with individual messages for each flatmate."""
        logger.info("Posting new chore schedule")

        # Generate new schedule
        logger.debug("Generating new schedule")
        assignments = self.schedule_manager.generate_new_schedule()
        if not assignments:
            logger.warning("Failed to generate schedule: No assignments created")
            return

        # Update last posted date
        logger.debug("Updating last posted date")
        self.schedule_manager.update_last_posted_date()

        # Get the chores channel if not provided
        if channel is None:
            logger.debug("No channel provided, getting chores channel from config")
            channel_id = self.config_manager.get_chores_channel_id()
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Chores channel not found: {channel_id}")
                return
            logger.debug(f"Using channel: {channel.name} (ID: {channel.id})")

        # First, post a header message for the weekly schedule
        logger.debug("Posting schedule header")
        await channel.send(BotStrings.SCHEDULE_HEADER)

        # Then post instructions (only once)
        if not self.instructions_sent:
            logger.debug("Posting instructions (first time)")
            instructions_message = await channel.send(BotStrings.REACTION_INSTRUCTIONS)
            self.instructions_sent = True
        else:
            logger.debug("Instructions already sent")

        # Clear previous message cache
        old_cache_size = len(self.message_cache)
        self.message_cache = {}
        logger.debug(f"Cleared previous message cache ({old_cache_size} entries)")

        # Send individual messages for each assignment
        emojis = self.config_manager.get_emoji()
        logger.debug(f"Sending {len(assignments)} individual assignment messages")

        for chore, flatmate_name in assignments.items():
            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
            if not flatmate:
                logger.warning(f"Flatmate not found for assignment: {chore} -> {flatmate_name}")
                continue

            discord_id = flatmate["discord_id"]
            logger.debug(
                f"Creating assignment message for chore '{chore}' assigned to {flatmate_name} (ID: {discord_id})")

            # Create the assignment message
            task_message = BotStrings.TASK_ASSIGNMENT.format(
                mention=f"<@{discord_id}>",
                chore=chore
            )

            # Send the message
            message = await channel.send(task_message)
            logger.debug(f"Assignment message sent, ID: {message.id}")

            # Add reaction emojis for interaction
            await message.add_reaction(emojis["completed"])
            await message.add_reaction(emojis["unavailable"])
            logger.debug(f"Added reactions to message {message.id}: {emojis['completed']} and {emojis['unavailable']}")

            # Cache the message ID for reaction handling
            self.message_cache[message.id] = (chore, flatmate_name)
            logger.debug(f"Cached message ID {message.id} for chore '{chore}' assigned to {flatmate_name}")

        logger.info(f"Posted new schedule in channel {channel.name} ({channel.id}) with {len(assignments)} assignments")

    async def send_reminders(self, channel=None):
        """Send reminders for pending chores."""
        logger.info("Sending reminders for pending chores")

        # Get reminder settings
        reminder_settings = self.config_manager.get_reminder_settings()
        if not reminder_settings.get("enabled", True):
            logger.info("Reminders are disabled, skipping")
            return

        # Get pending chores
        pending_chores = self.schedule_manager.get_pending_chores()
        if not pending_chores:
            logger.info("No pending chores to remind about")
            return

        logger.debug(f"Found {len(pending_chores)} pending chores: {pending_chores}")

        # Get the chores channel if not provided
        if channel is None:
            logger.debug("No channel provided, getting chores channel from config")
            channel_id = self.config_manager.get_chores_channel_id()
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Chores channel not found: {channel_id}")
                return
            logger.debug(f"Using channel: {channel.name} (ID: {channel.id})")

        # Send a reminder header
        logger.debug("Sending reminder header")
        await channel.send(BotStrings.REMINDER_HEADER)

        # Send individual reminders for each pending chore
        assignments = self.schedule_manager.get_current_assignments()
        reminder_count = 0

        for chore in pending_chores:
            flatmate_name = assignments.get(chore)
            if not flatmate_name:
                logger.warning(f"No assignment found for pending chore: {chore}")
                continue

            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
            if not flatmate:
                logger.warning(f"Flatmate not found for assignment: {chore} -> {flatmate_name}")
                continue

            discord_id = flatmate["discord_id"]
            logger.debug(f"Creating reminder for chore '{chore}' assigned to {flatmate_name} (ID: {discord_id})")

            # Create the reminder message
            reminder_message = BotStrings.REMINDER_MESSAGE.format(
                mention=f"<@{discord_id}>",
                chore=chore
            )

            # Send the message
            await channel.send(reminder_message)
            reminder_count += 1
            logger.debug(f"Sent reminder for chore '{chore}' to {flatmate_name}")

        logger.info(f"Sent {reminder_count} reminders for pending chores")

    def _create_schedule_embed(self, assignments):
        """Create an embed for the chore schedule."""
        logger.debug(f"Creating schedule embed for {len(assignments)} assignments")

        embed = discord.Embed(
            title=BotStrings.EMBED_SCHEDULE_TITLE,
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )

        # Add each chore and assigned flatmate to the embed
        for chore, flatmate_name in assignments.items():
            # Get the flatmate's Discord ID to mention them
            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)

            # Get chore frequency
            frequency = self.config_manager.get_chore_frequency(chore)
            freq_text = "" if frequency == 1 else f" (every {frequency} weeks)"

            if flatmate:
                discord_id = flatmate["discord_id"]
                value = BotStrings.EMBED_TASK_ASSIGNED.format(mention=f"<@{discord_id}>")
                logger.debug(f"Assigned to flatmate: {flatmate_name} (ID: {discord_id})")
            else:
                value = BotStrings.EMBED_TASK_ASSIGNED.format(mention=flatmate_name)
                logger.warning(f"Flatmate not found for assignment: {chore} -> {flatmate_name}")

            embed.add_field(name=f"**{chore}{freq_text}**", value=value, inline=False)

        # Add instructions for reactions
        emojis = self.config_manager.get_emoji()
        embed.add_field(
            name=BotStrings.EMBED_HOW_TO_RESPOND,
            value=BotStrings.EMBED_REACTIONS_GUIDE,
            inline=False
        )

        # Add footer with last updated time
        embed.set_footer(text=BotStrings.EMBED_SCHEDULE_FOOTER)
        logger.debug("Schedule embed created successfully")

        return embed

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions to chore assignment messages."""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            logger.debug(f"Ignoring bot reaction from user ID: {payload.user_id}")
            return

        # Check if this is a reaction to one of our tracked messages
        if payload.message_id in self.message_cache:
            logger.info(f"Detected reaction to tracked chore message: {payload.message_id}")
            await self._handle_chore_reaction(payload)
        elif payload.message_id in self.difficulty_vote_cache:
            # We don't need to do anything here, as voting is handled in the vote_difficulty command
            logger.debug(f"Detected reaction to difficulty vote message: {payload.message_id}")
            pass
        elif hasattr(self,
                     'next_week_planning_cache') and self.next_week_planning_cache and payload.message_id == self.next_week_planning_cache.get(
                "message_id"):
            # Handle reactions to next week planning
            logger.info(f"Detected reaction to next week planning message: {payload.message_id}")
            await self._handle_next_week_planning_reaction(payload)
        else:
            logger.debug(f"Ignoring reaction to untracked message: {payload.message_id}")

    async def _handle_chore_reaction(self, payload):
        """Handle reactions to chore assignment messages."""
        logger.info(f"Handling chore reaction from user ID: {payload.user_id}, emoji: {payload.emoji}")

        # Get the channel
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            logger.error(f"Channel not found: {payload.channel_id}")
            return

        # Get the message
        try:
            logger.debug(f"Fetching message: {payload.message_id}")
            message = await channel.fetch_message(payload.message_id)
            if not message:
                logger.warning(f"Message not found: {payload.message_id}")
                return
        except discord.errors.NotFound:
            logger.error(f"Message {payload.message_id} not found, possibly deleted")
            return
        except Exception as e:
            logger.error(f"Failed to fetch message: {e}", exc_info=True)
            return

        # Get the user who reacted
        user = self.bot.get_user(payload.user_id)
        if not user:
            logger.warning(f"User not found: {payload.user_id}")
            return

        # Get the chore and assigned flatmate from our cache
        chore, assigned_flatmate_name = self.message_cache[payload.message_id]
        logger.debug(f"Cached assignment: chore '{chore}' assigned to {assigned_flatmate_name}")

        # Get the flatmate from the user's Discord ID
        flatmate = self.config_manager.get_flatmate_by_discord_id(payload.user_id)
        if not flatmate:
            # Remove reaction if the user is not a flatmate
            logger.warning(f"User {user.name} (ID: {payload.user_id}) is not a flatmate, removing reaction")
            await message.remove_reaction(payload.emoji, user)
            return

        # Get the emoji configuration
        emojis = self.config_manager.get_emoji()
        emoji_name = str(payload.emoji)
        logger.debug(f"Reaction emoji: {emoji_name}")

        # Check if this is the assigned flatmate or someone else helping out
        is_assigned_flatmate = flatmate["name"] == assigned_flatmate_name

        # Handle the reaction based on the emoji
        if emoji_name == emojis["completed"]:
            # Check if the chore is still in pending chores
            pending_chores = self.schedule_manager.get_pending_chores()
            is_pending = chore in pending_chores

            # Get who has already completed this chore
            completed_by = self.schedule_manager.schedule_data.get("completed_by", {}).get(chore, [])
            has_already_completed = flatmate["name"] in completed_by

            # If the chore is not pending, and this person already completed it, ignore
            if not is_pending and has_already_completed:
                logger.debug(f"Flatmate {flatmate['name']} has already completed this chore, ignoring")
                await message.remove_reaction(payload.emoji, user)
                await channel.send(
                    f"{user.mention} You've already completed this chore.",
                    delete_after=10
                )
                return

            if is_assigned_flatmate:
                # Mark chore as completed by assigned flatmate
                logger.info(f"Marking chore '{chore}' as completed by {flatmate['name']}")
                success, message_text = self.schedule_manager.mark_chore_completed(chore, flatmate["name"])

                if success:
                    # Send completion message
                    completion_msg = BotStrings.TASK_COMPLETED.format(
                        mention=user.mention,
                        chore=chore
                    )
                    await channel.send(completion_msg)
                    logger.info(f"Chore '{chore}' marked as completed by {flatmate['name']}")

                    # Play celebration music
                    music_cog = self.bot.get_cog("MusicCog")
                    if music_cog:
                        logger.info("Triggering music celebration")
                        await music_cog.play_celebration(channel.guild)
                    else:
                        logger.warning("MusicCog not found, cannot play celebration music")
            else:
                # Another flatmate is completing the chore
                logger.info(f"Flatmate {flatmate['name']} is completing chore '{chore}'")

                # Mark chore as completed with helper
                success, message_text = self.schedule_manager.mark_chore_completed(
                    chore, assigned_flatmate_name, helper=flatmate["name"]
                )

                if success:
                    # Get the assigned flatmate's discord mention
                    assigned_flatmate = self.config_manager.get_flatmate_by_name(assigned_flatmate_name)
                    assigned_mention = f"<@{assigned_flatmate['discord_id']}>" if assigned_flatmate else assigned_flatmate_name

                    # Check if this is an additional completion
                    if "additional" in message_text:
                        # Additional completion message
                        helper_msg = f"✅ {user.mention} has also completed the chore **{chore}**! Thank you so much for participating in keeping our flat clean! 🙌"
                    else:
                        # First completion by helper
                        helper_msg = f"✅ {user.mention} has completed the chore **{chore}** that was assigned to {assigned_mention}! Thank you so much for participating in keeping our flat clean! 🦸"

                    await channel.send(helper_msg)
                    logger.info(f"Chore '{chore}' completed by {flatmate['name']} for {assigned_flatmate_name}")

                    # Play celebration music
                    music_cog = self.bot.get_cog("MusicCog")
                    if music_cog:
                        logger.info("Triggering music celebration")
                        await music_cog.play_celebration(channel.guild)
                    else:
                        logger.warning("MusicCog not found, cannot play celebration music")
        elif emoji_name == emojis["unavailable"]:
            # Only the assigned flatmate can mark as unavailable
            if not is_assigned_flatmate:
                logger.warning(f"User {user.name} tried to mark someone else's chore as unavailable")
                await message.remove_reaction(payload.emoji, user)
                await channel.send(
                    f"{user.mention} You can only mark your own assigned chores as unavailable.",
                    delete_after=10
                )
                return

            # Mark the original flatmate as having voted
            logger.info(f"Marking flatmate {flatmate['name']} as unavailable for chore '{chore}'")
            self.schedule_manager.add_voted_flatmate(flatmate["name"])

            # Randomly reassign the chore
            logger.debug(f"Randomly reassigning chore '{chore}' from {flatmate['name']}")
            next_flatmate_name = self.schedule_manager.randomly_reassign_chore(
                chore,
                flatmate["name"]
            )

            if next_flatmate_name:
                # Get the next flatmate's Discord ID
                next_flatmate = self.config_manager.get_flatmate_by_name(next_flatmate_name)

                if next_flatmate:
                    next_discord_id = next_flatmate["discord_id"]
                    logger.debug(f"Chore reassigned to {next_flatmate_name} (ID: {next_discord_id})")

                    # Send reassignment notification
                    reassign_msg = BotStrings.TASK_REASSIGNED_FULL.format(
                        original_mention=user.mention,
                        chore=chore,
                        new_mention=f"<@{next_discord_id}>"
                    )
                    await channel.send(reassign_msg)

                    # Create a new message for the reassigned chore
                    new_task_msg = BotStrings.TASK_ASSIGNMENT.format(
                        mention=f"<@{next_discord_id}>",
                        chore=chore
                    )
                    new_message = await channel.send(new_task_msg)
                    logger.debug(f"Created new assignment message, ID: {new_message.id}")

                    # Add reactions to the new message
                    await new_message.add_reaction(emojis["completed"])
                    await new_message.add_reaction(emojis["unavailable"])
                    logger.debug(f"Added reactions to new message {new_message.id}")

                    # Update our message cache
                    self.message_cache[new_message.id] = (chore, next_flatmate_name)
                    logger.debug(f"Cached new message ID {new_message.id} for reassigned chore")

                    # Remove the old message from the cache
                    self.message_cache.pop(payload.message_id, None)
                    logger.debug(f"Removed old message ID {payload.message_id} from cache")

                    logger.info(
                        f"Chore '{chore}' successfully reassigned from {flatmate['name']} to {next_flatmate_name}")
            else:
                logger.warning(f"Failed to reassign chore '{chore}'")
                await channel.send(BotStrings.ERR_REASSIGN_FAILED.format(chore=chore))
        else:
            # Remove unrelated reactions
            logger.debug(f"Removing unrelated reaction {emoji_name} from message {payload.message_id}")
            await message.remove_reaction(payload.emoji, user)

    async def _handle_next_week_planning_reaction(self, payload):
        """Handle reactions to next week planning messages."""
        logger.info(f"Handling next week planning reaction from user ID: {payload.user_id}, emoji: {payload.emoji}")

        # Skip if not a tracked message
        if not hasattr(self,
                       'next_week_planning_cache') or not self.next_week_planning_cache or self.next_week_planning_cache.get(
                "message_id") != payload.message_id:
            logger.debug("Not a tracked planning message, skipping")
            return

        # Get the channel
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            logger.error(f"Channel not found: {payload.channel_id}")
            return

        # Get the message
        try:
            logger.debug(f"Fetching message: {payload.message_id}")
            message = await channel.fetch_message(payload.message_id)
            if not message:
                logger.warning(f"Message not found: {payload.message_id}")
                return
        except discord.errors.NotFound:
            logger.error(f"Message {payload.message_id} not found, possibly deleted")
            return
        except Exception as e:
            logger.error(f"Failed to fetch message: {e}", exc_info=True)
            return

        # Get the user who reacted
        user = self.bot.get_user(payload.user_id)
        if not user or user.bot:  # Skip if bot reaction
            logger.debug(f"Skipping reaction from bot or non-existent user: {payload.user_id}")
            return

        # Get emoji
        emoji_name = str(payload.emoji)
        logger.debug(f"Reaction emoji: {emoji_name}")

        # Number emojis for flatmate selection
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # Check if the emoji is a number emoji
        if emoji_name in number_emojis:
            # Find the corresponding flatmate
            selected_index = number_emojis.index(emoji_name)
            selected_flatmate = None
            logger.debug(f"Selected index: {selected_index}")

            for name, idx in self.next_week_planning_cache["flatmates"]:
                if idx == selected_index:
                    selected_flatmate = name
                    break

            if not selected_flatmate:
                logger.warning(f"No flatmate found for index {selected_index}")
                await message.remove_reaction(payload.emoji, user)
                return

            logger.debug(f"Selected flatmate: {selected_flatmate}")

            # Toggle the flatmate's exclusion status
            excluded_flatmates = self.schedule_manager.get_excluded_for_next_rotation()
            logger.debug(f"Current excluded flatmates: {excluded_flatmates}")

            if selected_flatmate in excluded_flatmates:
                # Include the flatmate
                logger.info(f"Including flatmate {selected_flatmate} in next rotation")
                self.schedule_manager.include_in_next_rotation(selected_flatmate)
                await channel.send(
                    f"{user.mention} has included {selected_flatmate} in the next chore rotation.",
                    delete_after=5
                )
            else:
                # Exclude the flatmate
                logger.info(f"Excluding flatmate {selected_flatmate} from next rotation")
                self.schedule_manager.exclude_from_next_rotation(selected_flatmate)
                await channel.send(
                    f"{user.mention} has excluded {selected_flatmate} from the next chore rotation.",
                    delete_after=5
                )

            # Update the embed to reflect changes
            logger.debug("Updating planning embed to reflect changes")
            await self._update_next_week_planning_embed(message)

        # Remove the reaction
        logger.debug(f"Removing reaction {emoji_name} from user {user.name}")
        await message.remove_reaction(payload.emoji, user)

    async def _update_next_week_planning_embed(self, message):
        """Update the next week planning embed to reflect current exclusions."""
        logger.debug(f"Updating next week planning embed for message ID: {message.id}")

        # Get all flatmates who are not on vacation
        active_flatmates = self.config_manager.get_active_flatmates()
        logger.debug(f"Found {len(active_flatmates)} active flatmates")

        # Get excluded flatmates for next rotation
        excluded_flatmates = self.schedule_manager.get_excluded_for_next_rotation()
        logger.debug(f"Current excluded flatmates: {excluded_flatmates}")

        # Create updated embed
        embed = discord.Embed(
            title="🗓️ Next Week's Chore Rotation Planning",
            description="Below are the flatmates who will be included in next week's chore rotation.\n"
                        "React with the corresponding number to toggle inclusion/exclusion.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Number emojis for selection
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # Add fields for each flatmate with updated status
        for i, flatmate in enumerate(active_flatmates):
            if i >= len(number_emojis):
                logger.warning(f"More flatmates than available emojis, skipping flatmate: {flatmate['name']}")
                break

            # Check if flatmate is excluded for next rotation
            is_excluded = flatmate["name"] in excluded_flatmates

            # Determine status
            status = "❌ Excluded from next rotation" if is_excluded else "✅ Included in next rotation"
            logger.debug(f"Flatmate {flatmate['name']} status: {status}")

            embed.add_field(
                name=f"{number_emojis[i]} {flatmate['name']}",
                value=f"<@{flatmate['discord_id']}>\n{status}",
                inline=True
            )

        # Add instructions
        embed.add_field(
            name="Instructions",
            value="React with the number next to a flatmate to toggle their inclusion/exclusion.\n"
                  "Changes will apply to the next schedule generation.",
            inline=False
        )

        # Edit the message with the updated embed
        await message.edit(embed=embed)
        logger.debug(f"Updated next week planning embed for message ID: {message.id}")


async def setup(bot):
    logger.info("Setting up ChoresCog")
    chores_cog = ChoresCog(bot)
    await bot.add_cog(chores_cog)
    try:
        logger.debug("Adding chores command group to the bot")
        bot.tree.add_command(chores_cog.chores)
        logger.info("ChoresCog setup completed successfully")
    except Exception as e:
        logger.warning(f"Skipping command registration: {e}")  # Command already registered, skip