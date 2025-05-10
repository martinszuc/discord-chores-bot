import discord
from discord import app_commands
from discord.ext import commands
import logging
import datetime
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

        embed = discord.Embed(
            title="Chores Bot Configuration",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        # Add flatmates
        flatmates_str = "\n".join([f"• {f['name']} (<@{f['discord_id']}>)" for f in flatmates])
        embed.add_field(name="Flatmates", value=flatmates_str or "None", inline=False)

        # Add chores
        chores_str = "\n".join([f"• {chore}" for chore in chores])
        embed.add_field(name="Chores", value=chores_str or "None", inline=False)

        # Add schedule
        embed.add_field(
            name="Posting Schedule",
            value=f"Day: {schedule['day']}\nTime: {schedule['time']}\nTimezone: {schedule['timezone']}",
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
    @app_commands.describe(name="Chore name to add")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_chore(self, interaction: discord.Interaction, name: str):
        """Add a new chore."""
        success, message = self.config_manager.add_chore(name)
        await interaction.response.send_message(message)

    @chores.command(name="remove_chore")
    @app_commands.describe(name="Chore name to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_chore(self, interaction: discord.Interaction, name: str):
        """Remove a chore."""
        success, message = self.config_manager.remove_chore(name)
        await interaction.response.send_message(message)

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

    def _create_schedule_embed(self, assignments):
        """Create an embed for the chore schedule."""
        embed = discord.Embed(
            title=BotStrings.EMBED_SCHEDULE_TITLE,
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )

        # Add each chore and assigned flatmate to the embed
        for chore, flatmate_name in assignments.items():
            # Get the flatmate's Discord ID to mention them
            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
            if flatmate:
                discord_id = flatmate["discord_id"]
                value = BotStrings.EMBED_TASK_ASSIGNED.format(mention=f"<@{discord_id}>")
            else:
                value = BotStrings.EMBED_TASK_ASSIGNED.format(mention=flatmate_name)

            embed.add_field(name=f"**{chore}**", value=value, inline=False)

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
        if payload.message_id not in self.message_cache:
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


async def setup(bot):
    chores_cog = ChoresCog(bot)
    await bot.add_cog(chores_cog)
    bot.tree.add_command(chores_cog.chores)