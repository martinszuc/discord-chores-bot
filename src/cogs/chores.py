import discord
from discord import app_commands
from discord.ext import commands
import logging
import datetime
import asyncio
from src.utils.config_manager import ConfigManager
from src.utils.schedule_manager import ScheduleManager
from src.utils.strings import BotStrings

logger = logging.getLogger('chores-bot')


class ChoresCog(commands.Cog):
    def __init__(self, bot):
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

    def cog_check(self, ctx):
        """Check if the command is being used in the chores channel."""
        chores_channel_id = self.config_manager.get_chores_channel_id()
        return ctx.channel.id == chores_channel_id

    chores = app_commands.Group(name="chores", description="Commands for managing chores")

    @chores.command(name="show")
    async def show_schedule(self, interaction: discord.Interaction):
        """Show the current chore schedule."""
        assignments = self.schedule_manager.get_current_assignments()
        if not assignments:
            await interaction.response.send_message(BotStrings.CMD_NO_SCHEDULE)
            return

        # Create an embed to display the schedule
        embed = self._create_schedule_embed(assignments)
        await interaction.response.send_message(embed=embed)

    @chores.command(name="next")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def next_schedule(self, interaction: discord.Interaction):
        """Generate and post the next chore schedule."""
        await interaction.response.send_message("Generating new chore schedule...")
        await self.post_schedule(interaction.channel)
        await interaction.followup.send(BotStrings.CMD_NEW_SCHEDULE)

    @chores.command(name="reset")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_schedule(self, interaction: discord.Interaction):
        """Reset the chore rotation."""
        success, message = self.schedule_manager.reset_schedule()
        await interaction.response.send_message(message)
        # Reset the message cache and instructions flag
        self.message_cache = {}
        self.instructions_sent = False

    @chores.command(name="config")
    async def show_config(self, interaction: discord.Interaction):
        """Show the current configuration."""
        flatmates = self.config_manager.get_flatmates()
        chores = self.config_manager.get_chores()
        schedule = self.config_manager.get_posting_schedule()
        reminder_settings = self.config_manager.get_reminder_settings()

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

        # Add chores with difficulty
        chores_str = ""
        for chore in chores:
            difficulty = self.config_manager.get_chore_details(chore).get("difficulty", 1)
            difficulty_stars = "⭐" * difficulty
            chores_str += f"• {chore} ({difficulty_stars})\n"

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
            value=f"Status: {reminder_status}\nDay: {reminder_settings.get('day', 'Friday')}\nTime: {reminder_settings.get('time', '18:00')}",
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

    @chores.command(name="add_flatmate")
    @app_commands.describe(name="Flatmate name", discord_id="Discord user ID")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_flatmate(self, interaction: discord.Interaction, name: str, discord_id: str):
        """Add a new flatmate."""
        try:
            discord_id_int = int(discord_id)
            success, message = self.config_manager.add_flatmate(name, discord_id_int)
            await interaction.response.send_message(message)
        except ValueError:
            await interaction.response.send_message("Invalid Discord ID. Please provide a valid numeric ID.")

    @chores.command(name="remove_flatmate")
    @app_commands.describe(name="Flatmate name to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_flatmate(self, interaction: discord.Interaction, name: str):
        """Remove a flatmate."""
        success, message = self.config_manager.remove_flatmate(name)
        await interaction.response.send_message(message)

    @chores.command(name="add_chore")
    @app_commands.describe(name="Chore name to add", difficulty="Difficulty level (1-5)")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_chore(self, interaction: discord.Interaction, name: str, difficulty: int = 1):
        """Add a new chore with optional difficulty rating."""
        # Validate difficulty level
        if difficulty < 1 or difficulty > 5:
            await interaction.response.send_message("Difficulty must be between 1 and 5.")
            return

        success, message = self.config_manager.add_chore(name, difficulty)
        await interaction.response.send_message(message)

    @chores.command(name="remove_chore")
    @app_commands.describe(name="Chore name to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_chore(self, interaction: discord.Interaction, name: str):
        """Remove a chore."""
        success, message = self.config_manager.remove_chore(name)
        await interaction.response.send_message(message)

    @chores.command(name="vacation")
    @app_commands.describe(
        status="Enable or disable vacation mode",
        user="The user to set vacation mode for (optional, defaults to yourself)"
    )
    async def toggle_vacation(self, interaction: discord.Interaction, status: bool = True, user: discord.User = None):
        """Enable or disable vacation mode for yourself or another flatmate."""
        # If no user specified, use the command invoker
        target_user = user or interaction.user

        # Get the flatmate based on Discord ID
        flatmate = self.config_manager.get_flatmate_by_discord_id(target_user.id)
        if not flatmate:
            await interaction.response.send_message(f"{target_user.display_name} is not registered as a flatmate.")
            return

        # Update vacation status
        success, message = self.config_manager.set_flatmate_vacation(flatmate["name"], status)

        # If turning off vacation mode, set the "recently returned" flag
        if success and not status:
            flatmate["recently_returned"] = True
            self.config_manager.save_config()

            if target_user.id == interaction.user.id:
                await interaction.response.send_message(BotStrings.VACATION_DISABLED.format(name=flatmate["name"]))
            else:
                await interaction.response.send_message(BotStrings.VACATION_DISABLED_OTHER.format(
                    name=flatmate["name"],
                    setter=interaction.user.display_name
                ))
        elif success:
            if target_user.id == interaction.user.id:
                await interaction.response.send_message(BotStrings.VACATION_ENABLED.format(name=flatmate["name"]))
            else:
                await interaction.response.send_message(BotStrings.VACATION_ENABLED_OTHER.format(
                    name=flatmate["name"],
                    setter=interaction.user.display_name
                ))
        else:
            await interaction.response.send_message(message)

    @chores.command(name="stats")
    @app_commands.describe(name="Flatmate name to view stats for (optional)")
    async def show_stats(self, interaction: discord.Interaction, name: str = None):
        """Show statistics for yourself or another flatmate."""
        # If no name is provided, use the requestor's name
        if not name:
            flatmate = self.config_manager.get_flatmate_by_discord_id(interaction.user.id)
            if not flatmate:
                await interaction.response.send_message("You are not registered as a flatmate.")
                return
            name = flatmate["name"]

        # Get the stats for the specified flatmate
        stats = self.config_manager.get_flatmate_stats(name)
        if not stats:
            await interaction.response.send_message(f"No statistics found for {name}.")
            return

        # Calculate completion rate
        total_chores = stats["completed"] + stats["skipped"]
        completion_rate = 0
        if total_chores > 0:
            completion_rate = round((stats["completed"] / total_chores) * 100, 1)

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

    @chores.command(name="set_difficulty")
    @app_commands.describe(chore="Chore name", difficulty="Difficulty level (1-5)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_difficulty(self, interaction: discord.Interaction, chore: str, difficulty: int):
        """Set the difficulty level for a chore."""
        # Validate difficulty level
        if difficulty < 1 or difficulty > 5:
            await interaction.response.send_message("Difficulty must be between 1 and 5.")
            return

        success, message = self.config_manager.set_chore_difficulty(chore, difficulty)
        if success:
            await interaction.response.send_message(BotStrings.DIFFICULTY_SET.format(chore=chore, level=difficulty))
        else:
            await interaction.response.send_message(message)

    @chores.command(name="vote_difficulty")
    @app_commands.describe(chore="Chore to vote on difficulty")
    async def vote_difficulty(self, interaction: discord.Interaction, chore: str):
        """Start a vote on the difficulty level of a chore."""
        # Check if the chore exists
        if chore not in self.config_manager.get_chores():
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

        # Send a message that users can react to
        message = await interaction.channel.send(f"Vote on the difficulty of **{chore}**:")

        # Add reaction emojis
        emojis = self.config_manager.get_emoji()
        for i in range(1, 6):
            await message.add_reaction(emojis[f"difficulty_{i}"])

        # Store the message ID for later processing
        self.difficulty_vote_cache[message.id] = chore

        # Wait for 5 minutes then tally the votes
        await asyncio.sleep(300)  # 5 minutes

        try:
            # Fetch the updated message with reactions
            updated_message = await interaction.channel.fetch_message(message.id)

            # Count votes
            vote_counts = {i: 0 for i in range(1, 6)}

            for reaction in updated_message.reactions:
                # Skip reactions that aren't difficulty ratings
                if str(reaction.emoji) not in [emojis[f"difficulty_{i}"] for i in range(1, 6)]:
                    continue

                # Figure out which difficulty this reaction represents
                for i in range(1, 6):
                    if str(reaction.emoji) == emojis[f"difficulty_{i}"]:
                        # Count non-bot votes
                        users = [user async for user in reaction.users() if not user.bot]
                        vote_counts[i] = len(users)
                        break

            # Calculate the average difficulty (weighted average)
            total_votes = sum(vote_counts.values())
            if total_votes > 0:
                weighted_sum = sum(level * count for level, count in vote_counts.items())
                average_difficulty = round(weighted_sum / total_votes)

                # Ensure it's between 1-5
                average_difficulty = max(1, min(5, average_difficulty))

                # Update the chore difficulty
                self.config_manager.set_chore_difficulty(chore, average_difficulty)

                # Announce the result
                await interaction.channel.send(
                    BotStrings.DIFFICULTY_VOTE_RESULT.format(chore=chore, level=average_difficulty)
                )
            else:
                await interaction.channel.send(f"No votes were cast for **{chore}**.")

            # Remove from cache
            self.difficulty_vote_cache.pop(message.id, None)

        except Exception as e:
            logger.error(f"Error processing difficulty vote: {e}")
            await interaction.channel.send(f"There was an error processing the vote for **{chore}**.")

    @chores.command(name="next_week")
    async def next_week_planning(self, interaction: discord.Interaction):
        """Show and plan who will be included in next week's chore rotation."""
        # Get all flatmates who are not on vacation
        active_flatmates = self.config_manager.get_active_flatmates()
        if not active_flatmates:
            await interaction.response.send_message(BotStrings.ERR_NEXT_WEEK_NO_ACTIVE)
            return

        # Get excluded flatmates for next rotation
        excluded_flatmates = self.schedule_manager.get_excluded_for_next_rotation()

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
                break

            # Check if flatmate is already excluded for next rotation
            is_excluded = flatmate["name"] in excluded_flatmates

            # For each flatmate, show their status
            status = "❌ Excluded from next rotation" if is_excluded else "✅ Included in next rotation"

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

        # Get the sent message for adding reactions
        message = await interaction.original_response()

        # Add reactions for each flatmate
        for i, flatmate in enumerate(active_flatmates):
            if i < len(number_emojis):
                await message.add_reaction(number_emojis[i])

        # Store message ID and flatmates in cache for reaction handling
        self.next_week_planning_cache = {
            "message_id": message.id,
            "flatmates": [(f["name"], i) for i, f in enumerate(active_flatmates) if i < len(number_emojis)]
        }

    async def post_schedule(self, channel=None):
        """Post the weekly chore schedule with individual messages for each flatmate."""
        # Generate new schedule
        assignments = self.schedule_manager.generate_new_schedule()
        if not assignments:
            logger.warning("Failed to generate schedule: No assignments created")
            return

        # Update last posted date
        self.schedule_manager.update_last_posted_date()

        # Get the chores channel if not provided
        if channel is None:
            channel_id = self.config_manager.get_chores_channel_id()
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Chores channel not found: {channel_id}")
                return

        # First, post a header message for the weekly schedule
        await channel.send(BotStrings.SCHEDULE_HEADER)

        # Then post instructions (only once)
        if not self.instructions_sent:
            instructions_message = await channel.send(BotStrings.REACTION_INSTRUCTIONS)
            self.instructions_sent = True

        # Clear previous message cache
        self.message_cache = {}

        # Send individual messages for each assignment
        emojis = self.config_manager.get_emoji()
        for chore, flatmate_name in assignments.items():
            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
            if not flatmate:
                continue

            discord_id = flatmate["discord_id"]

            # Create the assignment message
            task_message = BotStrings.TASK_ASSIGNMENT.format(
                mention=f"<@{discord_id}>",
                chore=chore
            )

            # Send the message
            message = await channel.send(task_message)

            # Add reaction emojis for interaction
            await message.add_reaction(emojis["completed"])
            await message.add_reaction(emojis["unavailable"])

            # Cache the message ID for reaction handling
            self.message_cache[message.id] = (chore, flatmate_name)

        logger.info(f"Posted new schedule in channel {channel.name} ({channel.id})")

    async def send_reminders(self, channel=None):
        """Send reminders for pending chores."""
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

        # Get the chores channel if not provided
        if channel is None:
            channel_id = self.config_manager.get_chores_channel_id()
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Chores channel not found: {channel_id}")
                return

        # Send a reminder header
        await channel.send(BotStrings.REMINDER_HEADER)

        # Send individual reminders for each pending chore
        assignments = self.schedule_manager.get_current_assignments()
        for chore in pending_chores:
            flatmate_name = assignments.get(chore)
            if not flatmate_name:
                continue

            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
            if not flatmate:
                continue

            discord_id = flatmate["discord_id"]

            # Create the reminder message
            reminder_message = BotStrings.REMINDER_MESSAGE.format(
                mention=f"<@{discord_id}>",
                chore=chore
            )

            # Send the message
            await channel.send(reminder_message)

        logger.info(f"Sent reminders for {len(pending_chores)} pending chores")

    def _create_schedule_embed(self, assignments):
        """Create an embed for the chore schedule."""
        embed = discord.Embed(
            title=BotStrings.EMBED_SCHEDULE_TITLE,
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )

        # Add each chore and assigned flatmate to the embed
        for chore, flatmate_name in assignments.items():
            # Get chore difficulty
            difficulty = self.config_manager.get_chore_details(chore).get("difficulty", 1)
            difficulty_stars = "⭐" * difficulty

            # Get the flatmate's Discord ID to mention them
            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
            if flatmate:
                discord_id = flatmate["discord_id"]
                value = BotStrings.EMBED_TASK_ASSIGNED.format(mention=f"<@{discord_id}>")
            else:
                value = BotStrings.EMBED_TASK_ASSIGNED.format(mention=flatmate_name)

            embed.add_field(name=f"**{chore}** {difficulty_stars}", value=value, inline=False)

        # Add instructions for reactions
        emojis = self.config_manager.get_emoji()
        embed.add_field(
            name=BotStrings.EMBED_HOW_TO_RESPOND,
            value=BotStrings.EMBED_REACTIONS_GUIDE,
            inline=False
        )

        # Add footer with last updated time
        embed.set_footer(text=BotStrings.EMBED_SCHEDULE_FOOTER)

        return embed

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions to chore assignment messages."""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return

        # Check if this is a reaction to one of our tracked messages
        if payload.message_id in self.message_cache:
            await self._handle_chore_reaction(payload)
        elif payload.message_id in self.difficulty_vote_cache:
            # We don't need to do anything here, as voting is handled in the vote_difficulty command
            pass
        elif hasattr(self, 'next_week_planning_cache') and payload.message_id == self.next_week_planning_cache.get(
                "message_id"):
            # Handle reactions to next week planning
            await self._handle_next_week_planning_reaction(payload)

    async def _handle_chore_reaction(self, payload):
        """Handle reactions to chore assignment messages."""
        # Get the channel
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return

        # Get the message
        try:
            message = await channel.fetch_message(payload.message_id)
            if not message:
                return
        except Exception as e:
            logger.error(f"Failed to fetch message: {e}")
            return

        # Get the user who reacted
        user = self.bot.get_user(payload.user_id)
        if not user:
            return

        # Get the chore and assigned flatmate from our cache
        chore, assigned_flatmate_name = self.message_cache[payload.message_id]

        # Get the flatmate from the user's Discord ID
        flatmate = self.config_manager.get_flatmate_by_discord_id(payload.user_id)
        if not flatmate:
            # Remove reaction if the user is not a flatmate
            await message.remove_reaction(payload.emoji, user)
            return

        # Check if this is the assigned flatmate
        if flatmate["name"] != assigned_flatmate_name:
            # Remove reaction if not the assigned flatmate
            await message.remove_reaction(payload.emoji, user)
            await channel.send(
                f"{user.mention} This is not your assigned chore.",
                delete_after=10
            )
            return

        # Get the emoji configuration
        emojis = self.config_manager.get_emoji()
        emoji_name = str(payload.emoji)

        # Handle the reaction based on the emoji
        if emoji_name == emojis["completed"]:
            # Mark chore as completed
            success, _ = self.schedule_manager.mark_chore_completed(chore, flatmate["name"])

            if success:
                # Send completion message
                completion_msg = BotStrings.TASK_COMPLETED.format(
                    mention=user.mention,
                    chore=chore
                )
                await channel.send(completion_msg)

        elif emoji_name == emojis["unavailable"]:
            # Mark the original flatmate as having voted
            self.schedule_manager.add_voted_flatmate(flatmate["name"])

            # Randomly reassign the chore
            next_flatmate_name = self.schedule_manager.randomly_reassign_chore(
                chore,
                flatmate["name"]
            )

            if next_flatmate_name:
                # Get the next flatmate's Discord ID
                next_flatmate = self.config_manager.get_flatmate_by_name(next_flatmate_name)

                if next_flatmate:
                    next_discord_id = next_flatmate["discord_id"]

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

                    # Add reactions to the new message
                    await new_message.add_reaction(emojis["completed"])
                    await new_message.add_reaction(emojis["unavailable"])

                    # Update our message cache
                    self.message_cache[new_message.id] = (chore, next_flatmate_name)

                    # Remove the old message from the cache
                    self.message_cache.pop(payload.message_id, None)
            else:
                await channel.send(BotStrings.ERR_REASSIGN_FAILED.format(chore=chore))
        else:
            # Remove unrelated reactions
            await message.remove_reaction(payload.emoji, user)

    async def _handle_next_week_planning_reaction(self, payload):
        """Handle reactions to next week planning messages."""
        # Skip if not a tracked message
        if not hasattr(self, 'next_week_planning_cache') or self.next_week_planning_cache.get(
                "message_id") != payload.message_id:
            return

        # Get the channel
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return

        # Get the message
        try:
            message = await channel.fetch_message(payload.message_id)
            if not message:
                return
        except Exception as e:
            logger.error(f"Failed to fetch message: {e}")
            return

        # Get the user who reacted
        user = self.bot.get_user(payload.user_id)
        if not user or user.bot:  # Skip if bot reaction
            return

        # Get emoji
        emoji_name = str(payload.emoji)

        # Number emojis for flatmate selection
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # Check if the emoji is a number emoji
        if emoji_name in number_emojis:
            # Find the corresponding flatmate
            selected_index = number_emojis.index(emoji_name)
            selected_flatmate = None

            for name, idx in self.next_week_planning_cache["flatmates"]:
                if idx == selected_index:
                    selected_flatmate = name
                    break

            if not selected_flatmate:
                await message.remove_reaction(payload.emoji, user)
                return

            # Toggle the flatmate's exclusion status
            excluded_flatmates = self.schedule_manager.get_excluded_for_next_rotation()

            if selected_flatmate in excluded_flatmates:
                # Include the flatmate
                self.schedule_manager.include_in_next_rotation(selected_flatmate)
                await channel.send(
                    f"{user.mention} has included {selected_flatmate} in the next chore rotation.",
                    delete_after=5
                )
            else:
                # Exclude the flatmate
                self.schedule_manager.exclude_from_next_rotation(selected_flatmate)
                await channel.send(
                    f"{user.mention} has excluded {selected_flatmate} from the next chore rotation.",
                    delete_after=5
                )

            # Update the embed to reflect changes
            await self._update_next_week_planning_embed(message)

        # Remove the reaction
        await message.remove_reaction(payload.emoji, user)

    async def _update_next_week_planning_embed(self, message):
        """Update the next week planning embed to reflect current exclusions."""
        # Get all flatmates who are not on vacation
        active_flatmates = self.config_manager.get_active_flatmates()

        # Get excluded flatmates for next rotation
        excluded_flatmates = self.schedule_manager.get_excluded_for_next_rotation()

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
                break

            # Check if flatmate is excluded for next rotation
            is_excluded = flatmate["name"] in excluded_flatmates

            # Determine status
            status = "❌ Excluded from next rotation" if is_excluded else "✅ Included in next rotation"

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


async def setup(bot):
    chores_cog = ChoresCog(bot)
    await bot.add_cog(chores_cog)
    bot.tree.add_command(chores_cog.chores)