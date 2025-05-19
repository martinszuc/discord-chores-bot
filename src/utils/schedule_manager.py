import json
import logging
import os
import datetime
import random
from pathlib import Path

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
                # Initialize with empty data
                default_data = {
                    "last_posted": None,
                    "current_assignments": {},
                    "previous_assignments": {},  # Add storage for previous week's assignments
                    "rotation_indices": {},
                    "voted_flatmates": [],  # Track flatmates who have already voted
                    "pending_chores": [],  # Track chores that haven't been completed
                    "excluded_for_next_rotation": []  # Track flatmates to exclude from the next rotation
                }
                self._save_schedule_data(default_data)
                return default_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schedule data file: {e}")
            # Initialize with empty data on error
            return self._initialize_default_data()
        except Exception as e:
            logger.error(f"Failed to load schedule data: {e}", exc_info=True)
            # Initialize with empty data on error
            return self._initialize_default_data()

    def _initialize_default_data(self):
        """Initialize default schedule data."""
        logger.info("Initializing default schedule data")
        default_data = {
            "last_posted": None,
            "current_assignments": {},
            "previous_assignments": {},  # Add storage for previous week's assignments
            "rotation_indices": {},
            "voted_flatmates": [],
            "pending_chores": [],
            "excluded_for_next_rotation": []
        }
        return default_data

    def _save_schedule_data(self, data=None):
        """Save schedule data to the data file."""
        logger.info(f"Saving schedule data to: {self.data_file}")
        try:
            # Create parent directory if it doesn't exist
            Path(os.path.dirname(self.data_file)).mkdir(parents=True, exist_ok=True)

            # Save data
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

        # Reset voted flatmates when posting a new schedule
        old_voted = self.schedule_data.get("voted_flatmates", [])
        self.schedule_data["voted_flatmates"] = []
        logger.debug(f"Reset voted flatmates: {old_voted} -> []")

        # Initialize pending chores with all chores
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

    def calculate_priority_score(self, flatmate):
        """Calculate a priority score for a flatmate based on their stats.
        Lower score means higher priority to be assigned a chore.
        """
        logger.debug(f"Calculating priority score for flatmate: {flatmate['name']}")
        stats = self.config_manager.get_flatmate_stats(flatmate["name"])
        if not stats:
            logger.debug(f"No stats found for {flatmate['name']}, returning default score 0")
            return 0

        # Calculate score - give higher priority to those who complete chores
        # and lower priority to those who skip or get reassigned
        completed = stats.get("completed", 0)
        skipped = stats.get("skipped", 0)
        reassigned = stats.get("reassigned", 0)

        score = skipped * 2 + reassigned - completed * 0.5

        logger.debug(
            f"Priority score for {flatmate['name']}: {score} (completed: {completed}, skipped: {skipped}, reassigned: {reassigned})")
        return score

    def generate_new_schedule(self):
        """Generate a new chore schedule using the priority system and difficulty balancing,
        while ensuring rotation between weeks.
        """
        logger.info("Generating new chore schedule")

        # Store current assignments as previous before generating new ones
        current_assignments = self.get_current_assignments()
        if current_assignments:
            logger.debug(f"Storing current assignments as previous: {current_assignments}")
            self.schedule_data["previous_assignments"] = current_assignments.copy()

        # Get previous assignments to avoid repetition
        previous_assignments = self.get_previous_assignments()
        logger.debug(f"Previous assignments: {previous_assignments}")

        # Create inverse mapping: flatmate -> previous chore
        previous_flatmate_chores = {}
        for chore, flatmate in previous_assignments.items():
            previous_flatmate_chores[flatmate] = chore
        logger.debug(f"Previous flatmate -> chore mapping: {previous_flatmate_chores}")

        # Get active flatmates (not on vacation)
        all_active_flatmates = self.config_manager.get_active_flatmates()
        logger.debug(f"Found {len(all_active_flatmates)} active flatmates (not on vacation)")

        # Filter out flatmates excluded for the next rotation
        excluded_flatmates = self.get_excluded_for_next_rotation()
        logger.debug(f"Excluding flatmates from next rotation: {excluded_flatmates}")

        flatmates = [f for f in all_active_flatmates if f["name"] not in excluded_flatmates]
        logger.debug(f"Final list of {len(flatmates)} flatmates for schedule generation")

        # Get list of chores
        chores = self.config_manager.get_chores()
        logger.debug(f"Found {len(chores)} chores to assign")

        if not flatmates or not chores:
            logger.warning("Cannot generate schedule: No flatmates or no chores defined")
            return {}

        # Reset 'recently_returned' flag for all flatmates
        for flatmate in self.config_manager.get_flatmates():
            if flatmate.get("recently_returned", False):
                logger.debug(f"Resetting 'recently_returned' flag for {flatmate['name']}")
                flatmate["recently_returned"] = False

        self.config_manager.save_config()

        # Sort chores by difficulty (highest first)
        sorted_chores = sorted(
            chores,
            key=lambda c: self.config_manager.get_chore_details(c).get("difficulty", 1),
            reverse=True
        )

        logger.debug(f"Chores sorted by difficulty (highest first): {sorted_chores}")

        # Calculate priority scores for flatmates
        logger.debug("Calculating priority scores for all flatmates")
        flatmates_with_scores = [
            (f, self.calculate_priority_score(f)) for f in flatmates
        ]

        for f, score in flatmates_with_scores:
            logger.debug(f"Priority score for {f['name']}: {score}")

        # Sort flatmates by priority score (lowest first = highest priority)
        sorted_flatmates = [f for f, _ in sorted(
            flatmates_with_scores,
            key=lambda item: item[1]
        )]

        logger.debug(f"Flatmates sorted by priority (highest first): {[f['name'] for f in sorted_flatmates]}")

        # Assign chores, starting with the most difficult chores
        new_assignments = {}
        flatmate_difficulty_sum = {f["name"]: 0 for f in flatmates}
        assigned_flatmates = set()  # Track which flatmates have been assigned

        logger.info("Beginning chore assignment process")

        # First pass: Try to assign each chore to someone who didn't have it last week
        for chore in sorted_chores:
            # Get difficulty of this chore
            chore_difficulty = self.config_manager.get_chore_details(chore).get("difficulty", 1)
            logger.debug(f"Assigning chore: {chore} (difficulty: {chore_difficulty})")

            # Find previous assignee of this chore
            previous_assignee = previous_assignments.get(chore)
            logger.debug(f"Previous assignee for '{chore}': {previous_assignee}")

            # Find eligible flatmates (those who don't have an assignment yet and didn't have this chore last week)
            eligible_flatmates = [
                f for f in sorted_flatmates
                if f["name"] not in assigned_flatmates and f["name"] != previous_assignee
            ]

            if not eligible_flatmates:
                # If no eligible flatmates, use anyone who hasn't been assigned yet
                eligible_flatmates = [f for f in sorted_flatmates if f["name"] not in assigned_flatmates]
                logger.debug(
                    f"No eligible flatmates who didn't have this chore last week, falling back to {len(eligible_flatmates)} unassigned flatmates")

            if eligible_flatmates:
                # Sort by current load
                sorted_by_load = sorted(
                    eligible_flatmates,
                    key=lambda f: flatmate_difficulty_sum[f["name"]]
                )

                # Assign to flatmate with lowest load
                assigned_flatmate = sorted_by_load[0]
                new_assignments[chore] = assigned_flatmate["name"]
                assigned_flatmates.add(assigned_flatmate["name"])

                # Update their total difficulty
                old_load = flatmate_difficulty_sum[assigned_flatmate["name"]]
                flatmate_difficulty_sum[assigned_flatmate["name"]] += chore_difficulty
                new_load = flatmate_difficulty_sum[assigned_flatmate["name"]]

                logger.info(f"Assigned '{chore}' to {assigned_flatmate['name']} (previous: {previous_assignee})")
                logger.debug(f"Updated load for {assigned_flatmate['name']}: {old_load} -> {new_load}")
            else:
                logger.warning(f"No eligible flatmates for chore: {chore}")

        # Second pass: Assign any remaining chores (should only happen if more chores than flatmates)
        remaining_chores = [c for c in sorted_chores if c not in new_assignments]
        if remaining_chores:
            logger.debug(f"Assigning {len(remaining_chores)} remaining chores: {remaining_chores}")

            for chore in remaining_chores:
                chore_difficulty = self.config_manager.get_chore_details(chore).get("difficulty", 1)

                # Sort all flatmates by current load
                sorted_by_load = sorted(
                    sorted_flatmates,
                    key=lambda f: flatmate_difficulty_sum[f["name"]]
                )

                # Assign to flatmate with lowest load
                assigned_flatmate = sorted_by_load[0]
                new_assignments[chore] = assigned_flatmate["name"]

                # Update their total difficulty
                old_load = flatmate_difficulty_sum[assigned_flatmate["name"]]
                flatmate_difficulty_sum[assigned_flatmate["name"]] += chore_difficulty
                new_load = flatmate_difficulty_sum[assigned_flatmate["name"]]

                logger.info(f"Assigned remaining chore '{chore}' to {assigned_flatmate['name']}")
                logger.debug(f"Updated load for {assigned_flatmate['name']}: {old_load} -> {new_load}")

        # Save new assignments
        logger.info(f"Final assignments: {new_assignments}")
        self.schedule_data["current_assignments"] = new_assignments

        # Reset voted flatmates list for the new schedule
        logger.debug("Resetting voted flatmates list for new schedule")
        self.schedule_data["voted_flatmates"] = []

        # Initialize pending chores with all chores
        logger.debug(f"Setting pending chores to all {len(new_assignments)} chores")
        self.schedule_data["pending_chores"] = list(new_assignments.keys())

        # Clear exclusions after generating the schedule
        logger.debug("Clearing exclusions after generating schedule")
        self.clear_next_rotation_exclusions()

        self._save_schedule_data()
        logger.info("New schedule generated and saved successfully")

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
        logger.info(f"Randomly reassigning chore '{chore}' from {excluding_flatmate}")

        # Get active flatmates
        flatmates = self.config_manager.get_active_flatmates()
        if not flatmates:
            logger.warning("Cannot reassign: No flatmates defined")
            return None

        # Get current assignment
        current_assignment = self.get_assignment_for_chore(chore)
        if not current_assignment:
            logger.warning(f"No current assignment found for chore: {chore}")
            return None

        # Get flatmates who haven't voted this week
        voted_flatmates = self.get_voted_flatmates()
        logger.debug(f"Flatmates who have already voted: {voted_flatmates}")

        # Eligible flatmates: not the current assignee, not on vacation, and hasn't voted yet
        eligible_flatmates = [
            f for f in flatmates
            if f["name"] != excluding_flatmate and f["name"] not in voted_flatmates
        ]

        logger.debug(
            f"Found {len(eligible_flatmates)} eligible flatmates who haven't voted yet: {[f['name'] for f in eligible_flatmates]}")

        # If no eligible flatmates who haven't voted, fall back to anyone except the current assignee
        if not eligible_flatmates:
            logger.warning("No eligible flatmates who haven't voted yet, falling back to any available flatmate")
            eligible_flatmates = [f for f in flatmates if f["name"] != excluding_flatmate]
            logger.debug(
                f"Fallback: {len(eligible_flatmates)} eligible flatmates: {[f['name'] for f in eligible_flatmates]}")

        if not eligible_flatmates:
            logger.warning("No eligible flatmates for reassignment")
            return None

        # Update statistics for the original flatmate
        logger.info(f"Updating skip statistics for {excluding_flatmate}")
        self.config_manager.update_flatmate_stats(excluding_flatmate, "skipped")

        # Randomly select a flatmate
        next_flatmate = random.choice(eligible_flatmates)
        logger.info(f"Randomly selected {next_flatmate['name']} for reassignment")

        # Update assignment
        old_assignment = self.schedule_data["current_assignments"].get(chore)
        self.schedule_data["current_assignments"][chore] = next_flatmate["name"]
        logger.debug(f"Updated assignment for '{chore}': {old_assignment} -> {next_flatmate['name']}")

        # Mark the new flatmate as having "voted" (been assigned a task)
        self.add_voted_flatmate(next_flatmate["name"])

        # Update statistics for the new flatmate
        logger.info(f"Updating reassignment statistics for {next_flatmate['name']}")
        self.config_manager.update_flatmate_stats(next_flatmate["name"], "reassigned")

        self._save_schedule_data()
        logger.info(f"Chore '{chore}' successfully reassigned from {excluding_flatmate} to {next_flatmate['name']}")

        return next_flatmate["name"]

    def mark_chore_completed(self, chore, flatmate_name, helper=None):
        """
        Mark a chore as completed by a flatmate.

        Args:
            chore (str): The chore that was completed
            flatmate_name (str): Name of the flatmate assigned to the chore
            helper (str, optional): Name of the flatmate who helped complete the chore

        Returns:
            tuple: (success, message)
        """
        logger.info(f"Marking chore '{chore}' as completed by {flatmate_name}" +
                    (f" with help from {helper}" if helper else ""))

        # Check if the chore exists and is assigned to the flatmate
        current_assignment = self.get_assignment_for_chore(chore)
        if not current_assignment:
            logger.warning(f"No assignment found for chore: {chore}")
            return False, f"No assignment found for chore: {chore}"

        if current_assignment != flatmate_name:
            logger.warning(f"Chore '{chore}' is assigned to {current_assignment}, not {flatmate_name}")
            return False, f"Chore is assigned to {current_assignment}, not {flatmate_name}"

        # Remove from pending chores
        if "pending_chores" not in self.schedule_data:
            logger.debug("Initializing pending_chores list")
            self.schedule_data["pending_chores"] = []

        if chore in self.schedule_data["pending_chores"]:
            logger.debug(f"Removing '{chore}' from pending chores")
            self.schedule_data["pending_chores"].remove(chore)
        else:
            logger.debug(f"Chore '{chore}' not in pending list, possibly already completed")

        # If there's a helper, update their stats instead of the assigned flatmate
        if helper:
            # Update helper statistics
            logger.info(f"Updating completion statistics for helper {helper}")
            self.config_manager.update_flatmate_stats(helper, "completed")

            # Mark helper as having voted
            self.add_voted_flatmate(helper)

            # We don't mark the original flatmate as having completed or voted
            # This way they don't get a completion stat but also aren't penalized
        else:
            # Mark flatmate as having voted
            self.add_voted_flatmate(flatmate_name)

            # Update statistics for the assigned flatmate
            logger.info(f"Updating completion statistics for {flatmate_name}")
            self.config_manager.update_flatmate_stats(flatmate_name, "completed")

        self._save_schedule_data()
        logger.info(f"Chore '{chore}' marked as completed" +
                    (f" by {helper} for {flatmate_name}" if helper else f" by {flatmate_name}"))

        return True, f"Chore '{chore}' marked as completed" + (
            f" by {helper} for {flatmate_name}" if helper else f" by {flatmate_name}")

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

    def special_one_time_rotation_fix(self):
        """One-time fix to ensure people who completed tasks last week
        are not assigned in the next rotation.
        """
        logger.info("Running special one-time rotation fix")

        # Get current assignments
        current_assignments = self.get_current_assignments()
        if not current_assignments:
            logger.warning("No current assignments to fix")
            return False, "No current assignments to fix"

        # Get the list of people who completed their tasks (not in pending chores)
        pending_chores = self.get_pending_chores()
        logger.debug(f"Current pending chores: {pending_chores}")

        completed_flatmates = []
        for chore, flatmate in current_assignments.items():
            if chore not in pending_chores:
                # If the chore is not pending, it was completed
                logger.debug(f"Flatmate {flatmate} completed chore '{chore}'")
                completed_flatmates.append(flatmate)

        logger.info(f"Flatmates who completed tasks: {completed_flatmates}")

        # Get all active flatmates
        all_active_flatmates = self.config_manager.get_active_flatmates()

        # Find flatmates who didn't complete tasks
        non_completing_flatmates = [f["name"] for f in all_active_flatmates
                                    if f["name"] not in completed_flatmates]

        logger.info(f"Flatmates who didn't complete tasks: {non_completing_flatmates}")

        if len(non_completing_flatmates) < len(self.config_manager.get_chores()):
            logger.warning("Not enough non-completing flatmates for all chores")
            return False, "Not enough flatmates who didn't complete tasks for all chores"

        # Exclude everyone except the non-completing flatmates from next rotation
        for flatmate in all_active_flatmates:
            if flatmate["name"] not in non_completing_flatmates:
                self.exclude_from_next_rotation(flatmate["name"])
                logger.info(f"Excluded {flatmate['name']} from next rotation as they completed their task")

        # Store current assignments as previous before next generation
        self.schedule_data["previous_assignments"] = current_assignments.copy()
        self._save_schedule_data()

        logger.info("One-time rotation fix applied successfully")
        return True, f"One-time fix applied. Next rotation will only include: {', '.join(non_completing_flatmates)}"