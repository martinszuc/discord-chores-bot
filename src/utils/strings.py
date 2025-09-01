"""
Centralized string repository for Discord Chores Bot - Jamaican Style, mon!
All user-facing messages should be defined here for easy customization.
Big up yuhself and keep di place clean!
"""


class BotStrings:
    # General messages
    SCHEDULE_HEADER = "🔔 **Weekly CHORE Schedule - Time fi Clean Up!** 🔔"
    TASK_ASSIGNMENT = "Wah gwaan {mention}! Yuh chore fi dis week is: **{chore}** - Mek it happen, bredrin!"
    TASK_COMPLETED = "✅ Big up {mention}! Dem done complete dem chore: **{chore}** - Irie work!"
    TASK_COMPLETED_FOR_OTHER = "✅ Bombaclaat! {helper_mention} done complete di chore **{chore}** fi {assignee_mention}! Wah a real hero dat! 🦸"
    TASK_UNAVAILABLE = "❌ {mention} cyan't manage dem chore dis week, seen?"
    TASK_REASSIGNED = "**{chore}** now gonna be done by {mention} - new plan, mon!"
    TASK_REASSIGNED_FULL = "{original_mention} cyan't manage it.\n**{chore}** get reassigned to {new_mention} - bless up!"

    # Usage instructions
    REACTION_INSTRUCTIONS = (
        "**How fi respond, seen:**\n"
        "✅ - Mark as done when yuh finish di ting\n"
        "❌ - Tell wi if yuh cyan't manage dis week (wi gonna give it to somebody else)"
    )

    # Command responses
    CMD_NEW_SCHEDULE = "New chore schedule done post up! Time fi get busy!"
    CMD_NO_SCHEDULE = "No chore schedule set up yet, bredrin. Use `/chores next` fi make one."
    CMD_RESET_SCHEDULE = "Schedule get reset! Clean slate fi everybody!"

    # Error messages
    ERR_NO_ASSIGNMENTS = "No chore assignments dem find, mon."
    ERR_NO_FLATMATE_CHORE = "Yuh nuh have no chores assign dis week - lucky yuh!"
    ERR_REASSIGN_FAILED = "Couldn't reassign di chore: {chore} - something nah work right"
    ERR_CHANNEL_NOT_FOUND = "Chores channel missing, mon: {channel_id}"
    ERR_NO_ELIGIBLE_FLATMATES = "Nobody available fi take on dis chore, seen?"
    ERR_NEXT_WEEK_NO_ACTIVE = "No active flatmates find fi next week rotation - weh everybody deh?"
    ERR_NEXT_WEEK_INVALID_SELECTION = "Dat selection nah work right. Try again, bredrin."

    # Embed titles and fields
    EMBED_SCHEDULE_TITLE = "📋 Weekly Chore Schedule - Mek Wi Clean Up!"
    EMBED_SCHEDULE_FOOTER = "Last update time"
    EMBED_TASK_ASSIGNED = "🧹 Assigned to: {mention} - Yuh turn fi shine!"
    EMBED_HOW_TO_RESPOND = "How fi respond, seen"
    EMBED_REACTIONS_GUIDE = (
        "✅ - Done and dusted!\n"
        "❌ - Mi cyan't manage dis week (wi gonna find somebody else)"
    )

    # Admin messages
    ADMIN_CONFIG_RELOADED = "✅ Configuration reload successful - everything irie!"
    ADMIN_CONFIG_FAILED = "❌ Configuration reload fail: {error} - something nah right"
    ADMIN_TEST_NOTIFICATION = "🔔 **TEST NOTIFICATION - Just Testing, Mon!** 🔔"

    # Flatmate management
    FLATMATE_ADDED = "Roomie add successful - welcome to di cleaning crew!"
    FLATMATE_EXISTS = "Roomie with dis name already inna di system"
    FLATMATE_ID_EXISTS = "Roomie with dis Discord ID already register"
    FLATMATE_REMOVED = "Roomie remove successful - dem gone now"
    FLATMATE_NOT_FOUND = "Cyan't find dat roomie anywhere"

    # Chore management
    CHORE_ADDED = "Chore add successful - more work fi everybody!"
    CHORE_EXISTS = "Dis chore already inna di list"
    CHORE_REMOVED = "Chore remove successful - one less ting fi do"
    CHORE_NOT_FOUND = "Cyan't find dat chore nowhere"

    # Settings
    SETTING_UPDATED = "✅ Setting `{setting}` update to `{value}` - irie!"
    SETTING_CRITICAL_WARNING = "⚠️ Dis a critical setting, seen? Consider restart di bot fi di changes work proper."
    SETTING_INVALID = "❌ Invalid setting: {setting}. Valid settings dem: {valid_settings}"
    SETTING_INVALID_VALUE = "❌ Invalid value fi {setting}. {reason} - try again, mon"
    SETTING_CURRENT = "Current value fi `{setting}`: `{value}`"

    # Vacation mode
    VACATION_ENABLED = "✅ {name} now on vacation and exclude from rotation - enjoy yuh break!"
    VACATION_DISABLED = "✅ {name} welcome back to rotation! Hope yuh rest good!"
    VACATION_ENABLED_OTHER = "✅ {setter} put {name} on vacation. Dem exclude from rotation now."
    VACATION_DISABLED_OTHER = "✅ {setter} bring back {name} from vacation. Welcome back to di grind!"

    # Statistics
    STATS_HEADER = "📊 **Statistics fi {name} - How Dem a Perform** 📊"
    STATS_COMPLETED = "Completed: {count} chores - big up yuhself!"
    STATS_REASSIGNED = "Reassigned to: {count} chores - helpful bredrin!"
    STATS_SKIPPED = "Skipped: {count} chores - gwaan step up yuh game!"
    STATS_COMPLETION_RATE = "Completion Rate: {rate}% - {rate > 80 ? 'Irie work!' : 'Room fi improvement!'}"

    # Reminders
    REMINDER_HEADER = "⏰ **Chore Reminder - Nuh Forget!** ⏰"
    REMINDER_MESSAGE = "Yow {mention}! Nuh forget fi complete yuh chore: **{chore}** - time fi get busy!"
    REMINDER_SETTINGS_UPDATED = "✅ Reminder settings update successful - wi gonna keep yuh on track!"
    REMINDER_ENABLED = "Reminders now enable on {day} at {time} - wi nah mek yuh forget!"
    REMINDER_DISABLED = "Reminders now disable - yuh on yuh own now, mon."

    # Difficulty ratings
    DIFFICULTY_SET = "✅ Difficulty fi **{chore}** set to {level}/5 - know wah yuh getting into!"
    DIFFICULTY_VOTE_HEADER = "🗳️ **Vote Fi Chore Difficulty - Mek Wi Know!** 🗳️"
    DIFFICULTY_VOTE_INSTRUCTIONS = "React with di number dat show how hard yuh think **{chore}** is:"
    DIFFICULTY_VOTE_SCALE = "1️⃣ = Easy like Sunday morning, 5️⃣ = Harder dan concrete!"
    DIFFICULTY_VOTE_RESULT = "Di difficulty fi **{chore}** set to {level}/5 based on everybody vote - democracy work!"

    # Next week planning
    NEXT_WEEK_INCLUDED = "✅ {name} include inna di next chore rotation - time fi work!"
    NEXT_WEEK_EXCLUDED = "❌ {name} exclude from di next chore rotation - enjoy yuh break!"
    NEXT_WEEK_TOGGLE = "{user} switch {name} inclusion inna di next chore rotation - change up di plan!"

    # Multiple completion messages
    TASK_COMPLETED_BY_HELPER = "✅ Bless up {helper_mention}! Dem complete di chore **{chore}** dat was assign to {assignee_mention}! Big up fi keeping wi place clean! 🦸"
    TASK_COMPLETED_ADDITIONAL = "✅ {mention} also complete di chore **{chore}**! Bless up fi going above and beyond! 🙌"

    # Frequency related messages
    FREQUENCY_SET = "Frequency fi '{chore}' set to {frequency} ({freq_text}) - plan it out proper!"
    CHORE_ADDED_WITH_FREQUENCY = "Chore '{name}' add successful. It gonna show up {freq_text} - nuh worry, wi nah forget!"

    ERR_CHORE_ALREADY_COMPLETED = "Yuh done complete dis chore already, mon."
    ERR_ONLY_OWN_CHORE_UNAVAILABLE = "Yuh can only mark yuh own chores as unavailable, seen?"
    ERR_DIFFICULTY_RANGE = "Difficulty must be between 1 and 5, bredrin."
    ERR_FREQUENCY_MINIMUM = "Frequency must be at least 1, mon."
    ERR_VOTE_MESSAGE_DELETED = "Di vote message fi **{chore}** get deleted, seen."
    ERR_VOTE_PROCESSING = "Something wrong wid processing di vote fi **{chore}**, mon."
    ERR_NO_VOTES_CAST = "Nobody vote fi **{chore}** - weh everybody deh?"

    # Next week planning
    NEXT_WEEK_PLANNING_TITLE = "🗓️ Next Week's Chore Rotation Planning - Plan Fi Tomorrow!"
    NEXT_WEEK_PLANNING_DESC = "Below are di flatmates who gonna be inna next week's chore rotation.\nReact wid di number beside a flatmate fi toggle dem inclusion/exclusion."
    NEXT_WEEK_STATUS_EXCLUDED = "❌ Excluded from next rotation"
    NEXT_WEEK_STATUS_INCLUDED = "✅ Included in next rotation"
    NEXT_WEEK_INSTRUCTIONS_TITLE = "Instructions"
    NEXT_WEEK_INSTRUCTIONS_DESC = "React wid di number next to a flatmate fi toggle dem inclusion/exclusion.\nChanges gonna apply to di next schedule generation."
    NEXT_WEEK_INCLUDED_MSG = "{user} include {flatmate} inna di next chore rotation - welcome back!"
    NEXT_WEEK_EXCLUDED_MSG = "{user} exclude {flatmate} from di next chore rotation - tek a break!"

    # Difficulty voting
    DIFFICULTY_VOTE_MESSAGE = "Vote pon di difficulty of **{chore}** - mek wi know how hard it is:"
    DIFFICULTY_VOTE_RESULT_SUCCESS = "Di difficulty fi **{chore}** now set to {level}/5 based on {votes} votes - democracy work!"

    # Multiple completion messages (updated)
    TASK_COMPLETED_BY_HELPER_ALT = "✅ Big up {mention}! Dem complete di chore **{chore}** dat was assigned to {assigned_mention}! Thank yuh fi keeping wi place clean! 🦸"
    TASK_COMPLETED_ADDITIONAL_ALT = "✅ {mention} also complete di chore **{chore}**! Thank yuh fi going above and beyond! 🙌"

    # Frequency messages
    FREQUENCY_UPDATED = "Frequency fi '{chore}' set to {frequency} ({freq_text}) - plan out proper!"
    CHORE_ADDED_SUCCESS = "Chore '{name}' add successful. It gonna appear {freq_text} - wi nah forget!"