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
            "excluded_for_next_rotation": [],
            "last_rotation_week": {},  # Track when each chore was last in rotation
            "completed_by": {}  # Track who has completed each chore
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

    def generate_new_schedule(self):
        """Generate a new chore schedule using a priority-based system that considers completion statistics and frequency."""
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

        # Get current week number (for frequency calculation)
        current_week = datetime.datetime.now().isocalendar()[1]
        logger.debug(f"Current week number: {current_week}")

        # Get full chore data
        chores_data = self.config_manager.get_chores_data()
        logger.debug(f"Got {len(chores_data)} chores with frequency data")

        # Filter chores based on frequency
        eligible_chores = []
        for chore in chores_data:
            chore_name = chore["name"]
            frequency = chore.get("frequency", 1)

            # Initialize last rotation week if not exists
            if "last_rotation_week" not in self.schedule_data:
                self.schedule_data["last_rotation_week"] = {}

            last_week = self.schedule_data["last_rotation_week"].get(chore_name, 0)

            # If frequency is 1 (weekly), always include
            # If frequency > 1, include if it's been enough weeks since last rotation
            if frequency == 1 or (current_week - last_week) % frequency == 0:
                eligible_chores.append(chore_name)
                # Update last rotation week
                self.schedule_data["last_rotation_week"][chore_name] = current_week

        logger.debug(f"Eligible chores for this week: {eligible_chores}")

        if not flatmates or not eligible_chores:
            logger.warning("Cannot generate schedule: No flatmates or no eligible chores")
            return {}

        # Reset 'recently_returned' flag for all flatmates
        for flatmate in self.config_manager.get_flatmates():
            if flatmate.get("recently_returned", False):
                logger.debug(f"Resetting 'recently_returned' flag for {flatmate['name']}")
                flatmate["recently_returned"] = False

        self.config_manager.save_config()

        # Calculate priority scores for each flatmate based on statistics
        flatmate_priorities = []
        for flatmate in flatmates:
            name = flatmate["name"]
            stats = self.config_manager.get_flatmate_stats(name)

            # Higher priority for those who have completed fewer chores
            completed = stats.get("completed", 0)
            skipped = stats.get("skipped", 0)
            reassigned = stats.get("reassigned", 0)

            # Priority formula: prioritize those who have completed fewer chores
            # and those who have skipped more (they should take responsibility)
            priority_score = 100 - (completed * 10) + (skipped * 5)

            # Lower priority if they had a chore last week (to avoid repetition)
            if name in previous_flatmate_chores:
                priority_score -= 15

            logger.debug(
                f"Flatmate {name} priority score: {priority_score} (completed: {completed}, skipped: {skipped})")
            flatmate_priorities.append((flatmate, priority_score))

        # Sort flatmates by priority (highest score first)
        sorted_flatmates = [f for f, _ in sorted(flatmate_priorities, key=lambda x: x[1], reverse=True)]
        logger.debug(f"Flatmates sorted by priority: {[f['name'] for f in sorted_flatmates]}")

        # New assignments dict
        new_assignments = {}
        available_flatmates = list(sorted_flatmates)  # Start with all flatmates

        # First pass: Try to assign chores avoiding last week's assignments
        for chore in eligible_chores:
            logger.debug(f"Assigning chore: {chore}")

            # Skip if no flatmates available
            if not available_flatmates:
                break

            # Get flatmate who had this chore last week
            previous_assignee = previous_assignments.get(chore)
            logger.debug(f"Previous assignee for '{chore}': {previous_assignee}")

            # Try to assign to someone who didn't have this chore last week
            assigned = False
            for flatmate in available_flatmates[:]:  # Copy to avoid modification during iteration
                if flatmate["name"] != previous_assignee:
                    new_assignments[chore] = flatmate["name"]
                    available_flatmates.remove(flatmate)
                    logger.info(f"Assigned '{chore}' to {flatmate['name']} (by priority)")
                    assigned = True
                    break

            # If we couldn't avoid last week's assignee, just pick the highest priority available
            if not assigned and available_flatmates:
                flatmate = available_flatmates[0]
                new_assignments[chore] = flatmate["name"]
                available_flatmates.remove(flatmate)
                logger.info(f"Assigned '{chore}' to {flatmate['name']} (only available option)")

        # Handle any remaining chores (if more chores than flatmates)
        remaining_chores = [c for c in eligible_chores if c not in new_assignments]
        if remaining_chores:
            logger.debug(f"Processing {len(remaining_chores)} remaining chores")

            # Reset available flatmates list, excluding those who already have multiple chores
            already_assigned = {}
            for chore, flatmate_name in new_assignments.items():
                already_assigned[flatmate_name] = already_assigned.get(flatmate_name, 0) + 1

            # Prioritize flatmates with fewest assignments
            available_for_extra = [(f, already_assigned.get(f["name"], 0)) for f in sorted_flatmates]
            available_for_extra.sort(key=lambda x: x[1])  # Sort by number of current assignments

            for chore in remaining_chores:
                if not available_for_extra:
                    logger.warning(f"No flatmates available for remaining chore: {chore}")
                    break

                flatmate, _ = available_for_extra[0]
                new_assignments[chore] = flatmate["name"]
                logger.info(f"Assigned remaining chore '{chore}' to {flatmate['name']}")

                # Update assignment count and re-sort
                for i, (f, count) in enumerate(available_for_extra):
                    if f["name"] == flatmate["name"]:
                        available_for_extra[i] = (f, count + 1)
                        break
                available_for_extra.sort(key=lambda x: x[1])

        # Save new assignments
        logger.info(f"Final assignments: {new_assignments}")
        self.schedule_data["current_assignments"] = new_assignments

        # Reset voted flatmates list for the new schedule
        logger.debug("Resetting voted flatmates list for new schedule")
        self.schedule_data["voted_flatmates"] = []

        # Initialize pending chores with all chores
        logger.debug(f"Setting pending chores to all {len(new_assignments)} chores")
        self.schedule_data["pending_chores"] = list(new_assignments.keys())

        # Initialize completed_by tracking
        logger.debug("Initializing completed_by tracking")
        self.schedule_data["completed_by"] = {chore: [] for chore in new_assignments.keys()}

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

    async def _handle_chore_reaction(self, payload):
        """Handle reactions to chore assignment messages."""
        logger.info(f"Handling chore reaction from user ID: {payload.user_id}, emoji: {payload.emoji}")

        # Get the channel
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            logger.error(f"Channel not found: {payload.channel_id}")
            return

        # Get the message
        try:
            logger.debug(f"Fetching message: {payload.message_id}")
            message = await channel.fetch_message(payload.message_id)
            if not message:
                logger.warning(f"Message not found: {payload.message_id}")
                return
        except discord.errors.NotFound:
            logger.error(f"Message {payload.message_id} not found, possibly deleted")
            return
        except Exception as e:
            logger.error(f"Failed to fetch message: {e}", exc_info=True)
            return

        # Get the user who reacted
        user = self.bot.get_user(payload.user_id)
        if not user:
            logger.warning(f"User not found: {payload.user_id}")
            return

        # Get the chore and assigned flatmate from our cache
        chore, assigned_flatmate_name = self.message_cache[payload.message_id]
        logger.debug(f"Cached assignment: chore '{chore}' assigned to {assigned_flatmate_name}")

        # Get the flatmate from the user's Discord ID
        flatmate = self.config_manager.get_flatmate_by_discord_id(payload.user_id)
        if not flatmate:
            # Remove reaction if the user is not a flatmate
            logger.warning(f"User {user.name} (ID: {payload.user_id}) is not a flatmate, removing reaction")
            await message.remove_reaction(payload.emoji, user)
            return

        # Get the emoji configuration
        emojis = self.config_manager.get_emoji()
        emoji_name = str(payload.emoji)
        logger.debug(f"Reaction emoji: {emoji_name}")

        # Check if this is the assigned flatmate or someone else helping out
        is_assigned_flatmate = flatmate["name"] == assigned_flatmate_name

        # Handle the reaction based on the emoji
        if emoji_name == emojis["completed"]:
            if is_assigned_flatmate:
                # Mark chore as completed by assigned flatmate
                logger.info(f"Marking chore '{chore}' as completed by {flatmate['name']}")
                success, message_text = self.schedule_manager.mark_chore_completed(chore, flatmate["name"])

                if success:
                    # Send completion message
                    completion_msg = BotStrings.TASK_COMPLETED.format(
                        mention=user.mention,
                        chore=chore
                    )
                    await channel.send(completion_msg)
                    logger.info(f"Chore '{chore}' marked as completed by {flatmate['name']}")

                    # Play celebration music
                    music_cog = self.bot.get_cog("MusicCog")
                    if music_cog:
                        logger.info("Triggering music celebration")
                        await music_cog.play_celebration(channel.guild)
                    else:
                        logger.warning("MusicCog not found, cannot play celebration music")
            else:
                # Another flatmate is completing the chore for the assigned flatmate
                logger.info(f"Flatmate {flatmate['name']} is completing chore '{chore}' for {assigned_flatmate_name}")

                # Mark chore as completed
                success, _ = self.mark_chore_completed(chore, assigned_flatmate_name,
                                                                        helper=flatmate["name"])

                if success:
                    # Get the assigned flatmate's discord mention
                    assigned_flatmate = self.config_manager.get_flatmate_by_name(assigned_flatmate_name)
                    assigned_mention = f"<@{assigned_flatmate['discord_id']}>" if assigned_flatmate else assigned_flatmate_name

                    # Send helper completion message
                    helper_msg = f"✅ {user.mention} has completed the chore **{chore}** for {assigned_mention}! What a hero! 🦸"
                    await channel.send(helper_msg)
                    logger.info(f"Chore '{chore}' completed by {flatmate['name']} for {assigned_flatmate_name}")

                    # Play celebration music
                    music_cog = self.bot.get_cog("MusicCog")
                    if music_cog:
                        logger.info("Triggering music celebration")
                        await music_cog.play_celebration(channel.guild)
                    else:
                        logger.warning("MusicCog not found, cannot play celebration music")

        elif emoji_name == emojis["unavailable"]:
            # Rest of your unavailable reaction handling...
            if not is_assigned_flatmate:
                # Only the assigned flatmate can mark as unavailable
                logger.warning(f"User {user.name} tried to mark someone else's chore as unavailable")
                await message.remove_reaction(payload.emoji, user)
                await channel.send(
                    f"{user.mention} You can only mark your own assigned chores as unavailable.",
                    delete_after=10
                )
                return

            # Mark the original flatmate as having voted
            logger.info(f"Marking flatmate {flatmate['name']} as unavailable for chore '{chore}'")
            self.add_voted_flatmate(flatmate["name"])

            # Randomly reassign the chore
            logger.debug(f"Randomly reassigning chore '{chore}' from {flatmate['name']}")
            next_flatmate_name = self.randomly_reassign_chore(
                chore,
                flatmate["name"]
            )

            if next_flatmate_name:
                # Get the next flatmate's Discord ID
                next_flatmate = self.config_manager.get_flatmate_by_name(next_flatmate_name)

                if next_flatmate:
                    next_discord_id = next_flatmate["discord_id"]
                    logger.debug(f"Chore reassigned to {next_flatmate_name} (ID: {next_discord_id})")

                    # Send reassignment notification
                    reassign_msg = BotStrings.TASK_REASSIGNED_FULL.format(
                        original_mention=user.mention,
                        chore=chore,
                        new_mention=f"<@{next_discord_id}>"
                    )
                    await channel.send(reassign_msg)

                    # Create a new message for the reassigned chore
                    new_task_msg = BotStrings.TASK_ASSIGNMENT.format(
                        mention=f"<@{next_discord_id}>",
                        chore=chore
                    )
                    new_message = await channel.send(new_task_msg)
                    logger.debug(f"Created new assignment message, ID: {new_message.id}")

                    # Add reactions to the new message
                    await new_message.add_reaction(emojis["completed"])
                    await new_message.add_reaction(emojis["unavailable"])
                    logger.debug(f"Added reactions to new message {new_message.id}")

                    # Update our message cache
                    self.message_cache[new_message.id] = (chore, next_flatmate_name)
                    logger.debug(f"Cached new message ID {new_message.id} for reassigned chore")

                    # Remove the old message from the cache
                    self.message_cache.pop(payload.message_id, None)
                    logger.debug(f"Removed old message ID {payload.message_id} from cache")

                    logger.info(
                        f"Chore '{chore}' successfully reassigned from {flatmate['name']} to {next_flatmate_name}")
            else:
                logger.warning(f"Failed to reassign chore '{chore}'")
                await channel.send(BotStrings.ERR_REASSIGN_FAILED.format(chore=chore))
        else:
            # Remove unrelated reactions
            logger.debug(f"Removing unrelated reaction {emoji_name} from message {payload.message_id}")
            await message.remove_reaction(payload.emoji, user)

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

    def reassign_chore_without_penalty(self, chore, current_assignee, new_assignee):
        """
        Reassign a chore from one flatmate to another without affecting their statistics.
        This is an admin function for exceptional situations.

        Args:
            chore (str): The chore to reassign
            current_assignee (str): Name of the current assignee
            new_assignee (str): Name of the new assignee

        Returns:
            bool: True if reassignment was successful, False otherwise
        """
        logger.info(f"Admin reassigning chore '{chore}' from {current_assignee} to {new_assignee} without penalty")

        # Check if chore exists in current assignments
        if chore not in self.schedule_data.get("current_assignments", {}):
            logger.warning(f"Chore '{chore}' not found in current assignments")
            return False

        # Check if current assignment matches
        if self.schedule_data["current_assignments"][chore] != current_assignee:
            logger.warning(
                f"Current assignee mismatch: expected {current_assignee}, got {self.schedule_data['current_assignments'][chore]}")
            return False

        # Update the assignment without updating any statistics
        old_assignee = self.schedule_data["current_assignments"][chore]
        self.schedule_data["current_assignments"][chore] = new_assignee
        logger.debug(f"Updated assignment for '{chore}': {old_assignee} -> {new_assignee}")

        # If the chore is in pending chores, keep it there
        # If it was already completed, it won't be in pending chores

        self._save_schedule_data()
        logger.info(
            f"Chore '{chore}' successfully reassigned from {current_assignee} to {new_assignee} without penalty")

        return True

    def mark_chore_completed(self, chore, flatmate_name, helper=None):
        """
        Mark a chore as completed.

        Args:
            chore (str): The chore that was completed
            flatmate_name (str): Name of the flatmate who was assigned the chore
            helper (str, optional): Name of the flatmate who helped, if different from the assignee

        Returns:
            tuple: (success, message)
        """
        logger.info(f"Marking chore '{chore}' as completed by {helper or flatmate_name}")

        # Check if chore exists in current assignments
        if chore not in self.schedule_data.get("current_assignments", {}):
            logger.warning(f"Chore '{chore}' not found in current assignments")
            return False, "Chore not found in current assignments"

        # Check if the chore is still pending
        if chore not in self.schedule_data.get("pending_chores", []):
            # Allow multiple completions - check if this person has already completed it
            completed_by = self.schedule_data.get("completed_by", {}).get(chore, [])
            completer = helper or flatmate_name

            if completer in completed_by:
                logger.warning(f"Chore '{chore}' already marked as completed by {completer}")
                return False, f"You've already completed this chore"

            # Allow another person to mark it as completed again
            logger.info(f"Chore '{chore}' already completed, but allowing {completer} to mark it again")

            # Track who completed it
            if "completed_by" not in self.schedule_data:
                self.schedule_data["completed_by"] = {}
            if chore not in self.schedule_data["completed_by"]:
                self.schedule_data["completed_by"][chore] = []

            self.schedule_data["completed_by"][chore].append(completer)

            # Update statistics for the helper
            self.config_manager.update_flatmate_stats(completer, "completed")

            # Save updated data
            self._save_schedule_data()
            logger.info(f"Chore '{chore}' marked as completed by {completer} (additional completion)")

            return True, "Chore marked as completed (additional)"

        # First completion - remove from pending chores
        self.schedule_data["pending_chores"].remove(chore)
        logger.debug(f"Removed chore '{chore}' from pending chores")

        # Initialize completed_by tracking if not exists
        if "completed_by" not in self.schedule_data:
            self.schedule_data["completed_by"] = {}
        if chore not in self.schedule_data["completed_by"]:
            self.schedule_data["completed_by"][chore] = []

        # Track who completed it
        completer = helper or flatmate_name
        self.schedule_data["completed_by"][chore].append(completer)

        # Update statistics for the completer
        self.config_manager.update_flatmate_stats(completer, "completed")

        # Save updated data
        self._save_schedule_data()
        logger.info(f"Chore '{chore}' marked as completed successfully by {completer}")

        return True, "Chore marked as completed"