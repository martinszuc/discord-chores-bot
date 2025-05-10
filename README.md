# Discord Chores Bot

A Discord bot designed to manage and track chores for flatmates sharing an apartment. The bot posts weekly chore schedules, tracks task completion, and handles task rotation when someone is unavailable.

## Features

- 🗓️ Weekly chore schedule posting in a designated channel
- 👍 Task completion tracking with emoji reactions
- 🔄 Task rotation when someone is unavailable
- 🛠️ Easy configuration for flatmates and chores
- 🔐 Role-based permissions
- 🐳 Docker and Docker Compose support for easy deployment
- 📊 Statistics tracking for each flatmate
- ⭐ Chore difficulty ratings and balancing
- 🏖️ Vacation mode
- ⏰ Customizable reminders for pending chores
- 🔄 Next week planning and exclusions

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

Edit the `config.json` file to configure your bot. The example below shows the basic structure:

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
    "..."
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

See `config.example.json` for a fully documented configuration example.

## Commands

### Basic Commands
- `/chores show` - Show the current chore schedule
- `/chores config` - Show the current configuration
- `/chores vacation status:True/False [user:@user]` - Enable/disable vacation mode
- `/chores next_week` - Plan who will be included in next week's rotation
- `/chores stats [name]` - Show statistics for a flatmate

### Admin Commands
- `/choresadmin status` - Show bot status
- `/choresadmin reload_config` - Reload the bot configuration
- `/choresadmin reminders` - Configure reminder settings
- `/choresadmin test_reminder` - Test the reminder system
- `/choresadmin test_notification [chore]` - Test the notification system
- `/choresadmin stats_summary` - Show statistics for all flatmates
- `/choresadmin settings` - View or edit bot settings

### Flatmate Management
- `/chores add_flatmate name:name discord_id:id` - Add a new flatmate
- `/chores remove_flatmate name:name` - Remove a flatmate

### Chore Management
- `/chores add_chore name:chore_name difficulty:1-5` - Add a new chore
- `/chores remove_chore name:chore_name` - Remove a chore
- `/chores set_difficulty chore:chore_name difficulty:1-5` - Set chore difficulty
- `/chores vote_difficulty chore:chore_name` - Start a vote on chore difficulty

### Help Commands
- `/choreshelp show` - Display general help information
- `/choreshelp show command:command_name` - Display help for a specific command

## Emoji Reactions

- ✅ - Mark a chore as completed
- ❌ - Indicate you cannot complete a chore (will be reassigned)
- 1️⃣-5️⃣ - Vote on chore difficulty (when voting is active)

## Advanced Features

### Chore Difficulty and Assignment Balancing

Chores can have difficulty ratings from 1 to 5 stars. The bot uses these ratings to balance the workload when assigning chores:

1. Chores are assigned in order of difficulty (highest first)
2. The flatmate with the lowest total difficulty so far gets assigned the next chore
3. Flatmates who skip chores often get higher priority for future assignments
4. Flatmates who recently returned from vacation get priority for easier chores

### Vacation Mode

Flatmates can enable vacation mode to be excluded from chore assignments:

- Use `/chores vacation status:True` to enable vacation mode
- Use `/chores vacation status:False` to disable vacation mode
- When returning from vacation, flatmates get a boost in priority for easier chores

### Next Week Planning

The `/chores next_week` command allows you to plan who will be included in the next chore rotation:

1. A message with all active flatmates will be displayed
2. React with the number emoji next to a flatmate to toggle their inclusion/exclusion
3. Exclusions are temporary and will be cleared after the next schedule is generated

### Automated Reminders

The bot can send automatic reminders for pending chores:

- Configure reminder settings with `/choresadmin reminders`
- Set the day and time when reminders should be sent
- Flatmates will be reminded of chores they haven't completed yet

### Viewing Logs

If you're running with Docker:

```bash
docker logs -f discord-chores-bot
```

If you're running directly with Python:

```bash
tail -f bot.log
```

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
