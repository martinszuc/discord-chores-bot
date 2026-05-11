import datetime
import json
import logging
import os
import random
from pathlib import Path

import discord

from src.utils.strings import BotStrings

logger = logging.getLogger('chores-bot')


class ScheduleManager:
    def __init__(self, config_manager):
        logger.info("Initializing ScheduleManager")
        self.config_manager = config_manager
        self.data_file = self.config_manager.get_schedule_data_file()
        logger.debug(f"Schedule data file: {self.data_file}")
        self.schedule_data = self._load_schedule_data()
        logger.debug("ScheduleManager initialized successfully")

    def _load_schedule_data(self):
        """Load schedule data from the data file."""
        logger.info(f"Loading schedule data from: {self.data_file}")
        try:
            if os.path.exists(self.data_file):
                logger.debug("Schedule data file exists, loading data")
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(
                        f"Schedule data loaded successfully. Current assignments: {len(data.get('current_assignments', {}))}")
                    return data
            else:
                logger.info(f"Schedule data file not found, creating new file with default data: {self.data_file}")
                default_data = self._initialize_default_data()
                self._save_schedule_data(default_data)
                return default_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schedule data file: {e}")
            return self._initialize_default_data()
        except Exception as e:
            logger.error(f"Failed to load schedule data: {e}", exc_info=True)
            return self._initialize_default_data()

    def _initialize_default_data(self):
        """Initialize default schedule data."""
        logger.info("Initializing default schedule data")
        default_data = {
            "last_posted": None,
            "current_assignments": {},
            "previous_assignments": {},
            "rotation_indices": {},
            "voted_flatmates": [],
            "pending_chores": [],
            "excluded_for_next_rotation": [],
            "last_rotation_week": {},
            "completed_by": {}
        }
        return default_data

    def _save_schedule_data(self, data=None):
        """Save schedule data to the data file."""
        logger.info(f"Saving schedule data to: {self.data_file}")
        try:
            Path(os.path.dirname(self.data_file)).mkdir(parents=True, exist_ok=True)

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data or self.schedule_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Schedule data saved successfully to {self.data_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save schedule data: {e}", exc_info=True)
            raise

    def get_last_posted_date(self):
        """Get the date when the schedule was last posted."""
        logger.debug("Getting last posted date")
        last_posted = self.schedule_data.get("last_posted")
        logger.debug(f"Last posted date: {last_posted}")
        return last_posted

    def update_last_posted_date(self):
        """Update the last posted date to now."""
        logger.info("Updating last posted date to current time")
        now = datetime.datetime.now().isoformat()
        self.schedule_data["last_posted"] = now

        old_voted = self.schedule_data.get("voted_flatmates", [])
        self.schedule_data["voted_flatmates"] = []
        logger.debug(f"Reset voted flatmates: {old_voted} -> []")

        assignments = self.schedule_data.get("current_assignments", {})
        self.schedule_data["pending_chores"] = list(assignments.keys())
        logger.debug(f"Set pending chores: {self.schedule_data['pending_chores']}")

        self._save_schedule_data()
        logger.info(f"Last posted date updated to: {now}")

    def get_current_assignments(self):
        """Get the current chore assignments."""
        logger.debug("Getting current chore assignments")
        assignments = self.schedule_data.get("current_assignments", {})
        logger.debug(f"Current assignments: {assignments}")
        return assignments

    def get_previous_assignments(self):
        """Get the previous week's chore assignments."""
        logger.debug("Getting previous chore assignments")
        assignments = self.schedule_data.get("previous_assignments", {})
        logger.debug(f"Previous assignments: {assignments}")
        return assignments

    def get_pending_chores(self):
        """Get the list of chores that haven't been completed yet."""
        logger.debug("Getting pending chores")
        pending = self.schedule_data.get("pending_chores", [])
        logger.debug(f"Pending chores: {pending}")
        return pending

    def get_assignment_for_chore(self, chore):
        """Get the flatmate assigned to a specific chore."""
        logger.debug(f"Getting assignment for chore: {chore}")
        assigned_flatmate = self.schedule_data.get("current_assignments", {}).get(chore)
        logger.debug(f"Chore '{chore}' is assigned to: {assigned_flatmate}")
        return assigned_flatmate

    def get_rotation_index(self, chore):
        """Get the current rotation index for a chore."""
        logger.debug(f"Getting rotation index for chore: {chore}")
        index = self.schedule_data.get("rotation_indices", {}).get(chore, 0)
        logger.debug(f"Rotation index for '{chore}': {index}")
        return index

    def add_voted_flatmate(self, flatmate_name):
        """Mark a flatmate as having voted (used a reaction)."""
        logger.info(f"Adding flatmate to voted list: {flatmate_name}")
        if "voted_flatmates" not in self.schedule_data:
            logger.debug("Initializing voted_flatmates list")
            self.schedule_data["voted_flatmates"] = []

        if flatmate_name not in self.schedule_data["voted_flatmates"]:
            logger.debug(f"Adding {flatmate_name} to voted flatmates list")
            self.schedule_data["voted_flatmates"].append(flatmate_name)
            self._save_schedule_data()
            logger.info(f"Flatmate {flatmate_name} added to voted list")
        else:
            logger.debug(f"Flatmate {flatmate_name} already in voted list")

    def get_voted_flatmates(self):
        """Get list of flatmates who have already voted."""
        logger.debug("Getting list of voted flatmates")
        voted = self.schedule_data.get("voted_flatmates", [])
        logger.debug(f"Voted flatmates: {voted}")
        return voted

    def get_excluded_for_next_rotation(self):
        """Get the list of flatmates excluded from the next rotation."""
        logger.debug("Getting flatmates excluded from next rotation")
        if "excluded_for_next_rotation" not in self.schedule_data:
            logger.debug("excluded_for_next_rotation not found, initializing empty list")
            self.schedule_data["excluded_for_next_rotation"] = []

        excluded = self.schedule_data["excluded_for_next_rotation"]
        logger.debug(f"Excluded flatmates: {excluded}")
        return excluded

    def exclude_from_next_rotation(self, flatmate_name):
        """Exclude a flatmate from the next rotation."""
        logger.info(f"Excluding flatmate from next rotation: {flatmate_name}")
        if "excluded_for_next_rotation" not in self.schedule_data:
            logger.debug("excluded_for_next_rotation not found, initializing empty list")
            self.schedule_data["excluded_for_next_rotation"] = []

        if flatmate_name not in self.schedule_data["excluded_for_next_rotation"]:
            logger.debug(f"Adding {flatmate_name} to excluded list")
            self.schedule_data["excluded_for_next_rotation"].append(flatmate_name)
            self._save_schedule_data()
            logger.info(f"Flatmate {flatmate_name} excluded from next rotation")
            return True
        else:
            logger.debug(f"Flatmate {flatmate_name} already excluded from next rotation")
            return False

    def include_in_next_rotation(self, flatmate_name):
        """Include a previously excluded flatmate in the next rotation."""
        logger.info(f"Including flatmate in next rotation: {flatmate_name}")
        if "excluded_for_next_rotation" not in self.schedule_data:
            logger.debug("excluded_for_next_rotation not found, nothing to include")
            return False

        if flatmate_name in self.schedule_data["excluded_for_next_rotation"]:
            logger.debug(f"Removing {flatmate_name} from excluded list")
            self.schedule_data["excluded_for_next_rotation"].remove(flatmate_name)
            self._save_schedule_data()
            logger.info(f"Flatmate {flatmate_name} included in next rotation")
            return True
        else:
            logger.debug(f"Flatmate {flatmate_name} was not in excluded list")
            return False

    def clear_next_rotation_exclusions(self):
        """Clear all exclusions for the next rotation."""
        logger.info("Clearing all exclusions for next rotation")
        old_excluded = self.schedule_data.get("excluded_for_next_rotation", [])
        self.schedule_data["excluded_for_next_rotation"] = []
        self._save_schedule_data()
        logger.info(f"Cleared exclusions: {old_excluded}")
        return True

    def generate_new_schedule(self):
        """
        Generate a new chore schedule using simple rotation.
        Distributes chores across all flatmates each week.
        Each chore rotates to the next person in the list.
        """
        logger.info("Generating new chore schedule with simple rotation")

        # Store current assignments as previous
        current_assignments = self.get_current_assignments()
        if current_assignments:
            logger.debug(f"Storing current assignments as previous: {current_assignments}")
            self.schedule_data["previous_assignments"] = current_assignments.copy()

        previous_assignments = self.get_previous_assignments()
        logger.debug(f"Previous assignments: {previous_assignments}")

        # Get active flatmates (not on vacation, not excluded)
        all_active_flatmates = self.config_manager.get_active_flatmates()
        logger.debug(f"Found {len(all_active_flatmates)} active flatmates (not on vacation)")

        excluded_flatmates = self.get_excluded_for_next_rotation()
        logger.debug(f"Excluding flatmates from next rotation: {excluded_flatmates}")

        flatmates = [f for f in all_active_flatmates if f["name"] not in excluded_flatmates]
        logger.debug(f"Final list of {len(flatmates)} flatmates for schedule generation")

        if not flatmates:
            logger.warning("Cannot generate schedule: No flatmates available")
            return {}

        # Get current week for frequency checks
        current_week = datetime.datetime.now().isocalendar()[1]
        logger.debug(f"Current week number: {current_week}")

        # Determine which chores should appear this week based on frequency
        chores_data = self.config_manager.get_chores_data()
        logger.debug(f"Got {len(chores_data)} chores with frequency data")

        eligible_chores = []
        for chore in chores_data:
            chore_name = chore["name"]
            frequency = chore.get("frequency", 1)

            if "last_rotation_week" not in self.schedule_data:
                self.schedule_data["last_rotation_week"] = {}

            last_week = self.schedule_data["last_rotation_week"].get(chore_name, 0)

            if frequency == 1 or (current_week - last_week) % frequency == 0:
                eligible_chores.append(chore_name)
                self.schedule_data["last_rotation_week"][chore_name] = current_week

        logger.debug(f"Eligible chores for this week: {eligible_chores}")

        if not eligible_chores:
            logger.warning("Cannot generate schedule: No eligible chores for this week")
            return {}

        # Initialize rotation_indices if not present
        if "rotation_indices" not in self.schedule_data:
            self.schedule_data["rotation_indices"] = {}

        # For new chores, stagger the starting position
        for i, chore in enumerate(eligible_chores):
            if chore not in self.schedule_data["rotation_indices"]:
                # Stagger: first chore starts at 0, second at 1, etc.
                self.schedule_data["rotation_indices"][chore] = i % len(flatmates)
                logger.debug(f"Initializing rotation index for '{chore}' to {i % len(flatmates)}")

        new_assignments = {}

        # Track how many chores each flatmate has been assigned this week
        flatmate_chore_count = {f["name"]: 0 for f in flatmates}

        # Simple rotation: for each chore, assign to the next person in rotation
        # This ensures chores are distributed across flatmates each week
        for i, chore in enumerate(eligible_chores):
            # Get current rotation index for this chore
            rotation_index = self.schedule_data["rotation_indices"].get(chore, i % len(flatmates))

            # Ensure the rotation index is within bounds
            if rotation_index >= len(flatmates):
                rotation_index = rotation_index % len(flatmates)

            # Assign to the flatmate at this rotation index
            assigned_flatmate = flatmates[rotation_index]
            new_assignments[chore] = assigned_flatmate["name"]
            flatmate_chore_count[assigned_flatmate["name"]] += 1

            logger.info(f"Assigned '{chore}' to {assigned_flatmate['name']} (rotation index: {rotation_index})")

            # Increment rotation index for next week (with wraparound)
            self.schedule_data["rotation_indices"][chore] = (rotation_index + 1) % len(flatmates)

        logger.info(f"Final assignments: {new_assignments}")
        logger.debug(f"Chore distribution: {flatmate_chore_count}")

        self.schedule_data["current_assignments"] = new_assignments

        # Reset voted flatmates list
        logger.debug("Resetting voted flatmates list for new schedule")
        self.schedule_data["voted_flatmates"] = []

        # Set all chores as pending
        logger.debug(f"Setting pending chores to all {len(new_assignments)} chores")
        self.schedule_data["pending_chores"] = list(new_assignments.keys())

        # Initialize completed_by tracking
        logger.debug("Initializing completed_by tracking")
        self.schedule_data["completed_by"] = {chore: [] for chore in new_assignments.keys()}

        # Clear exclusions after generating schedule
        logger.debug("Clearing exclusions after generating schedule")
        self.clear_next_rotation_exclusions()

        # Clear recently_returned flags
        for flatmate in self.config_manager.get_flatmates():
            if flatmate.get("recently_returned", False):
                logger.debug(f"Resetting 'recently_returned' flag for {flatmate['name']}")
                flatmate["recently_returned"] = False

        self.config_manager.save_config()
        self._save_schedule_data()
        logger.info("New schedule generated and saved successfully")

        return new_assignments

    def randomly_reassign_chore(self, chore, excluding_flatmate):
        """
        Randomly reassign a chore to a flatmate who hasn't voted this week.
        Updates stats: skipped for original, reassigned for new assignee.
        """
        logger.info(f"Randomly reassigning chore '{chore}' from {excluding_flatmate}")

        flatmates = self.config_manager.get_active_flatmates()
        if not flatmates:
            logger.warning("Cannot reassign: No flatmates defined")
            return None

        current_assignment = self.get_assignment_for_chore(chore)
        if not current_assignment:
            logger.warning(f"No current assignment found for chore: {chore}")
            return None

        voted_flatmates = self.get_voted_flatmates()
        logger.debug(f"Flatmates who have already voted: {voted_flatmates}")

        eligible_flatmates = [
            f for f in flatmates
            if f["name"] != excluding_flatmate and f["name"] not in voted_flatmates
        ]

        logger.debug(
            f"Found {len(eligible_flatmates)} eligible flatmates who haven't voted yet: {[f['name'] for f in eligible_flatmates]}")

        if not eligible_flatmates:
            logger.warning("No eligible flatmates who haven't voted yet, falling back to any available flatmate")
            eligible_flatmates = [f for f in flatmates if f["name"] != excluding_flatmate]
            logger.debug(
                f"Fallback: {len(eligible_flatmates)} eligible flatmates: {[f['name'] for f in eligible_flatmates]}")

        if not eligible_flatmates:
            logger.warning("No eligible flatmates for reassignment")
            return None

        # Update statistics for the original flatmate (SKIPPED)
        logger.info(f"Updating SKIPPED statistics for {excluding_flatmate}")
        self.config_manager.update_flatmate_stats(excluding_flatmate, "skipped")

        next_flatmate = random.choice(eligible_flatmates)
        logger.info(f"Randomly selected {next_flatmate['name']} for reassignment")

        old_assignment = self.schedule_data["current_assignments"].get(chore)
        self.schedule_data["current_assignments"][chore] = next_flatmate["name"]
        logger.debug(f"Updated assignment for '{chore}': {old_assignment} -> {next_flatmate['name']}")

        self.add_voted_flatmate(next_flatmate["name"])

        # Update statistics for the new flatmate (REASSIGNED)
        logger.info(f"Updating REASSIGNED statistics for {next_flatmate['name']}")
        self.config_manager.update_flatmate_stats(next_flatmate["name"], "reassigned")

        self._save_schedule_data()
        logger.info(f"Chore '{chore}' successfully reassigned from {excluding_flatmate} to {next_flatmate['name']}")

        return next_flatmate["name"]

    def mark_chore_completed(self, chore, flatmate_name, helper=None):
        """
        Mark a chore as completed.

        Updates stats:
        - If helper: helper gets "helped" stat only; assigned person gets nothing
        - If no helper: assigned flatmate gets "completed" stat
        """
        logger.info(f"Marking chore '{chore}' as completed by {helper or flatmate_name}")

        if chore not in self.schedule_data.get("current_assignments", {}):
            logger.warning(f"Chore '{chore}' not found in current assignments")
            return False, "Chore not found in current assignments"

        if chore not in self.schedule_data.get("pending_chores", []):
            completed_by = self.schedule_data.get("completed_by", {}).get(chore, [])
            completer = helper or flatmate_name

            if completer in completed_by:
                logger.warning(f"Chore '{chore}' already marked as completed by {completer}")
                return False, f"You've already completed this chore"

            logger.info(f"Chore '{chore}' already completed, but allowing {completer} to mark it again")

            if "completed_by" not in self.schedule_data:
                self.schedule_data["completed_by"] = {}
            if chore not in self.schedule_data["completed_by"]:
                self.schedule_data["completed_by"][chore] = []

            self.schedule_data["completed_by"][chore].append(completer)

            if helper:
                logger.info(f"Updating HELPED stat for helper: {helper}")
                self.config_manager.update_flatmate_stats(helper, "helped")
            else:
                logger.info(f"Updating COMPLETED stat for assigned: {flatmate_name}")
                self.config_manager.update_flatmate_stats(flatmate_name, "completed")

            self._save_schedule_data()
            return True, "Chore marked as completed (additional)"

        # First completion
        self.schedule_data["pending_chores"].remove(chore)

        if "completed_by" not in self.schedule_data:
            self.schedule_data["completed_by"] = {}
        if chore not in self.schedule_data["completed_by"]:
            self.schedule_data["completed_by"][chore] = []

        completer = helper or flatmate_name
        self.schedule_data["completed_by"][chore].append(completer)

        if helper:
            # helper did the work — only they get credit
            logger.info(f"Helper {helper} completed chore for {flatmate_name}")
            self.config_manager.update_flatmate_stats(helper, "helped")
        else:
            self.config_manager.update_flatmate_stats(flatmate_name, "completed")

        self._save_schedule_data()
        logger.info(f"Chore '{chore}' marked as completed by {completer}")

        return True, "Chore marked as completed"

    def reset_schedule(self):
        """Reset the schedule data."""
        logger.info("Resetting schedule data")
        self.schedule_data = {
            "last_posted": None,
            "current_assignments": {},
            "previous_assignments": {},
            "rotation_indices": {},
            "voted_flatmates": [],
            "pending_chores": [],
            "excluded_for_next_rotation": []
        }
        self._save_schedule_data()
        logger.info("Schedule has been reset")
        return True, "Schedule has been reset"