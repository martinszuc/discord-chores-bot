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

    def get_active_flatmates(self):
        """Get the list of flatmates who are not on vacation."""
        return [f for f in self.get_flatmates() if not f.get("on_vacation", False)]

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
            "discord_id": discord_id,
            "on_vacation": False,
            "stats": {
                "completed": 0,
                "reassigned": 0,
                "skipped": 0
            }
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

    def set_flatmate_vacation(self, name, status):
        """Set the vacation status of a flatmate."""
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            return False, "Flatmate not found"

        flatmate["on_vacation"] = status
        self.save_config()
        return True, f"Vacation status for {name} set to {status}"

    def update_flatmate_stats(self, name, stat_type, increment=1):
        """Update statistics for a flatmate."""
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            return False, "Flatmate not found"

        if "stats" not in flatmate:
            flatmate["stats"] = {
                "completed": 0,
                "reassigned": 0,
                "skipped": 0
            }

        if stat_type in flatmate["stats"]:
            flatmate["stats"][stat_type] += increment
            self.save_config()
            return True, f"Statistics updated for {name}"
        else:
            return False, f"Unknown statistic type: {stat_type}"

    def get_flatmate_stats(self, name):
        """Get statistics for a flatmate."""
        flatmate = self.get_flatmate_by_name(name)
        if not flatmate:
            return None

        if "stats" not in flatmate:
            flatmate["stats"] = {
                "completed": 0,
                "reassigned": 0,
                "skipped": 0
            }
            self.save_config()

        return flatmate["stats"]

    def get_chores(self):
        """Get the list of chores."""
        return self.config.get("chores", [])

    def get_chore_details(self, chore_name):
        """Get details of a specific chore."""
        chores_with_details = self.config.get("chores_details", {})
        if chore_name in chores_with_details:
            return chores_with_details[chore_name]
        return {"difficulty": 1}  # Default difficulty

    def add_chore(self, chore_name, difficulty=1):
        """Add a new chore."""
        chores = self.get_chores()
        if chore_name in chores:
            return False, "Chore already exists"

        chores.append(chore_name)
        self.config["chores"] = chores

        # Initialize chore details
        if "chores_details" not in self.config:
            self.config["chores_details"] = {}

        self.config["chores_details"][chore_name] = {
            "difficulty": difficulty
        }

        self.save_config()
        return True, "Chore added successfully"

    def remove_chore(self, chore_name):
        """Remove a chore."""
        chores = self.get_chores()
        if chore_name not in chores:
            return False, "Chore not found"

        chores.remove(chore_name)
        self.config["chores"] = chores

        # Remove from details if exists
        if "chores_details" in self.config and chore_name in self.config["chores_details"]:
            del self.config["chores_details"][chore_name]

        self.save_config()
        return True, "Chore removed successfully"

    def set_chore_difficulty(self, chore_name, difficulty):
        """Set the difficulty level for a chore."""
        if chore_name not in self.get_chores():
            return False, "Chore not found"

        # Initialize chores_details if not exists
        if "chores_details" not in self.config:
            self.config["chores_details"] = {}

        # Initialize chore details if not exists
        if chore_name not in self.config["chores_details"]:
            self.config["chores_details"][chore_name] = {}

        self.config["chores_details"][chore_name]["difficulty"] = difficulty
        self.save_config()
        return True, f"Difficulty for {chore_name} set to {difficulty}"

    def get_posting_schedule(self):
        """Get the posting day and time."""
        return {
            "day": self.config.get("posting_day", "Monday"),
            "time": self.config.get("posting_time", "9:00"),
            "timezone": self.config.get("timezone", "UTC")
        }

    def get_reminder_settings(self):
        """Get reminder settings."""
        if "reminders" not in self.config:
            self.config["reminders"] = {
                "enabled": True,
                "day": "Friday",
                "time": "18:00"
            }
            self.save_config()

        return self.config["reminders"]

    def update_reminder_settings(self, enabled=None, day=None, time=None):
        """Update reminder settings."""
        if "reminders" not in self.config:
            self.config["reminders"] = {
                "enabled": True,
                "day": "Friday",
                "time": "18:00"
            }

        if enabled is not None:
            self.config["reminders"]["enabled"] = enabled

        if day is not None:
            self.config["reminders"]["day"] = day

        if time is not None:
            self.config["reminders"]["time"] = time

        self.save_config()
        return True, "Reminder settings updated"

    def get_emoji(self):
        """Get the emoji configuration."""
        return self.config.get("emoji", {
            "completed": "✅",
            "unavailable": "❌",
            "difficulty_1": "1️⃣",
            "difficulty_2": "2️⃣",
            "difficulty_3": "3️⃣",
            "difficulty_4": "4️⃣",
            "difficulty_5": "5️⃣"
        })

    def get_schedule_data_file(self):
        """Get the path to the schedule data file."""
        return self.config.get("schedule_data_file", "data/schedule_data.json")