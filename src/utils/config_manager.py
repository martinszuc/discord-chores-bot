import json
import logging
import os
from pathlib import Path

logger = logging.getLogger('chores-bot')


class ConfigManager:
    def __init__(self, config_path="config.json"):
        logger.info(f"Initializing ConfigManager with config path: {config_path}")
        self.config_path = config_path
        self.config = self._load_config()
        logger.debug("ConfigManager initialized successfully")

    def _load_config(self):
        """Load configuration from the config file."""
        logger.info(f"Loading configuration from: {self.config_path}")
        try:
            if not os.path.exists(self.config_path):
                logger.critical(f"Config file not found: {self.config_path}")
                raise FileNotFoundError(f"Config file not found: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(
                    f"Config loaded successfully with {len(config.get('flatmates', []))} flatmates and {len(config.get('chores', []))} chores")
                return config
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            logger.critical(f"Failed to load config: {e}", exc_info=True)
            raise

    def save_config(self):
        """Save the current configuration to the config file."""
        logger.info(f"Saving configuration to: {self.config_path}")
        try:
            # Create parent directory if it doesn't exist
            Path(os.path.dirname(self.config_path)).mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Config saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}", exc_info=True)
            raise

    def get_token(self):
        """Get the Discord bot token."""
        logger.debug("Getting Discord bot token")
        token = self.config.get("token")
        if not token or token == "YOUR_DISCORD_BOT_TOKEN":
            logger.warning("Bot token not properly configured or using placeholder value")
        return token

    def get_prefix(self):
        """Get the command prefix."""
        logger.debug("Getting command prefix")
        prefix = self.config.get("prefix", "!")
        logger.debug(f"Command prefix: {prefix}")
        return prefix

    def get_chores_channel_id(self):
        """Get the ID of the chores channel."""
        logger.debug("Getting chores channel ID")
        channel_id = self.config.get("chores_channel_id")
        logger.debug(f"Chores channel ID: {channel_id}")
        return channel_id

    def get_admin_role_id(self):
        """Get the ID of the admin role."""
        logger.debug("Getting admin role ID")
        role_id = self.config.get("admin_role_id")
        logger.debug(f"Admin role ID: {role_id}")
        return role_id

    def get_flatmates(self):
        """Get the list of flatmates."""
        logger.debug("Getting list of flatmates")
        flatmates = self.config.get("flatmates", [])
        logger.debug(f"Found {len(flatmates)} flatmates")
        return flatmates

    def get_active_flatmates(self):
        """Get the list of flatmates who are not on vacation."""
        logger.debug("Getting list of active flatmates (not on vacation)")
        flatmates = self.get_flatmates()
        active_flatmates = [f for f in flatmates if not f.get("on_vacation", False)]
        logger.debug(f"Found {len(active_flatmates)} active flatmates out of {len(flatmates)} total")
        return active_flatmates

    def get_flatmate_by_name(self, name):
        """Get a flatmate by name."""
        logger.debug(f"Looking for flatmate with name: {name}")
        for flatmate in self.get_flatmates():
            if flatmate["name"].lower() == name.lower():
                logger.debug(f"Found flatmate: {flatmate['name']} (ID: {flatmate['discord_id']})")
                return flatmate
        logger.debug(f"Flatmate not found with name: {name}")
        return None

    def get_flatmate_by_discord_id(self, discord_id):
        """Get a flatmate by Discord ID."""
        logger.debug(f"Looking for flatmate with Discord ID: {discord_id}")
        for flatmate in self.get_flatmates():
            if flatmate["discord_id"] == discord_id:
                logger.debug(f"Found flatmate: {flatmate['name']} by Discord ID: {discord_id}")
                return flatmate
        logger.debug(f"Flatmate not found with Discord ID: {discord_id}")
        return None

    def add_flatmate(self, name, discord_id):
        """Add a new flatmate."""
        logger.info(f"Adding new flatmate: {name} with Discord ID: {discord_id}")

        # Check if flatmate with name already exists
        if self.get_flatmate_by_name(name):
            logger.warning(f"Attempted to add flatmate with duplicate name: {name}")
            return False, "Flatmate with this name already exists"

        # Check if flatmate with Discord ID already exists
        if self.get_flatmate_by_discord_id(discord_id):
            logger.warning(f"Attempted to add flatmate with duplicate Discord ID: {discord_id}")
            return False, "Flatmate with this Discord ID already exists"

        # Add the flatmate
        new_flatmate = {
            "name": name,
            "discord_id": discord_id,
            "on_vacation": False,
            "stats": {
                "completed": 0,
                "reassigned": 0,
                "skipped": 0
            }
        }

        self.config["flatmates"].append(new_flatmate)
        self.save_config()
        logger.info(f"Flatmate added successfully: {name} (ID: {discord_id})")
        return True, "Flatmate added successfully"

    def remove_flatmate(self, name):
        """Remove a flatmate by name."""
        logger.info(f"Removing flatmate: {name}")
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            logger.warning(f"Attempted to remove non-existent flatmate: {name}")
            return False, "Flatmate not found"

        self.config["flatmates"].remove(flatmate)
        self.save_config()
        logger.info(f"Flatmate removed successfully: {name}")
        return True, "Flatmate removed successfully"

    def set_flatmate_vacation(self, name, status):
        """Set the vacation status of a flatmate."""
        logger.info(f"Setting vacation status for {name} to {status}")
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            logger.warning(f"Attempted to set vacation status for non-existent flatmate: {name}")
            return False, "Flatmate not found"

        flatmate["on_vacation"] = status
        self.save_config()
        logger.info(f"Vacation status updated for {name}: {status}")
        return True, f"Vacation status for {name} set to {status}"

    def update_flatmate_stats(self, name, stat_type, increment=1):
        """Update statistics for a flatmate."""
        logger.info(f"Updating stats for {name}: {stat_type} +{increment}")
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            logger.warning(f"Attempted to update stats for non-existent flatmate: {name}")
            return False, "Flatmate not found"

        # Initialize stats if not present
        if "stats" not in flatmate:
            logger.debug(f"Initializing stats for {name}")
            flatmate["stats"] = {
                "completed": 0,
                "reassigned": 0,
                "skipped": 0
            }

        # Update the specified stat
        if stat_type in flatmate["stats"]:
            prev_value = flatmate["stats"][stat_type]
            flatmate["stats"][stat_type] += increment
            new_value = flatmate["stats"][stat_type]
            logger.info(f"Stats updated for {name}: {stat_type} {prev_value} -> {new_value}")
            self.save_config()
            return True, f"Statistics updated for {name}"
        else:
            logger.warning(f"Attempted to update unknown stat type: {stat_type}")
            return False, f"Unknown statistic type: {stat_type}"

    def get_flatmate_stats(self, name):
        """Get statistics for a flatmate."""
        logger.debug(f"Getting stats for flatmate: {name}")
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            logger.warning(f"Attempted to get stats for non-existent flatmate: {name}")
            return None

        # Initialize stats if not present
        if "stats" not in flatmate:
            logger.debug(f"Initializing stats for {name}")
            flatmate["stats"] = {
                "completed": 0,
                "reassigned": 0,
                "skipped": 0
            }
            self.save_config()

        logger.debug(f"Stats for {name}: {flatmate['stats']}")
        return flatmate["stats"]

    def add_chore(self, chore_name):
        """Add a new chore."""
        logger.info(f"Adding new chore: {chore_name}")
        chores = self.get_chores()
        if chore_name in chores:
            logger.warning(f"Attempted to add duplicate chore: {chore_name}")
            return False, "Chore already exists"

        # Add the chore to the list
        chores.append(chore_name)
        self.config["chores"] = chores

        self.save_config()
        logger.info(f"Chore added successfully: {chore_name}")
        return True, "Chore added successfully"

    def get_posting_schedule(self):
        """Get the posting day and time."""
        logger.debug("Getting posting schedule")
        schedule = {
            "day": self.config.get("posting_day", "Monday"),
            "time": self.config.get("posting_time", "9:00"),
            "timezone": self.config.get("timezone", "UTC")
        }
        logger.debug(f"Posting schedule: {schedule}")
        return schedule

    def get_reminder_settings(self):
        """Get reminder settings."""
        logger.debug("Getting reminder settings")
        if "reminders" not in self.config:
            logger.debug("Reminder settings not found, initializing with defaults")
            self.config["reminders"] = {
                "enabled": True,
                "day": "Friday",
                "time": "11:00"
            }
            self.save_config()

        logger.debug(f"Reminder settings: {self.config['reminders']}")
        return self.config["reminders"]

    def update_reminder_settings(self, enabled=None, day=None, time=None):
        """Update reminder settings."""
        logger.info(f"Updating reminder settings: enabled={enabled}, day={day}, time={time}")
        if "reminders" not in self.config:
            logger.debug("Reminder settings not found, initializing with defaults")
            self.config["reminders"] = {
                "enabled": True,
                "day": "Friday",
                "time": "11:00"
            }

        # Update values if provided
        if enabled is not None:
            old_enabled = self.config["reminders"].get("enabled", True)
            self.config["reminders"]["enabled"] = enabled
            logger.info(f"Updated reminder enabled: {old_enabled} -> {enabled}")

        if day is not None:
            old_day = self.config["reminders"].get("day", "Friday")
            self.config["reminders"]["day"] = day
            logger.info(f"Updated reminder day: {old_day} -> {day}")

        if time is not None:
            old_time = self.config["reminders"].get("time", "11:00")
            self.config["reminders"]["time"] = time
            logger.info(f"Updated reminder time: {old_time} -> {time}")

        self.save_config()
        logger.info("Reminder settings updated successfully")
        return True, "Reminder settings updated"

    def get_emoji(self):
        """Get the emoji configuration."""
        logger.debug("Getting emoji configuration")
        default_emoji = {
            "completed": "✅",
            "unavailable": "❌"
        }

        emoji_config = self.config.get("emoji", default_emoji)
        logger.debug(f"Emoji configuration: {emoji_config}")
        return emoji_config

    def get_schedule_data_file(self):
        """Get the path to the schedule data file."""
        logger.debug("Getting schedule data file path")
        data_file = self.config.get("schedule_data_file", "data/schedule_data.json")
        logger.debug(f"Schedule data file: {data_file}")
        return data_file

    def get_chores(self):
        """Get the list of chore names."""
        logger.debug("Getting list of chores")
        chores_data = self.config.get("chores", [])

        # Handle both old and new format
        if chores_data and isinstance(chores_data[0], dict):
            # New format
            chore_names = [chore["name"] for chore in chores_data]
            logger.debug(f"Found {len(chore_names)} chores (new format)")
            return chore_names
        else:
            # Old format - strings
            logger.debug(f"Found {len(chores_data)} chores (old format)")
            return chores_data

    def get_chores_data(self):
        """Get the full chore data including frequency."""
        logger.debug("Getting full chore data")
        chores_data = self.config.get("chores", [])

        # Handle old format
        if chores_data and not isinstance(chores_data[0], dict):
            # Convert old format to new format
            logger.debug("Converting chores from old to new format")
            chores_data = [{"name": chore, "frequency": 1} for chore in chores_data]
            self.config["chores"] = chores_data
            self.save_config()

        logger.debug(f"Found {len(chores_data)} chores with frequency data")
        return chores_data

    def get_chore_by_name(self, name):
        """Get a chore by name."""
        logger.debug(f"Looking for chore with name: {name}")
        chores_data = self.get_chores_data()

        for chore in chores_data:
            if chore["name"].lower() == name.lower():
                logger.debug(f"Found chore: {chore}")
                return chore

        logger.debug(f"Chore not found with name: {name}")
        return None

    def get_chore_frequency(self, name):
        """Get the frequency of a chore."""
        chore = self.get_chore_by_name(name)
        if chore:
            frequency = chore.get("frequency", 1)
            logger.debug(f"Frequency for chore '{name}': {frequency}")
            return frequency

        logger.debug(f"Frequency not found for chore: {name}")
        return 1  # Default to weekly

    def set_chore_frequency(self, name, frequency):
        """Set the frequency of a chore."""
        logger.info(f"Setting frequency for chore '{name}' to {frequency}")

        chores_data = self.get_chores_data()

        # Find the chore
        for chore in chores_data:
            if chore["name"].lower() == name.lower():
                chore["frequency"] = frequency
                self.config["chores"] = chores_data
                self.save_config()
                logger.info(f"Frequency for chore '{name}' set to {frequency}")
                return True, f"Frequency for '{name}' set to {frequency}"

        logger.warning(f"Attempted to set frequency for non-existent chore: {name}")
        return False, "Chore not found"

    def add_chore(self, chore_name, frequency=1):
        """Add a new chore with frequency."""
        logger.info(f"Adding new chore: {chore_name} with frequency: {frequency}")

        # Get existing chores
        chores_data = self.get_chores_data()

        # Check if chore already exists
        for chore in chores_data:
            if chore["name"].lower() == chore_name.lower():
                logger.warning(f"Attempted to add duplicate chore: {chore_name}")
                return False, "Chore already exists"

        # Add the new chore
        new_chore = {
            "name": chore_name,
            "frequency": frequency
        }

        chores_data.append(new_chore)
        self.config["chores"] = chores_data

        self.save_config()
        logger.info(f"Chore added successfully: {chore_name} (frequency: {frequency})")
        return True, "Chore added successfully"

    def remove_chore(self, chore_name):
        """Remove a chore."""
        logger.info(f"Removing chore: {chore_name}")

        chores_data = self.get_chores_data()

        # Find the chore
        for i, chore in enumerate(chores_data):
            if isinstance(chore, dict) and chore["name"].lower() == chore_name.lower():
                del chores_data[i]
                self.config["chores"] = chores_data
                self.save_config()
                logger.info(f"Chore removed successfully: {chore_name}")
                return True, "Chore removed successfully"
            elif isinstance(chore, str) and chore.lower() == chore_name.lower():
                del chores_data[i]
                self.config["chores"] = chores_data
                self.save_config()
                logger.info(f"Chore removed successfully: {chore_name}")
                return True, "Chore removed successfully"

        logger.warning(f"Attempted to remove non-existent chore: {chore_name}")
        return False, "Chore not found"