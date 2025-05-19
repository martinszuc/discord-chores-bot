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
    """Load configuration from config.json file."""
    logger.info("Loading configuration from config.json")
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(
                f"Configuration loaded successfully. Found {len(config.get('flatmates', []))} flatmates and {len(config.get('chores', []))} chores")
            return config
    except FileNotFoundError:
        logger.critical("config.json file not found. Please create a config file based on the template.")
        raise
    except json.JSONDecodeError as e:
        logger.critical(f"Invalid JSON in config.json: {e}")
        raise
    except Exception as e:
        logger.critical(f"Failed to load config: {e}")
        raise


# Create data directory if it doesn't exist
def init_data_dir():
    """Initialize data directory for persistent storage."""
    logger.info("Initializing data directory")
    data_dir = Path("data")
    if not data_dir.exists():
        logger.info("Data directory does not exist, creating it")
        data_dir.mkdir(exist_ok=True)
    else:
        logger.debug("Data directory already exists")


class ChoresBot(commands.Bot):
    def __init__(self, config):
        logger.info("Initializing ChoresBot")
        self.config = config
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True

        logger.debug(f"Bot configured with prefix: {config['prefix']}")

        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None  # We'll use a custom help command
        )

        # Store the bot start time
        self.launched_at = datetime.datetime.now()
        logger.info(f"Bot initialization completed at {self.launched_at}")

    async def setup_hook(self):
        """Set up all cogs and scheduled tasks."""
        logger.info("Setting up bot hooks and extensions")

        # Track loaded cogs
        loaded_cogs = []

        # Load all cogs
        try:
            await self.load_extension("src.cogs.chores")
            loaded_cogs.append("chores")
            logger.info("Loaded chores cog")
        except Exception as e:
            logger.error(f"Failed to load chores cog: {e}", exc_info=True)

        try:
            await self.load_extension("src.cogs.admin")
            loaded_cogs.append("admin")
            logger.info("Loaded admin cog")
        except Exception as e:
            logger.error(f"Failed to load admin cog: {e}", exc_info=True)

        try:
            await self.load_extension("src.cogs.help")
            loaded_cogs.append("help")
            logger.info("Loaded help cog")
        except Exception as e:
            logger.error(f"Failed to load help cog: {e}", exc_info=True)

        # Load the fix rotation cog
        try:
            await self.load_extension("src.cogs.fix_rotation")
            loaded_cogs.append("fix_rotation")
            logger.info("Loaded fix_rotation cog")
        except Exception as e:
            logger.error(f"Failed to load fix_rotation cog: {e}", exc_info=True)

        logger.info(f"Cog loading completed. Loaded cogs: {', '.join(loaded_cogs)}")

        # Schedule the first chore post
        logger.info("Creating task for first chore post")
        self.loop.create_task(self.schedule_first_chore_post())

        # Schedule the first reminder
        logger.info("Creating task for first reminder")
        self.loop.create_task(self.schedule_first_reminder())

        # Sync slash commands with Discord
        try:
            logger.info("Syncing slash commands with Discord")
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
            for cmd in synced:
                logger.debug(f"Synced command: {cmd.name}")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}", exc_info=True)

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Serving {len(self.guilds)} guild(s)')

        for guild in self.guilds:
            logger.debug(f"Connected to guild: {guild.name} (ID: {guild.id})")

        # Set bot status
        activity_text = f"/choreshelp show"
        logger.info(f"Setting bot activity status to: {activity_text}")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=activity_text
            )
        )
        logger.info("Bot is now fully ready")

    async def schedule_first_chore_post(self):
        """Schedule the first chore post based on the configured day and time."""
        logger.info("Scheduling first chore post")
        try:
            # Get the chores cog
            chores_cog = self.get_cog("ChoresCog")
            if not chores_cog:
                logger.error("Chores cog not found, cannot schedule chore post")
                return

            # Get the configured day and time
            day_name = self.config["posting_day"]
            time_str = self.config["posting_time"]
            timezone = pytz.timezone(self.config["timezone"])

            logger.info(f"Configured posting schedule: {day_name} at {time_str} ({timezone})")

            # Calculate when the next posting should occur
            now = datetime.datetime.now(timezone)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day_idx = days.index(day_name)
            current_day_idx = now.weekday()

            # Calculate days until next posting
            days_until = (target_day_idx - current_day_idx) % 7
            if days_until == 0 and now.strftime('%H:%M') > time_str:
                logger.debug("Today is posting day but time has passed, scheduling for next week")
                days_until = 7

            logger.debug(
                f"Current day index: {current_day_idx} ({days[current_day_idx]}), Target day index: {target_day_idx} ({days[target_day_idx]})")
            logger.debug(f"Days until next posting: {days_until}")

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
            logger.info("Time to post chore schedule, calling post_schedule")
            await chores_cog.post_schedule()
            logger.info("First chore schedule posted successfully")

            # Schedule weekly posts
            logger.info("Setting up recurring weekly chore posts")
            while True:
                one_week_seconds = 7 * 24 * 60 * 60
                logger.info(f"Waiting {one_week_seconds} seconds until next posting")
                await asyncio.sleep(one_week_seconds)  # Wait one week
                logger.info("Time for weekly chore schedule posting")
                await chores_cog.post_schedule()
                logger.info("Weekly chore schedule posted successfully")

        except Exception as e:
            logger.error(f"Error in schedule_first_chore_post: {e}", exc_info=True)

    async def schedule_first_reminder(self):
        """Schedule the first reminder based on the configured reminder settings."""
        logger.info("Scheduling first reminder")
        try:
            # Get the chores cog
            chores_cog = self.get_cog("ChoresCog")
            if not chores_cog:
                logger.error("Chores cog not found, cannot schedule reminders")
                return

            # Get reminder settings
            reminder_settings = chores_cog.config_manager.get_reminder_settings()
            if not reminder_settings.get("enabled", True):
                logger.info("Reminders are disabled, not scheduling")
                return

            # Get the configured day and time
            day_name = reminder_settings.get("day", "Friday")
            time_str = reminder_settings.get("time", "11:00")
            timezone = pytz.timezone(self.config["timezone"])

            logger.info(f"Configured reminder schedule: {day_name} at {time_str} ({timezone})")

            # Calculate when the next reminder should occur
            now = datetime.datetime.now(timezone)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day_idx = days.index(day_name)
            current_day_idx = now.weekday()

            logger.debug(
                f"Current day index: {current_day_idx} ({days[current_day_idx]}), Target day index: {target_day_idx} ({days[target_day_idx]})")

            # Calculate days until next reminder
            days_until = (target_day_idx - current_day_idx) % 7
            if days_until == 0 and now.strftime('%H:%M') > time_str:
                logger.debug("Today is reminder day but time has passed, scheduling for next week")
                days_until = 7

            logger.debug(f"Days until next reminder: {days_until}")

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
                logger.info(f"Sending reminders in channel {channel.name} (ID: {channel_id})")
                await chores_cog.send_reminders(channel)
                logger.info("Reminders sent successfully")
            else:
                logger.error(f"Chores channel not found: {channel_id}")

            # Schedule weekly reminders
            logger.info("Setting up recurring weekly reminders")
            while True:
                one_week_seconds = 7 * 24 * 60 * 60
                logger.info(f"Waiting {one_week_seconds} seconds until next reminder")
                await asyncio.sleep(one_week_seconds)  # Wait one week

                # Check if reminders are still enabled
                reminder_settings = chores_cog.config_manager.get_reminder_settings()
                if not reminder_settings.get("enabled", True):
                    logger.info("Reminders are now disabled, stopping reminder schedule")
                    return

                # Get the chores channel
                channel_id = self.config["chores_channel_id"]
                channel = self.get_channel(channel_id)

                if channel:
                    logger.info(f"Sending weekly reminders in channel {channel.name} (ID: {channel_id})")
                    await chores_cog.send_reminders(channel)
                    logger.info("Weekly reminders sent successfully")
                else:
                    logger.error(f"Chores channel not found: {channel_id}")

        except Exception as e:
            logger.error(f"Error in schedule_first_reminder: {e}", exc_info=True)


async def main():
    """Main entry point for the bot."""
    logger.info("Starting Discord Chores Bot")

    # Initialize data directory
    logger.info("Initializing data directory")
    init_data_dir()

    # Load configuration
    logger.info("Loading configuration")
    try:
        config = load_config()
    except Exception as e:
        logger.critical(f"Failed to start bot due to configuration error: {e}")
        return

    # Check critical config values
    if not config.get("token"):
        logger.critical("Bot token not found in config.json")
        return

    if not config.get("chores_channel_id"):
        logger.warning("Chores channel ID not set in config.json")

    # Create the bot
    logger.info("Creating bot instance")
    global bot
    bot = ChoresBot(config)

    # Run the bot with the token from config
    logger.info("Starting bot...")
    try:
        await bot.start(config["token"])
    except discord.LoginFailure:
        logger.critical("Invalid bot token. Please check your configuration.")
    except Exception as e:
        logger.critical(f"Error starting bot: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Script executed directly")
    asyncio.run(main())