import json
import logging
import os
import datetime
import random
from pathlib import Path

logger = logging.getLogger('chores-bot')


class ScheduleManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.data_file = self.config_manager.get_schedule_data_file()
        self.schedule_data = self._load_schedule_data()

    def _load_schedule_data(self):
        """Load schedule data from the data file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Initialize with empty data
                default_data = {
                    "last_posted": None,
                    "current_assignments": {},
                    "rotation_indices": {},
                    "voted_flatmates": []  # Track flatmates who have already voted
                }
                self._save_schedule_data(default_data)
                return default_data
        except Exception as e:
            logger.error(f"Failed to load schedule data: {e}")
            # Initialize with empty data on error
            return {
                "last_posted": None,
                "current_assignments": {},
                "rotation_indices": {},
                "voted_flatmates": []
            }

    def _save_schedule_data(self, data=None):
        """Save schedule data to the data file."""
        try:
            # Create parent directory if it doesn't exist
            Path(os.path.dirname(self.data_file)).mkdir(parents=True, exist_ok=True)

            # Save data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data or self.schedule_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Schedule data saved to {self.data_file}")
        except Exception as e:
            logger.error(f"Failed to save schedule data: {e}")
            raise

    def get_last_posted_date(self):
        """Get the date when the schedule was last posted."""
        return self.schedule_data.get("last_posted")

    def update_last_posted_date(self):
        """Update the last posted date to now."""
        self.schedule_data["last_posted"] = datetime.datetime.now().isoformat()
        # Reset voted flatmates when posting a new schedule
        self.schedule_data["voted_flatmates"] = []
        self._save_schedule_data()

    def get_current_assignments(self):
        """Get the current chore assignments."""
        return self.schedule_data.get("current_assignments", {})

    def get_assignment_for_chore(self, chore):
        """Get the flatmate assigned to a specific chore."""
        return self.schedule_data.get("current_assignments", {}).get(chore)

    def get_rotation_index(self, chore):
        """Get the current rotation index for a chore."""
        return self.schedule_data.get("rotation_indices", {}).get(chore, 0)

    def add_voted_flatmate(self, flatmate_name):
        """Mark a flatmate as having voted (used a reaction)."""
        if "voted_flatmates" not in self.schedule_data:
            self.schedule_data["voted_flatmates"] = []

        if flatmate_name not in self.schedule_data["voted_flatmates"]:
            self.schedule_data["voted_flatmates"].append(flatmate_name)
            self._save_schedule_data()

    def get_voted_flatmates(self):
        """Get list of flatmates who have already voted."""
        return self.schedule_data.get("voted_flatmates", [])

    def generate_new_schedule(self):
        """Generate a new chore schedule."""
        flatmates = self.config_manager.get_flatmates()
        chores = self.config_manager.get_chores()

        if not flatmates or not chores:
            logger.warning("Cannot generate schedule: No flatmates or no chores defined")
            return {}

        new_assignments = {}
        for chore in chores:
            # Get or initialize rotation index for this chore
            if "rotation_indices" not in self.schedule_data:
                self.schedule_data["rotation_indices"] = {}

            rotation_idx = self.get_rotation_index(chore)

            # Assign chore to flatmate based on rotation index
            assigned_flatmate = flatmates[rotation_idx % len(flatmates)]
            new_assignments[chore] = assigned_flatmate["name"]

            # Update rotation index for next time
            self.schedule_data["rotation_indices"][chore] = (rotation_idx + 1) % len(flatmates)

        # Save new assignments
        self.schedule_data["current_assignments"] = new_assignments
        # Reset voted flatmates list for the new schedule
        self.schedule_data["voted_flatmates"] = []
        self._save_schedule_data()

        return new_assignments

    def randomly_reassign_chore(self, chore, excluding_flatmate):
        """
        Randomly reassign a chore to a flatmate who hasn't voted this week,
        excluding the original flatmate.

        Args:
            chore (str): The chore to reassign
            excluding_flatmate (str): Name of the flatmate to exclude from reassignment

        Returns:
            str or None: Name of the flatmate the chore was reassigned to, or None if reassignment failed
        """
        flatmates = self.config_manager.get_flatmates()
        if not flatmates:
            logger.warning("Cannot reassign: No flatmates defined")
            return None

        # Get current assignment
        current_assignment = self.get_assignment_for_chore(chore)
        if not current_assignment:
            logger.warning(f"No current assignment for chore: {chore}")
            return None

        # Get flatmates who haven't voted this week
        voted_flatmates = self.get_voted_flatmates()

        # Eligible flatmates: not the current assignee and hasn't voted yet
        eligible_flatmates = [
            f for f in flatmates
            if f["name"] != excluding_flatmate and f["name"] not in voted_flatmates
        ]

        # If no eligible flatmates who haven't voted, fall back to anyone except the current assignee
        if not eligible_flatmates:
            logger.warning("No eligible flatmates who haven't voted yet, falling back to any available flatmate")
            eligible_flatmates = [f for f in flatmates if f["name"] != excluding_flatmate]

        if not eligible_flatmates:
            logger.warning("No eligible flatmates for reassignment")
            return None

        # Randomly select a flatmate
        next_flatmate = random.choice(eligible_flatmates)

        # Update assignment
        self.schedule_data["current_assignments"][chore] = next_flatmate["name"]

        # Mark the new flatmate as having "voted" (been assigned a task)
        self.add_voted_flatmate(next_flatmate["name"])

        self._save_schedule_data()

        return next_flatmate["name"]

    def rotate_assignment(self, chore):
        """Rotate the assignment for a specific chore to the next flatmate."""
        flatmates = self.config_manager.get_flatmates()
        if not flatmates:
            logger.warning("Cannot rotate assignment: No flatmates defined")
            return None

        # Get current assignment
        current_assignment = self.get_assignment_for_chore(chore)
        if not current_assignment:
            logger.warning(f"No current assignment for chore: {chore}")
            return None

        # Find current flatmate index
        current_idx = -1
        for i, flatmate in enumerate(flatmates):
            if flatmate["name"] == current_assignment:
                current_idx = i
                break

        if current_idx == -1:
            logger.warning(f"Current assigned flatmate not found: {current_assignment}")
            return None

        # Find next flatmate
        next_idx = (current_idx + 1) % len(flatmates)
        next_flatmate = flatmates[next_idx]

        # Update assignment
        self.schedule_data["current_assignments"][chore] = next_flatmate["name"]
        self._save_schedule_data()

        return next_flatmate["name"]

    def mark_chore_completed(self, chore, flatmate_name):
        """Mark a chore as completed by a flatmate."""
        # Check if the chore exists and is assigned to the flatmate
        current_assignment = self.get_assignment_for_chore(chore)
        if not current_assignment:
            return False, f"No assignment found for chore: {chore}"

        if current_assignment != flatmate_name:
            return False, f"Chore is assigned to {current_assignment}, not {flatmate_name}"

        # Mark flatmate as having voted
        self.add_voted_flatmate(flatmate_name)

        # Record completion (could be expanded to track completion history)
        # For now, we'll just return success
        return True, f"Chore '{chore}' marked as completed by {flatmate_name}"

    def reset_schedule(self):
        """Reset the schedule data."""
        self.schedule_data = {
            "last_posted": None,
            "current_assignments": {},
            "rotation_indices": {},
            "voted_flatmates": []
        }
        self._save_schedule_data()
        return True, "Schedule has been reset"