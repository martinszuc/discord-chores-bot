import json
import logging

logger = logging.getLogger('chores-bot')


class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from the config file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def save_config(self):
        """Save the current configuration to the config file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Config saved successfully")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def get_token(self):
        """Get the Discord bot token."""
        return self.config.get("token")

    def get_prefix(self):
        """Get the command prefix."""
        return self.config.get("prefix", "!")

    def get_chores_channel_id(self):
        """Get the ID of the chores channel."""
        return self.config.get("chores_channel_id")

    def get_admin_role_id(self):
        """Get the ID of the admin role."""
        return self.config.get("admin_role_id")

    def get_flatmates(self):
        """Get the list of flatmates."""
        return self.config.get("flatmates", [])

    def get_flatmate_by_name(self, name):
        """Get a flatmate by name."""
        for flatmate in self.get_flatmates():
            if flatmate["name"].lower() == name.lower():
                return flatmate
        return None

    def get_flatmate_by_discord_id(self, discord_id):
        """Get a flatmate by Discord ID."""
        for flatmate in self.get_flatmates():
            if flatmate["discord_id"] == discord_id:
                return flatmate
        return None

    def add_flatmate(self, name, discord_id):
        """Add a new flatmate."""
        if self.get_flatmate_by_name(name):
            return False, "Flatmate with this name already exists"

        if self.get_flatmate_by_discord_id(discord_id):
            return False, "Flatmate with this Discord ID already exists"

        self.config["flatmates"].append({
            "name": name,
            "discord_id": discord_id
        })
        self.save_config()
        return True, "Flatmate added successfully"

    def remove_flatmate(self, name):
        """Remove a flatmate by name."""
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            return False, "Flatmate not found"

        self.config["flatmates"].remove(flatmate)
        self.save_config()
        return True, "Flatmate removed successfully"

    def get_chores(self):
        """Get the list of chores."""
        return self.config.get("chores", [])

    def add_chore(self, chore_name):
        """Add a new chore."""
        if chore_name in self.get_chores():
            return False, "Chore already exists"

        self.config["chores"].append(chore_name)
        self.save_config()
        return True, "Chore added successfully"

    def remove_chore(self, chore_name):
        """Remove a chore."""
        if chore_name not in self.get_chores():
            return False, "Chore not found"

        self.config["chores"].remove(chore_name)
        self.save_config()
        return True, "Chore removed successfully"

    def get_posting_schedule(self):
        """Get the posting day and time."""
        return {
            "day": self.config.get("posting_day", "Monday"),
            "time": self.config.get("posting_time", "9:00"),
            "timezone": self.config.get("timezone", "UTC")
        }

    def get_emoji(self):
        """Get the emoji configuration."""
        return self.config.get("emoji", {
            "completed": "✅",
            "unavailable": "❌"
        })

    def get_schedule_data_file(self):
        """Get the path to the schedule data file."""
        return self.config.get("schedule_data_file", "data/schedule_data.json")