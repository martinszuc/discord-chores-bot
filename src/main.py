import asyncio
import datetime
import json
import logging
import os
from pathlib import Path

import discord
import pytz
from discord.ext import commands

from src.utils.connection_handler import ConnectionHandler

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


def get_bot_token(config):
    """Get bot token from environment variable or config file."""
    logger.info("Getting bot token")

    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        logger.info("✅ Using Discord token from environment variable")
        return token

    token = config.get("token")
    if token and token != "YOUR_DISCORD_BOT_TOKEN":
        logger.info("Using Discord token from config file")
        return token

    logger.critical(
        "❌ Bot token not found! Please set DISCORD_BOT_TOKEN environment variable or add token to config.json")
    return None


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
    def __init__(self, config, token):
        logger.info("Initializing ChoresBot")
        self.config = config
        self.token = token

        # Connection tracking
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.last_disconnect_time = None
        self.is_ready = False

        # Connection handler for monitoring
        self.connection_handler = None

        # Enhanced intents for better connection stability
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        intents.guilds = True
        intents.voice_states = True

        logger.debug(f"Bot configured with prefix: {config['prefix']}")

        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None,
            heartbeat_timeout=60.0,  # Increased timeout for unstable connections
            max_messages=1000  # Limit message cache to reduce memory usage
        )

        self.launched_at = datetime.datetime.now()
        logger.info(f"Bot initialization completed at {self.launched_at}")

    async def setup_hook(self):
        """Set up all cogs and scheduled tasks."""
        logger.info("Setting up bot hooks and extensions")

        loaded_cogs = []

        # Load all cogs with error handling
        cogs = [
            ("src.cogs.chores", "chores"),
            ("src.cogs.admin", "admin"),
            ("src.cogs.help", "help"),
            ("src.cogs.music", "music")
        ]

        for cog_path, cog_name in cogs:
            try:
                await self.load_extension(cog_path)
                loaded_cogs.append(cog_name)
                logger.info(f"Loaded {cog_name} cog")
            except Exception as e:
                logger.error(f"Failed to load {cog_name} cog: {e}", exc_info=True)

        logger.info(f"Cog loading completed. Loaded cogs: {', '.join(loaded_cogs)}")

        # Initialize connection handler
        logger.info("Initializing connection handler")
        self.connection_handler = ConnectionHandler(self)
        self.loop.create_task(self.connection_handler.monitor_connection_health())
        logger.info("Connection monitoring started")

        # Schedule tasks
        logger.info("Creating task for first chore post")
        self.loop.create_task(self.schedule_first_chore_post())

        logger.info("Creating task for first reminder")
        self.loop.create_task(self.schedule_first_reminder())

        # Sync slash commands
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
        logger.info(f'✅ {self.user} has connected to Discord!')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Serving {len(self.guilds)} guild(s)')

        for guild in self.guilds:
            logger.debug(f"Connected to guild: {guild.name} (ID: {guild.id})")

        # Reset reconnection counter on successful connection
        self.reconnect_attempts = 0
        self.is_ready = True

        # Notify connection handler
        if self.connection_handler:
            await self.connection_handler.on_connect()

        activity_text = f"/choreshelp show"
        logger.info(f"Setting bot activity status to: {activity_text}")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=activity_text
            )
        )
        logger.info("🎉 Bot is now fully ready and operational!")

    async def on_disconnect(self):
        """Called when bot disconnects from Discord."""
        self.reconnect_attempts += 1
        self.last_disconnect_time = datetime.datetime.now()
        self.is_ready = False

        logger.warning(
            f"⚠️ Bot disconnected from Discord (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")

        # Notify connection handler
        if self.connection_handler:
            await self.connection_handler.on_disconnect()

        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"❌ Max reconnection attempts ({self.max_reconnect_attempts}) reached")
            logger.error("Bot will restart via Docker/system restart policy")

    async def on_resumed(self):
        """Called when connection resumes after disconnect."""
        if self.last_disconnect_time:
            downtime = datetime.datetime.now() - self.last_disconnect_time
            logger.info(f"✅ Bot resumed connection to Discord after {downtime.total_seconds():.1f} seconds")
        else:
            logger.info("✅ Bot resumed connection to Discord")

        self.reconnect_attempts = 0
        self.is_ready = True

        # Notify connection handler
        if self.connection_handler:
            await self.connection_handler.on_resumed()

    async def on_connect(self):
        """Called when bot establishes connection to Discord."""
        logger.info("🔗 Bot connected to Discord gateway")

        # Notify connection handler
        if self.connection_handler:
            await self.connection_handler.on_connect()

    async def on_error(self, event_method: str, *args, **kwargs):
        """Handle errors in event methods."""
        logger.error(f"Error in event {event_method}", exc_info=True)

    async def schedule_first_chore_post(self):
        """Schedule the first chore post based on the configured day and time."""
        logger.info("Scheduling first chore post")
        try:
            chores_cog = self.get_cog("ChoresCog")
            if not chores_cog:
                logger.error("Chores cog not found, cannot schedule chore post")
                return

            day_name = self.config["posting_day"]
            time_str = self.config["posting_time"]
            timezone = pytz.timezone(self.config["timezone"])

            logger.info(f"Configured posting schedule: {day_name} at {time_str} ({timezone})")

            now = datetime.datetime.now(timezone)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day_idx = days.index(day_name)
            current_day_idx = now.weekday()

            days_until = (target_day_idx - current_day_idx) % 7
            if days_until == 0 and now.strftime('%H:%M') > time_str:
                logger.debug("Today is posting day but time has passed, scheduling for next week")
                days_until = 7

            logger.debug(
                f"Current day index: {current_day_idx} ({days[current_day_idx]}), Target day index: {target_day_idx} ({days[target_day_idx]})")
            logger.debug(f"Days until next posting: {days_until}")

            hour, minute = map(int, time_str.split(':'))
            next_post = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_post = next_post + datetime.timedelta(days=days_until)

            seconds_until = (next_post - now).total_seconds()

            logger.info(f"Next chore post scheduled for {next_post.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"Waiting {seconds_until:.2f} seconds")

            if seconds_until < 0:
                logger.info("Negative wait time detected, skipping immediate posting and scheduling for next week")
                next_post = next_post + datetime.timedelta(days=7)
                seconds_until = (next_post - now).total_seconds()
                logger.info(
                    f"Rescheduled for {next_post.strftime('%Y-%m-%d %H:%M:%S %Z')}, waiting {seconds_until:.2f} seconds")

            await asyncio.sleep(seconds_until)
            logger.info("Time to post chore schedule, calling post_schedule")
            await chores_cog.post_schedule()
            logger.info("First chore schedule posted successfully")

            # Schedule weekly posts
            logger.info("Setting up recurring weekly chore posts")
            while True:
                one_week_seconds = 7 * 24 * 60 * 60
                logger.info(f"Waiting {one_week_seconds} seconds until next posting")
                await asyncio.sleep(one_week_seconds)
                logger.info("Time for weekly chore schedule posting")
                await chores_cog.post_schedule()
                logger.info("Weekly chore schedule posted successfully")

        except Exception as e:
            logger.error(f"Error in schedule_first_chore_post: {e}", exc_info=True)

    async def schedule_first_reminder(self):
        """Schedule the first reminder based on the configured reminder settings."""
        logger.info("Scheduling first reminder")
        try:
            chores_cog = self.get_cog("ChoresCog")
            if not chores_cog:
                logger.error("Chores cog not found, cannot schedule reminders")
                return

            reminder_settings = chores_cog.config_manager.get_reminder_settings()
            if not reminder_settings.get("enabled", True):
                logger.info("Reminders are disabled, not scheduling")
                return

            day_name = reminder_settings.get("day", "Friday")
            time_str = reminder_settings.get("time", "18:00")
            timezone = pytz.timezone(self.config["timezone"])

            logger.info(f"Configured reminder schedule: {day_name} at {time_str} ({timezone})")

            now = datetime.datetime.now(timezone)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day_idx = days.index(day_name)
            current_day_idx = now.weekday()

            logger.debug(
                f"Current day index: {current_day_idx} ({days[current_day_idx]}), Target day index: {target_day_idx} ({days[target_day_idx]})")

            days_until = (target_day_idx - current_day_idx) % 7
            if days_until == 0 and now.strftime('%H:%M') > time_str:
                logger.debug("Today is reminder day but time has passed, scheduling for next week")
                days_until = 7

            logger.debug(f"Days until next reminder: {days_until}")

            hour, minute = map(int, time_str.split(':'))
            next_reminder = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_reminder = next_reminder + datetime.timedelta(days=days_until)

            seconds_until = (next_reminder - now).total_seconds()

            logger.info(f"Next reminder scheduled for {next_reminder.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"Waiting {seconds_until:.2f} seconds")

            await asyncio.sleep(seconds_until)

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
                await asyncio.sleep(one_week_seconds)

                reminder_settings = chores_cog.config_manager.get_reminder_settings()
                if not reminder_settings.get("enabled", True):
                    logger.info("Reminders are now disabled, stopping reminder schedule")
                    return

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
    logger.info("🚀 Starting Discord Chores Bot")

    init_data_dir()

    logger.info("Loading configuration")
    try:
        config = load_config()
    except Exception as e:
        logger.critical(f"Failed to start bot due to configuration error: {e}")
        return

    token = get_bot_token(config)
    if not token:
        logger.critical("❌ Cannot start bot without a valid token!")
        logger.info("💡 Set environment variable: DISCORD_BOT_TOKEN=your_bot_token")
        return

    if not config.get("chores_channel_id"):
        logger.warning("Chores channel ID not set in config.json")

    logger.info("Creating bot instance")
    global bot
    bot = ChoresBot(config, token)

    logger.info("🎬 Starting bot...")
    try:
        await bot.start(token)
    except discord.LoginFailure:
        logger.critical("❌ Invalid bot token. Please check your DISCORD_BOT_TOKEN environment variable.")
    except Exception as e:
        logger.critical(f"Error starting bot: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Script executed directly")
    asyncio.run(main())