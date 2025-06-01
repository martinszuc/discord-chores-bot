"""
Centralized string repository for Discord Chores Bot.
All user-facing messages should be defined here for easy customization.
"""


class BotStrings:
    # General messages
    SCHEDULE_HEADER = "🔔 **Weekly SEX Schedule** 🔔"
    TASK_ASSIGNMENT = "Hey {mention}, your chore for this week is: **{chore}**"
    TASK_COMPLETED = "✅ {mention} has completed their chore: **{chore}**"
    TASK_COMPLETED_FOR_OTHER = "✅ {helper_mention} has completed the chore **{chore}** for {assignee_mention}! What a hero! 🦸"
    TASK_UNAVAILABLE = "❌ {mention} can't complete their chore this week."
    TASK_REASSIGNED = "**{chore}** odteraz bude robic {mention}."
    TASK_REASSIGNED_FULL = "{original_mention} nemoze.\n**{chore}** has been reassigned to {new_mention}."

    # Usage instructions
    REACTION_INSTRUCTIONS = (
        "**How to respond:**\n"
        "✅ - Mark as completed once you've done the deed\n"
        "❌ - Indicate you can't do it this week (will be randomly reassigned)"
    )

    # Command responses
    CMD_NEW_SCHEDULE = "New chore schedule has been posted!"
    CMD_NO_SCHEDULE = "No chore schedule has been generated yet. Use `/chores next` to generate one."
    CMD_RESET_SCHEDULE = "Schedule has been reset!"

    # Error messages
    ERR_NO_ASSIGNMENTS = "No chore assignments found."
    ERR_NO_FLATMATE_CHORE = "You don't have any assigned chores this week."
    ERR_REASSIGN_FAILED = "Failed to reassign chore: {chore}"
    ERR_CHANNEL_NOT_FOUND = "Chores channel not found: {channel_id}"
    ERR_NO_ELIGIBLE_FLATMATES = "No eligible flatmates for reassignment."
    ERR_NEXT_WEEK_NO_ACTIVE = "No active flatmates found for next week's rotation."
    ERR_NEXT_WEEK_INVALID_SELECTION = "Invalid selection. Please try again."

    # Embed titles and fields
    EMBED_SCHEDULE_TITLE = "📋 Weekly Chore Schedule"
    EMBED_SCHEDULE_FOOTER = "Last updated"
    EMBED_TASK_ASSIGNED = "🧹 Assigned to: {mention}"
    EMBED_HOW_TO_RESPOND = "How to respond"
    EMBED_REACTIONS_GUIDE = (
        "✅ - Mark as completed\n"
        "❌ - I can't do it this week (will be randomly reassigned)"
    )

    # Admin messages
    ADMIN_CONFIG_RELOADED = "✅ Configuration reloaded successfully."
    ADMIN_CONFIG_FAILED = "❌ Failed to reload configuration: {error}"
    ADMIN_TEST_NOTIFICATION = "🔔 **TEST NOTIFICATION** 🔔"

    # Flatmate management
    FLATMATE_ADDED = "Homie added successfully"
    FLATMATE_EXISTS = "Homie with this name already exists"
    FLATMATE_ID_EXISTS = "Homie with this Discord ID already exists"
    FLATMATE_REMOVED = "Homie removed successfully"
    FLATMATE_NOT_FOUND = "Homie not found"

    # Chore management
    CHORE_ADDED = "Chore added successfully"
    CHORE_EXISTS = "Chore already exists"
    CHORE_REMOVED = "Chore removed successfully"
    CHORE_NOT_FOUND = "Chore not found"

    # Settings
    SETTING_UPDATED = "✅ Setting `{setting}` updated to `{value}`."
    SETTING_CRITICAL_WARNING = "⚠️ This is a critical setting. Consider restarting the bot for the changes to take full effect."
    SETTING_INVALID = "❌ Invalid setting: {setting}. Valid settings are: {valid_settings}"
    SETTING_INVALID_VALUE = "❌ Invalid value for {setting}. {reason}"
    SETTING_CURRENT = "Current value of `{setting}`: `{value}`"

    # Vacation mode
    VACATION_ENABLED = "✅ {name} is now on vacation and will be excluded from rotation."
    VACATION_DISABLED = "✅ {name} welcome back to rotation!"
    VACATION_ENABLED_OTHER = "✅ {setter} has set {name} to vacation. They will be excluded from rotation."
    VACATION_DISABLED_OTHER = "✅ {setter} has removed {name} from vacation. Welcome back to rotation!"

    # Statistics
    STATS_HEADER = "📊 **Statistics for {name}** 📊"
    STATS_COMPLETED = "Completed: {count} chores"
    STATS_REASSIGNED = "Reassigned to: {count} chores"
    STATS_SKIPPED = "Skipped: {count} chores"
    STATS_COMPLETION_RATE = "Completion Rate: {rate}%"

    # Reminders
    REMINDER_HEADER = "⏰ **Chore Reminder** ⏰"
    REMINDER_MESSAGE = "Hey {mention}, don't forget to complete your chore: **{chore}**"
    REMINDER_SETTINGS_UPDATED = "✅ Reminder settings updated successfully."
    REMINDER_ENABLED = "Reminders are now enabled on {day} at {time}."
    REMINDER_DISABLED = "Reminders are now disabled."

    # Difficulty ratings
    DIFFICULTY_SET = "✅ Difficulty for **{chore}** set to {level}/5."
    DIFFICULTY_VOTE_HEADER = "🗳️ **Vote for Chore Difficulty** 🗳️"
    DIFFICULTY_VOTE_INSTRUCTIONS = "React with the number that represents how difficult you think **{chore}** is:"
    DIFFICULTY_VOTE_SCALE = "1️⃣ = Very Easy, 5️⃣ = moc moc"
    DIFFICULTY_VOTE_RESULT = "The difficulty of **{chore}** has been set to {level}/5 based on votes."

    # Next week planning
    NEXT_WEEK_INCLUDED = "✅ {name} has been included in the next chore rotation."
    NEXT_WEEK_EXCLUDED = "❌ {name} has been excluded from the next chore rotation."
    NEXT_WEEK_TOGGLE = "{user} has toggled {name}'s inclusion in the next chore rotation."

    # Multiple completion messages
    TASK_COMPLETED_BY_HELPER = "✅ {helper_mention} has completed the chore **{chore}** that was assigned to {assignee_mention}! Thank you so much for participating in keeping our flat clean! 🦸"
    TASK_COMPLETED_ADDITIONAL = "✅ {mention} has also completed the chore **{chore}**! Thank you so much for participating in keeping our flat clean! 🙌"

    # Frequency related messages
    FREQUENCY_SET = "Frequency for '{chore}' set to {frequency} ({freq_text})."
    CHORE_ADDED_WITH_FREQUENCY = "Chore '{name}' added successfully. It will appear {freq_text}."