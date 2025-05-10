"""
Centralized string repository for Discord Chores Bot.
All user-facing messages should be defined here for easy customization.
"""


class BotStrings:
    # General messages
    SCHEDULE_HEADER = "🔔 **Weekly Chore Schedule** 🔔"
    TASK_ASSIGNMENT = "Hey {mention}, your chore for this week is: **{chore}**"
    TASK_COMPLETED = "✅ {mention} has completed their chore: **{chore}**"
    TASK_UNAVAILABLE = "❌ {mention} can't complete their chore this week."
    TASK_REASSIGNED = "**{chore}** has been reassigned to {mention}."
    TASK_REASSIGNED_FULL = "{original_mention} can't complete their chore this week.\n**{chore}** has been reassigned to {new_mention}."

    # Usage instructions
    REACTION_INSTRUCTIONS = (
        "**How to respond to your chore assignments:**\n"
        "✅ - Mark as completed once you've done the chore\n"
        "❌ - Indicate you can't do it this week (will be randomly reassigned to someone who hasn't voted yet)"
    )

    # Command responses
    CMD_NEW_SCHEDULE = "New chore schedule has been posted!"
    CMD_NO_SCHEDULE = "No chore schedule has been generated yet. Use `!chores next` to generate one."
    CMD_RESET_SCHEDULE = "Schedule has been reset!"

    # Error messages
    ERR_NO_ASSIGNMENTS = "No chore assignments found."
    ERR_NO_FLATMATE_CHORE = "You don't have any assigned chores this week."
    ERR_REASSIGN_FAILED = "Failed to reassign chore: {chore}"
    ERR_CHANNEL_NOT_FOUND = "Chores channel not found: {channel_id}"
    ERR_NO_ELIGIBLE_FLATMATES = "No eligible flatmates for reassignment."

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
    FLATMATE_ADDED = "Flatmate added successfully"
    FLATMATE_EXISTS = "Flatmate with this name already exists"
    FLATMATE_ID_EXISTS = "Flatmate with this Discord ID already exists"
    FLATMATE_REMOVED = "Flatmate removed successfully"
    FLATMATE_NOT_FOUND = "Flatmate not found"

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