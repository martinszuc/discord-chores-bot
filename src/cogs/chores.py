import discord
from discord.ext import commands
import logging
import datetime
from src.utils.config_manager import ConfigManager
from src.utils.schedule_manager import ScheduleManager

logger = logging.getLogger('chores-bot')


class ChoresCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_manager = ConfigManager()
        self.schedule_manager = ScheduleManager(self.config_manager)

        # Cache message IDs for reactions
        self.message_cache = {}

    def cog_check(self, ctx):
        """Check if the command is being used in the chores channel."""
        chores_channel_id = self.config_manager.get_chores_channel_id()
        return ctx.channel.id == chores_channel_id

    @commands.group(name="chores", invoke_without_command=True)
    async def chores(self, ctx):
        """Base command for chores management. Shows the current schedule if no subcommand is provided."""
        if ctx.invoked_subcommand is None:
            await self.show_schedule(ctx)

    @chores.command(name="schedule")
    async def show_schedule(self, ctx):
        """Show the current chore schedule."""
        assignments = self.schedule_manager.get_current_assignments()
        if not assignments:
            await ctx.send("No chore schedule has been generated yet. Use `!chores next` to generate one.")
            return

        # Create an embed to display the schedule
        embed = self._create_schedule_embed(assignments)
        await ctx.send(embed=embed)

    @chores.command(name="next")
    @commands.has_permissions(manage_messages=True)
    async def next_schedule(self, ctx):
        """Generate and post the next chore schedule."""
        await self.post_schedule(ctx.channel)
        await ctx.send("New chore schedule has been posted!")

    @chores.command(name="reset")
    @commands.has_role("Admin")  # You can customize this
    async def reset_schedule(self, ctx):
        """Reset the chore rotation."""
        success, message = self.schedule_manager.reset_schedule()
        await ctx.send(message)

    @chores.command(name="config")
    async def show_config(self, ctx):
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

        await ctx.send(embed=embed)

    @chores.command(name="add_flatmate")
    @commands.has_permissions(administrator=True)
    async def add_flatmate(self, ctx, name: str, discord_id: int):
        """Add a new flatmate."""
        success, message = self.config_manager.add_flatmate(name, discord_id)
        await ctx.send(message)

    @chores.command(name="remove_flatmate")
    @commands.has_permissions(administrator=True)
    async def remove_flatmate(self, ctx, name: str):
        """Remove a flatmate."""
        success, message = self.config_manager.remove_flatmate(name)
        await ctx.send(message)

    @chores.command(name="add_chore")
    @commands.has_permissions(administrator=True)
    async def add_chore(self, ctx, *, chore_name: str):
        """Add a new chore."""
        success, message = self.config_manager.add_chore(chore_name)
        await ctx.send(message)

    @chores.command(name="remove_chore")
    @commands.has_permissions(administrator=True)
    async def remove_chore(self, ctx, *, chore_name: str):
        """Remove a chore."""
        success, message = self.config_manager.remove_chore(chore_name)
        await ctx.send(message)

    async def post_schedule(self, channel=None):
        """Post the weekly chore schedule."""
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

        # Create an embed with the schedule
        embed = self._create_schedule_embed(assignments)

        # Post the schedule
        message = await channel.send(
            "🔔 **Weekly Chore Schedule** 🔔\n"
            "React with the appropriate emoji to mark a chore as completed or to indicate you can't do it this week.",
            embed=embed
        )

        # Add reaction emojis for interaction
        emojis = self.config_manager.get_emoji()
        await message.add_reaction(emojis["completed"])
        await message.add_reaction(emojis["unavailable"])

        # Cache the message ID for reaction handling
        self.message_cache = {
            "message_id": message.id,
            "assignments": assignments
        }

        logger.info(f"Posted new schedule in channel {channel.name} ({channel.id})")

    def _create_schedule_embed(self, assignments):
        """Create an embed for the chore schedule."""
        embed = discord.Embed(
            title="📋 Weekly Chore Schedule",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )

        # Add each chore and assigned flatmate to the embed
        for chore, flatmate_name in assignments.items():
            # Get the flatmate's Discord ID to mention them
            flatmate = self.config_manager.get_flatmate_by_name(flatmate_name)
            if flatmate:
                discord_id = flatmate["discord_id"]
                value = f"🧹 Assigned to: <@{discord_id}>"
            else:
                value = f"🧹 Assigned to: {flatmate_name}"

            embed.add_field(name=f"**{chore}**", value=value, inline=False)

        # Add instructions for reactions
        emojis = self.config_manager.get_emoji()
        embed.add_field(
            name="How to respond",
            value=f"{emojis['completed']} - Mark as completed\n"
                  f"{emojis['unavailable']} - I can't do it this week (will be reassigned)",
            inline=False
        )

        # Add footer with last updated time
        embed.set_footer(text="Last updated")

        return embed

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions to the chore schedule."""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return

        # Check if this is a reaction to our schedule message
        if not self.message_cache or payload.message_id != self.message_cache.get("message_id"):
            return

        # Get the emoji configuration
        emojis = self.config_manager.get_emoji()
        emoji_name = str(payload.emoji)

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

        # Get the flatmate from the user's Discord ID
        flatmate = self.config_manager.get_flatmate_by_discord_id(payload.user_id)
        if not flatmate:
            # Remove reaction if the user is not a flatmate
            await message.remove_reaction(payload.emoji, user)
            return

        # Get the assignments
        assignments = self.message_cache.get("assignments", {})

        # Find the chore assigned to this flatmate
        assigned_chore = None
        for chore, flatmate_name in assignments.items():
            if flatmate_name == flatmate["name"]:
                assigned_chore = chore
                break

        if not assigned_chore:
            # Remove reaction if the flatmate has no assigned chore
            await message.remove_reaction(payload.emoji, user)
            await channel.send(f"{user.mention} You don't have any assigned chores this week.", delete_after=10)
            return

        # Handle the reaction based on the emoji
        if emoji_name == emojis["completed"]:
            # Mark chore as completed
            success, message_text = self.schedule_manager.mark_chore_completed(assigned_chore, flatmate["name"])
            await channel.send(f"✅ {user.mention} has completed their chore: **{assigned_chore}**")

        elif emoji_name == emojis["unavailable"]:
            # Reassign the chore
            next_flatmate = self.schedule_manager.rotate_assignment(assigned_chore)
            if next_flatmate:
                # Get the next flatmate's Discord ID
                next_discord_id = None
                next_flatmate_obj = self.config_manager.get_flatmate_by_name(next_flatmate)
                if next_flatmate_obj:
                    next_discord_id = next_flatmate_obj["discord_id"]

                # Send notification
                if next_discord_id:
                    await channel.send(
                        f"❌ {user.mention} can't complete their chore this week.\n"
                        f"**{assigned_chore}** has been reassigned to <@{next_discord_id}>."
                    )
                else:
                    await channel.send(
                        f"❌ {user.mention} can't complete their chore this week.\n"
                        f"**{assigned_chore}** has been reassigned to {next_flatmate}."
                    )

                # Update the embed with the new assignment
                self.message_cache["assignments"][assigned_chore] = next_flatmate
                embed = self._create_schedule_embed(self.message_cache["assignments"])
                await message.edit(embed=embed)
            else:
                await channel.send(f"Failed to reassign chore: {assigned_chore}")
        else:
            # Remove unrelated reactions
            await message.remove_reaction(payload.emoji, user)


async def setup(bot):
    await bot.add_cog(ChoresCog(bot))