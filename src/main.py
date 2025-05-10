import os
import discord
from discord.ext import commands
import json
import asyncio
import logging
import datetime
import pytz
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger('chores-bot')


# Load configuration
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise


# Create data directory if it doesn't exist
def init_data_dir():
    Path("data").mkdir(exist_ok=True)


class ChoresBot(commands.Bot):
    def __init__(self, config):
        self.config = config
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None  # We'll use a custom help command
        )

        # Store the bot start time
        self.launched_at = datetime.datetime.now()

    async def setup_hook(self):
        # Load all cogs
        await self.load_extension("src.cogs.chores")
        await self.load_extension("src.cogs.admin")
        await self.load_extension("src.cogs.help")
        logger.info("All cogs loaded")

        # Schedule the first chore post
        self.loop.create_task(self.schedule_first_chore_post())

        # Schedule the first reminder
        self.loop.create_task(self.schedule_first_reminder())

        # Sync slash commands with Discord
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Serving {len(self.guilds)} guilds')

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"/choreshelp show"
            )
        )

    async def schedule_first_chore_post(self):
        """Schedule the first chore post based on the configured day and time."""
        try:
            # Get the chores cog
            chores_cog = self.get_cog("ChoresCog")
            if not chores_cog:
                logger.error("Chores cog not found")
                return

            # Get the configured day and time
            day_name = self.config["posting_day"]
            time_str = self.config["posting_time"]
            timezone = pytz.timezone(self.config["timezone"])

            # Calculate when the next posting should occur
            now = datetime.datetime.now(timezone)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day_idx = days.index(day_name)
            current_day_idx = now.weekday()

            # Calculate days until next posting
            days_until = (target_day_idx - current_day_idx) % 7
            if days_until == 0 and now.strftime('%H:%M') > time_str:
                days_until = 7

            # Parse the posting time
            hour, minute = map(int, time_str.split(':'))

            # Calculate the next posting time
            next_post = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_post = next_post + datetime.timedelta(days=days_until)

            # Calculate seconds until next posting
            seconds_until = (next_post - now).total_seconds()

            logger.info(f"Next chore post scheduled for {next_post.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"Waiting {seconds_until:.2f} seconds")

            # Schedule the first post
            await asyncio.sleep(seconds_until)
            await chores_cog.post_schedule()

            # Schedule weekly posts
            while True:
                await asyncio.sleep(7 * 24 * 60 * 60)  # Wait one week
                await chores_cog.post_schedule()

        except Exception as e:
            logger.error(f"Error in schedule_first_chore_post: {e}")

    async def schedule_first_reminder(self):
        """Schedule the first reminder based on the configured reminder settings."""
        try:
            # Get the chores cog
            chores_cog = self.get_cog("ChoresCog")
            if not chores_cog:
                logger.error("Chores cog not found")
                return

            # Get reminder settings
            reminder_settings = chores_cog.config_manager.get_reminder_settings()
            if not reminder_settings.get("enabled", True):
                logger.info("Reminders are disabled, not scheduling")
                return

            # Get the configured day and time
            day_name = reminder_settings.get("day", "Friday")
            time_str = reminder_settings.get("time", "18:00")
            timezone = pytz.timezone(self.config["timezone"])

            # Calculate when the next reminder should occur
            now = datetime.datetime.now(timezone)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day_idx = days.index(day_name)
            current_day_idx = now.weekday()

            # Calculate days until next reminder
            days_until = (target_day_idx - current_day_idx) % 7
            if days_until == 0 and now.strftime('%H:%M') > time_str:
                days_until = 7

            # Parse the reminder time
            hour, minute = map(int, time_str.split(':'))

            # Calculate the next reminder time
            next_reminder = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_reminder = next_reminder + datetime.timedelta(days=days_until)

            # Calculate seconds until next reminder
            seconds_until = (next_reminder - now).total_seconds()

            logger.info(f"Next reminder scheduled for {next_reminder.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"Waiting {seconds_until:.2f} seconds")

            # Schedule the first reminder
            await asyncio.sleep(seconds_until)

            # Get the chores channel
            channel_id = self.config["chores_channel_id"]
            channel = self.get_channel(channel_id)

            if channel:
                await chores_cog.send_reminders(channel)
            else:
                logger.error(f"Chores channel not found: {channel_id}")

            # Schedule weekly reminders
            while True:
                await asyncio.sleep(7 * 24 * 60 * 60)  # Wait one week

                # Check if reminders are still enabled
                reminder_settings = chores_cog.config_manager.get_reminder_settings()
                if not reminder_settings.get("enabled", True):
                    logger.info("Reminders are now disabled, stopping reminder schedule")
                    return

                # Get the chores channel
                channel_id = self.config["chores_channel_id"]
                channel = self.get_channel(channel_id)

                if channel:
                    await chores_cog.send_reminders(channel)
                else:
                    logger.error(f"Chores channel not found: {channel_id}")

        except Exception as e:
            logger.error(f"Error in schedule_first_reminder: {e}")


async def main():
    # Initialize data directory
    init_data_dir()

    # Load configuration
    config = load_config()

    # Create the bot
    global bot
    bot = ChoresBot(config)

    # Run the bot with the token from config
    await bot.start(config["token"])


if __name__ == "__main__":
    asyncio.run(main())