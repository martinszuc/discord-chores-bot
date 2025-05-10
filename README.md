# Discord Chores Bot

A Discord bot designed to manage and track chores for flatmates sharing an apartment. The bot posts weekly chore schedules, tracks task completion, and handles task rotation when someone is unavailable.

## Features

- 🗓️ Weekly chore schedule posting in a designated channel
- 👍 Task completion tracking with emoji reactions
- 🔄 Task rotation when someone is unavailable
- 🛠️ Easy configuration for flatmates and chores
- 🔐 Role-based permissions
- 🐳 Docker and Docker Compose support for easy deployment

## Requirements

- Python 3.8+
- Docker and Docker Compose
- Discord Bot Token (from Discord Developer Portal)

## Quick Start

1. Clone the repository:
   ```bash
   git clone git@github.com:martinszuc/discord-chores-bot.git
   cd discord-chores-bot
   ```

2. Create a `config.json` file based on the template:
   ```bash
   cp config.example.json config.json
   ```

3. Edit the `config.json` file with your Discord bot token, channel ID, and flatmate information

4. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" tab and click "Add Bot"
4. Copy the token and add it to your `config.json` file
5. Go to OAuth2 > URL Generator
6. Select the following scopes:
   - `bot`
   - `applications.commands`
7. Select the following bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Add Reactions
   - Embed Links
   - Mention Everyone
   - Manage Messages
8. Copy the generated URL and open it in a browser to add the bot to your server

## Configuration

Edit the `config.json` file to configure your bot:

```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN",
  "prefix": "!",
  "chores_channel_id": 123456789012345678,
  "admin_role_id": 123456789012345678,
  "posting_day": "Monday",
  "posting_time": "9:00",
  "timezone": "Europe/Bratislava",
  "flatmates": [
    {
      "name": "Dominik",
      "discord_id": 123456789012345678
    },
    ...
  ],
  "chores": [
    "Kupelka",
    "Zachod",
    "Vysavanie",
    "Zmyvanie",
    "Kuchyňa"
  ]
}
```

## Commands

- `!chores help` - Display help information
- `!chores schedule` - Show the current chore schedule
- `!chores next` - Post the next chore schedule immediately
- `!chores reset` - Reset the chore rotation
- `!chores config` - Show the current configuration
- `!chores add_flatmate <name> <discord_id>` - Add a new flatmate (admin only)
- `!chores remove_flatmate <name>` - Remove a flatmate (admin only)
- `!chores add_chore <chore_name>` - Add a new chore (admin only)
- `!chores remove_chore <chore_name>` - Remove a chore (admin only)

## Emoji Reactions

- ✅ - Mark a chore as completed
- ❌ - Indicate you cannot complete a chore (will be reassigned)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
