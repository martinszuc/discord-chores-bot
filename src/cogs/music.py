import asyncio
import logging
import os
import random

import discord
from discord.ext import commands

logger = logging.getLogger('chores-bot')


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_folder = "music"
        self.is_busy = False

        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)
            logger.info(f"Created music folder: {self.music_folder}")

        self.enabled = self.bot.config.get("music_celebration", {}).get("enabled", True)
        self.preferred_channel = self.bot.config.get("music_celebration", {}).get("channel_name", None)
        self.duration = self.bot.config.get("music_celebration", {}).get("duration", 30)

        logger.info(f"MusicCog initialized (enabled: {self.enabled})")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.voice_client:
                await guild.voice_client.disconnect(force=True)
                logger.info(f"Cleaned up stale voice connection in {guild.name}")
        self.is_busy = False

    async def play_celebration(self, guild):
        """Play a random song to celebrate a completed chore."""
        if not self.enabled:
            logger.debug("Music celebration is disabled in config")
            return

        if not self.bot.bot_ready:
            logger.debug("Skipping celebration, bot not ready")
            return

        if self.is_busy:
            logger.debug("Already playing a celebration, skipping")
            return

        self.is_busy = True
        voice_client = None

        try:
            voice_channel = await self._find_voice_channel(guild)
            if not voice_channel:
                logger.warning("No suitable voice channel found")
                self.is_busy = False
                return

            mp3_files = [f for f in os.listdir(self.music_folder) if f.endswith('.mp3')]
            if not mp3_files:
                logger.warning("No MP3 files found in music folder")
                self.is_busy = False
                return

            random_mp3 = random.choice(mp3_files)
            file_path = os.path.join(self.music_folder, random_mp3)
            logger.info(f"Selected song for celebration: {random_mp3}")

            try:
                # Disconnect if already connected
                if guild.voice_client:
                    await guild.voice_client.disconnect(force=True)
                    await asyncio.sleep(2)

                # reconnect=False prevents discord.py retrying with an invalidated
                # session (4006), which causes an infinite retry loop
                voice_client = await voice_channel.connect(reconnect=False)
                logger.info(f"Connected to voice channel: {voice_channel.name}")

                audio_source = discord.FFmpegPCMAudio(file_path)
                volume = self.bot.config.get("music_celebration", {}).get("volume", 0.5)
                transformed_source = discord.PCMVolumeTransformer(audio_source, volume=volume)

                voice_client.play(
                    transformed_source,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self._song_finished(e, voice_client), self.bot.loop
                    )
                )

                asyncio.create_task(self._disconnect_after_duration(voice_client))
                logger.info(f"Started playback with {self.duration}s timeout")

            except Exception as e:
                logger.error(f"Error during playback: {e}", exc_info=True)
                if guild.voice_client:
                    await guild.voice_client.disconnect()
                self.is_busy = False
                return

        except Exception as e:
            logger.error(f"Error in play_celebration: {e}", exc_info=True)
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
            self.is_busy = False

    async def _song_finished(self, error, voice_client):
        """Called when the song finishes playing."""
        if error:
            logger.error(f"Error during playback: {error}")

        try:
            if voice_client and voice_client.is_connected() and not voice_client.is_playing():
                await voice_client.disconnect()
                logger.info("Disconnected from voice channel after song finished")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}", exc_info=True)
        finally:
            self.is_busy = False

    async def _disconnect_after_duration(self, voice_client):
        """Force disconnect after maximum duration."""
        try:
            await asyncio.sleep(self.duration)
            if voice_client and voice_client.is_connected():
                if voice_client.is_playing():
                    voice_client.stop()
                await voice_client.disconnect(force=True)
                logger.info(f"Disconnected after {self.duration}s timeout")
        except Exception as e:
            logger.error(f"Error in disconnect timer: {e}", exc_info=True)
        finally:
            self.is_busy = False

    async def _find_voice_channel(self, guild):
        """Find a suitable voice channel to join."""
        # Try wiz-khalifa first (note: your config says "wiz-khalifa" but code looks for "ez-khalifa")
        preferred = self.preferred_channel or "wiz-khalifa"
        channel = discord.utils.get(guild.voice_channels, name=preferred)
        if channel:
            logger.debug(f"Found preferred voice channel: {channel.name}")
            return channel

        # Fall back to any channel with members
        for channel in guild.voice_channels:
            if len(channel.members) > 0:
                logger.debug(f"Found voice channel with members: {channel.name}")
                return channel

        # Last resort: first available channel
        if guild.voice_channels:
            logger.debug(f"Using first available voice channel: {guild.voice_channels[0].name}")
            return guild.voice_channels[0]

        logger.warning("No voice channels found in the guild")
        return None


async def setup(bot):
    logger.info("Setting up MusicCog")
    await bot.add_cog(MusicCog(bot))
    logger.info("MusicCog setup completed successfully")