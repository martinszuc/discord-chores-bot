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

        logger.info("MusicCog initialized")

    async def play_celebration(self, guild):
        """Play a random song to celebrate a completed chore."""
        if self.is_busy:
            logger.debug("Already playing a celebration, skipping")
            return

        self.is_busy = True

        try:
            # Find the "wiz khalifa" voice channel
            voice_channel = discord.utils.get(guild.voice_channels, name="wiz khalifa")
            if not voice_channel:
                logger.warning("Voice channel 'wiz khalifa' not found")
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
                # Check if already connected to a voice channel
                if guild.voice_client:
                    await guild.voice_client.disconnect()

                voice_client = await voice_channel.connect()
                logger.info(f"Connected to voice channel: {voice_channel.name}")

                # Create FFmpeg audio source
                audio_source = discord.FFmpegPCMAudio(file_path)

                # Play the audio
                voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._song_finished(e, voice_client), self.bot.loop))

                # Announce in the chores channel
                chores_channel_id = self.bot.config.get("chores_channel_id")
                if chores_channel_id:
                    chores_channel = guild.get_channel(chores_channel_id)
                    if chores_channel:
                        await chores_channel.send(f"🎵 Celebrating with: **{random_mp3.replace('.mp3', '')}**")

            except Exception as e:
                logger.error(f"Error connecting to voice channel: {e}", exc_info=True)
                self.is_busy = False
                return

        except Exception as e:
            logger.error(f"Error in play_celebration: {e}", exc_info=True)
            self.is_busy = False

    async def _song_finished(self, error, voice_client):
        """Called when the song finishes playing."""
        if error:
            logger.error(f"Error during playback: {error}")

        # Wait a moment before disconnecting
        await asyncio.sleep(1)

        # Disconnect from the voice channel
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            logger.info("Disconnected from voice channel after playing celebration")

        self.is_busy = False


async def setup(bot):
    logger.info("Setting up MusicCog")
    await bot.add_cog(MusicCog(bot))
    logger.info("MusicCog setup completed successfully")