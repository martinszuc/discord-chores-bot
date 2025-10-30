"""
Connection handler utility for managing Discord bot reconnections.
Provides additional resilience for network interruptions.
"""

import asyncio
import datetime
import logging

logger = logging.getLogger('chores-bot')


class ConnectionHandler:
    """Handle connection issues and provide reconnection strategies."""

    def __init__(self, bot):
        self.bot = bot
        self.connection_history = []
        self.last_successful_connect = None
        self.total_disconnects = 0

    def log_connection_event(self, event_type: str):
        """Log connection events for monitoring."""
        timestamp = datetime.datetime.now()
        self.connection_history.append({
            'timestamp': timestamp,
            'event': event_type
        })

        # Keep only last 100 events
        if len(self.connection_history) > 100:
            self.connection_history = self.connection_history[-100:]

        logger.info(f"Connection event: {event_type} at {timestamp}")

    def get_uptime(self) -> datetime.timedelta:
        """Get bot uptime since last successful connection."""
        if self.last_successful_connect:
            return datetime.datetime.now() - self.last_successful_connect
        return datetime.timedelta(0)

    def get_connection_stats(self) -> dict:
        """Get connection statistics."""
        return {
            'total_disconnects': self.total_disconnects,
            'uptime': self.get_uptime(),
            'last_successful_connect': self.last_successful_connect,
            'recent_events': self.connection_history[-10:]
        }

    async def on_connect(self):
        """Handle successful connection."""
        self.last_successful_connect = datetime.datetime.now()
        self.log_connection_event('CONNECTED')
        logger.info("✅ Successfully connected to Discord")

    async def on_disconnect(self):
        """Handle disconnection."""
        self.total_disconnects += 1
        self.log_connection_event('DISCONNECTED')
        logger.warning(f"⚠️ Disconnected from Discord (total disconnects: {self.total_disconnects})")

    async def on_resumed(self):
        """Handle connection resume."""
        self.log_connection_event('RESUMED')
        uptime = self.get_uptime()
        logger.info(f"✅ Connection resumed (uptime: {uptime})")

    async def monitor_connection_health(self):
        """Periodically monitor connection health."""
        while True:
            await asyncio.sleep(300)  # Check every 5 minutes

            if not self.bot.is_ready:
                logger.warning("⚠️ Bot is not in ready state")
                continue

            stats = self.get_connection_stats()
            uptime = stats['uptime']
            logger.info(f"Connection health check - Uptime: {uptime}, Disconnects: {stats['total_disconnects']}")

            # Log warning if too many recent disconnects
            recent_disconnects = sum(1 for event in stats['recent_events']
                                     if event['event'] == 'DISCONNECTED')
            if recent_disconnects > 3:
                logger.warning(f"⚠️ High disconnect rate detected: {recent_disconnects} in last 10 events")


async def setup_connection_monitoring(bot):
    """Set up connection monitoring for the bot."""
    handler = ConnectionHandler(bot)

    # Start monitoring task
    bot.loop.create_task(handler.monitor_connection_health())

    logger.info("Connection monitoring initialized")
    return handler