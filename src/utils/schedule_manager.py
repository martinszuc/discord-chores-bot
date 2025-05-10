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
                    "voted_flatmates": [],  # Track flatmates who have already voted
                    "pending_chores": [],  # Track chores that haven't been completed
                    "excluded_for_next_rotation": []  # Track flatmates to exclude from the next rotation
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
                "voted_flatmates": [],
                "pending_chores": [],
                "excluded_for_next_rotation": []
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
        # Initialize pending chores with all chores
        self.schedule_data["pending_chores"] = list(self.schedule_data.get("current_assignments", {}).keys())
        self._save_schedule_data()

    def get_current_assignments(self):
        """Get the current chore assignments."""
        return self.schedule_data.get("current_assignments", {})

    def get_pending_chores(self):
        """Get the list of chores that haven't been completed yet."""
        return self.schedule_data.get("pending_chores", [])

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

    def get_excluded_for_next_rotation(self):
        """Get the list of flatmates excluded from the next rotation."""
        if "excluded_for_next_rotation" not in self.schedule_data:
            self.schedule_data["excluded_for_next_rotation"] = []
        return self.schedule_data["excluded_for_next_rotation"]

    def exclude_from_next_rotation(self, flatmate_name):
        """Exclude a flatmate from the next rotation."""
        if "excluded_for_next_rotation" not in self.schedule_data:
            self.schedule_data["excluded_for_next_rotation"] = []

        if flatmate_name not in self.schedule_data["excluded_for_next_rotation"]:
            self.schedule_data["excluded_for_next_rotation"].append(flatmate_name)
            self._save_schedule_data()
            return True
        return False

    def include_in_next_rotation(self, flatmate_name):
        """Include a previously excluded flatmate in the next rotation."""
        if "excluded_for_next_rotation" not in self.schedule_data:
            return False

        if flatmate_name in self.schedule_data["excluded_for_next_rotation"]:
            self.schedule_data["excluded_for_next_rotation"].remove(flatmate_name)
            self._save_schedule_data()
            return True
        return False

    def clear_next_rotation_exclusions(self):
        """Clear all exclusions for the next rotation."""
        self.schedule_data["excluded_for_next_rotation"] = []
        self._save_schedule_data()
        return True

    def calculate_priority_score(self, flatmate):
        """Calculate a priority score for a flatmate based on their stats.
        Lower score means higher priority to be assigned a chore.
        """
        stats = self.config_manager.get_flatmate_stats(flatmate["name"])
        if not stats:
            return 0

        # Calculate score - give higher priority to those who complete chores
        # and lower priority to those who skip or get reassigned
        score = stats["skipped"] * 2 + stats["reassigned"] - stats["completed"] * 0.5

        # If flatmate recently returned from vacation, give them higher priority
        if flatmate.get("recently_returned", False):
            score -= 5

        return score

    def generate_new_schedule(self):
        """Generate a new chore schedule using the priority system and difficulty balancing."""
        # Get active flatmates (not on vacation)
        all_active_flatmates = self.config_manager.get_active_flatmates()

        # Filter out flatmates excluded for the next rotation
        excluded_flatmates = self.get_excluded_for_next_rotation()
        flatmates = [f for f in all_active_flatmates if f["name"] not in excluded_flatmates]

        # Get list of chores
        chores = self.config_manager.get_chores()

        if not flatmates or not chores:
            logger.warning("Cannot generate schedule: No flatmates or no chores defined")
            return {}

        # Reset 'recently_returned' flag for all flatmates
        for flatmate in self.config_manager.get_flatmates():
            if flatmate.get("recently_returned", False):
                flatmate["recently_returned"] = False

        self.config_manager.save_config()

        # Sort chores by difficulty (highest first)
        sorted_chores = sorted(
            chores,
            key=lambda c: self.config_manager.get_chore_details(c).get("difficulty", 1),
            reverse=True
        )

        # Calculate priority scores for flatmates
        flatmates_with_scores = [
            (f, self.calculate_priority_score(f)) for f in flatmates
        ]

        # Sort flatmates by priority score (lowest first = highest priority)
        sorted_flatmates = [f for f, _ in sorted(
            flatmates_with_scores,
            key=lambda item: item[1]
        )]

        # Assign chores, starting with the most difficult chores
        new_assignments = {}
        flatmate_difficulty_sum = {f["name"]: 0 for f in flatmates}

        for chore in sorted_chores:
            # Get difficulty of this chore
            chore_difficulty = self.config_manager.get_chore_details(chore).get("difficulty", 1)

            # Find flatmate with lowest total difficulty so far
            sorted_by_load = sorted(
                sorted_flatmates,
                key=lambda f: flatmate_difficulty_sum[f["name"]]
            )

            # Assign to flatmate with lowest load
            assigned_flatmate = sorted_by_load[0]
            new_assignments[chore] = assigned_flatmate["name"]

            # Update their total difficulty
            flatmate_difficulty_sum[assigned_flatmate["name"]] += chore_difficulty

        # Save new assignments
        self.schedule_data["current_assignments"] = new_assignments
        # Reset voted flatmates list for the new schedule
        self.schedule_data["voted_flatmates"] = []
        # Initialize pending chores with all chores
        self.schedule_data["pending_chores"] = list(new_assignments.keys())
        # Clear exclusions after generating the schedule
        self.clear_next_rotation_exclusions()

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
        flatmates = self.config_manager.get_active_flatmates()
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

        # Eligible flatmates: not the current assignee, not on vacation, and hasn't voted yet
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

        # Update statistics for the original flatmate
        self.config_manager.update_flatmate_stats(excluding_flatmate, "skipped")

        # Randomly select a flatmate
        next_flatmate = random.choice(eligible_flatmates)

        # Update assignment
        self.schedule_data["current_assignments"][chore] = next_flatmate["name"]

        # Mark the new flatmate as having "voted" (been assigned a task)
        self.add_voted_flatmate(next_flatmate["name"])

        # Update statistics for the new flatmate
        self.config_manager.update_flatmate_stats(next_flatmate["name"], "reassigned")

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

        # Remove from pending chores
        if "pending_chores" not in self.schedule_data:
            self.schedule_data["pending_chores"] = []

        if chore in self.schedule_data["pending_chores"]:
            self.schedule_data["pending_chores"].remove(chore)

        # Mark flatmate as having voted
        self.add_voted_flatmate(flatmate_name)

        # Update statistics
        self.config_manager.update_flatmate_stats(flatmate_name, "completed")

        self._save_schedule_data()

        return True, f"Chore '{chore}' marked as completed by {flatmate_name}"

    def reset_schedule(self):
        """Reset the schedule data."""
        self.schedule_data = {
            "last_posted": None,
            "current_assignments": {},
            "rotation_indices": {},
            "voted_flatmates": [],
            "pending_chores": [],
            "excluded_for_next_rotation": []
        }
        self._save_schedule_data()
        return True, "Schedule has been reset"