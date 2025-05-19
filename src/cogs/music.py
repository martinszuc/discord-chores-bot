import discord
from discord.ext import commands
import os
import random
import asyncio
import logging

logger = logging.getLogger('chores-bot')


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_folder = "music"  # Folder to store MP3 files
        self.is_busy = False  # Lock to prevent multiple simultaneous plays

        # Create music folder if it doesn't exist
        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)
            logger.info(f"Created music folder: {self.music_folder}")

        # Load configuration
        self.enabled = self.bot.config.get("music_celebration", {}).get("enabled", True)
        self.preferred_channel = self.bot.config.get("music_celebration", {}).get("channel_name", None)
        self.duration = self.bot.config.get("music_celebration", {}).get("duration", 30)  # Max seconds to play

        logger.info(f"MusicCog initialized (enabled: {self.enabled})")

    async def play_celebration(self, guild):
        """Play a random song to celebrate a completed chore."""
        if not self.enabled:
            logger.debug("Music celebration is disabled in config")
            return

        if self.is_busy:
            logger.debug("Already playing a celebration, skipping")
            return

        self.is_busy = True

        try:
            # Find a voice channel to join
            voice_channel = await self._find_voice_channel(guild)
            if not voice_channel:
                logger.warning("No suitable voice channel found")
                self.is_busy = False
                return

            # Get all MP3 files from the music folder
            mp3_files = [f for f in os.listdir(self.music_folder) if f.endswith('.mp3')]
            if not mp3_files:
                logger.warning("No MP3 files found in music folder")
                self.is_busy = False
                return

            # Select a random MP3 file
            random_mp3 = random.choice(mp3_files)
            file_path = os.path.join(self.music_folder, random_mp3)
            logger.info(f"Selected song for celebration: {random_mp3}")

            # Connect to the voice channel
            try:
                # Check if already connected to a voice channel in this guild
                if guild.voice_client:
                    await guild.voice_client.disconnect()
                    await asyncio.sleep(1)  # Brief delay to ensure clean disconnection

                voice_client = await voice_channel.connect()
                logger.info(f"Connected to voice channel: {voice_channel.name}")

                # Create FFmpeg audio source
                audio_source = discord.FFmpegPCMAudio(file_path)

                # Play the audio with a volume transformer to adjust volume
                volume = self.bot.config.get("music_celebration", {}).get("volume", 0.5)  # Default 50% volume
                transformed_source = discord.PCMVolumeTransformer(audio_source, volume=volume)

                voice_client.play(transformed_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._song_finished(e, voice_client), self.bot.loop))

                # Announce in the chores channel
                chores_channel_id = self.bot.config.get("chores_channel_id")
                if chores_channel_id:
                    chores_channel = guild.get_channel(chores_channel_id)
                    if chores_channel:
                        song_name = random_mp3.replace('.mp3', '').replace('_', ' ')
                        await chores_channel.send(f"🎵 Celebrating with: **{song_name}**")

                # Set a timer to disconnect after the duration
                self.bot.loop.create_task(self._disconnect_after_duration(voice_client))

            except Exception as e:
                logger.error(f"Error connecting to voice channel: {e}", exc_info=True)
                if guild.voice_client:
                    await guild.voice_client.disconnect()
                self.is_busy = False
                return

        except Exception as e:
            logger.error(f"Error in play_celebration: {e}", exc_info=True)
            self.is_busy = False

    async def _find_voice_channel(self, guild):
        """Find a suitable voice channel to join."""
        # Try to find the preferred channel first if configured
        if self.preferred_channel:
            channel = discord.utils.get(guild.voice_channels, name=self.preferred_channel)
            if channel:
                logger.debug(f"Found preferred voice channel: {channel.name}")
                return channel

        # Fall back to any voice channel with members
        for channel in guild.voice_channels:
            if len(channel.members) > 0:
                logger.debug(f"Found voice channel with members: {channel.name}")
                return channel

        # If no channel with members, just use the first voice channel
        if guild.voice_channels:
            logger.debug(f"Using first available voice channel: {guild.voice_channels[0].name}")
            return guild.voice_channels[0]

        # No voice channels found
        logger.warning("No voice channels found in the guild")
        return None

    async def _song_finished(self, error, voice_client):
        """Called when the song finishes playing."""
        if error:
            logger.error(f"Error during playback: {error}")

        # Only disconnect if the voice client is still connected and not already playing something else
        if voice_client and voice_client.is_connected() and not voice_client.is_playing():
            await voice_client.disconnect()
            logger.info("Disconnected from voice channel after playing celebration")

        self.is_busy = False

    async def _disconnect_after_duration(self, voice_client):
        """Disconnect after max duration to avoid playing too long."""
        try:
            await asyncio.sleep(self.duration)
            if voice_client and voice_client.is_connected():
                voice_client.stop()
                await voice_client.disconnect()
                logger.info(f"Disconnected after maximum duration ({self.duration}s)")
                self.is_busy = False
        except Exception as e:
            logger.error(f"Error in disconnect timer: {e}", exc_info=True)
            self.is_busy = False


async def setup(bot):
    logger.info("Setting up MusicCog")
    await bot.add_cog(MusicCog(bot))
    logger.info("MusicCog setup completed successfully")