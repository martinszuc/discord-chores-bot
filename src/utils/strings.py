"""
Gordon Ramsay Discord Chores Bot - Aggressive Chef Edition
For mature audiences only. Extreme profanity ahead.
"""


class BotStrings:
    # General messages
    SCHEDULE_HEADER = "🔥 **WEEKLY FUCKING CLEANING SCHEDULE - GET YOUR ARSES MOVING!** 🔥"
    TASK_ASSIGNMENT = "{mention}! Your job this week: **{chore}** - And don't fuck it up like last time, you muppet!"
    TASK_COMPLETED = "✅ FINALLY! {mention} actually finished **{chore}** without fucking it up! Congratulations on doing the bare minimum, you donkey!"
    TASK_COMPLETED_FOR_OTHER = "✅ Bloody hell! {helper_mention} had to do **{chore}** because {assignee_mention} is a useless waste of space! At least someone has a brain!"
    TASK_UNAVAILABLE = "❌ {mention} can't do their job this week. What a fucking surprise! Absolutely pathetic!"
    TASK_REASSIGNED = "**{chore}** is now {mention}'s problem - Try not to fuck this up too, yeah?"
    TASK_REASSIGNED_FULL = "{original_mention} is too incompetent to handle this.\n**{chore}** has been given to {new_mention} - Don't let me down or I'll shove this mop where the sun doesn't shine!"

    # Usage instructions
    REACTION_INSTRUCTIONS = (
        "**Listen up, you dense cabbage:**\n"
        "✅ - Mark it done when you've ACTUALLY finished, not before\n"
        "❌ - Click this if you're too bloody useless to do your job (and we'll find someone with an actual functioning brain)"
    )

    # Command responses
    CMD_NEW_SCHEDULE = "New cleaning schedule is up! Stop standing there like a bunch of fucking statues and GET TO WORK!"
    CMD_NO_SCHEDULE = "There's no schedule yet, you absolute muppet. Use `/chores next` to make one, or do I have to wipe your arse for you too?"
    CMD_RESET_SCHEDULE = "Schedule reset! Fresh start, though I'm sure you'll fuck this up just as badly!"

    # Error messages
    ERR_NO_ASSIGNMENTS = "No chores assigned yet, you lazy sods."
    ERR_NO_FLATMATE_CHORE = "You don't have a chore this week - Don't get cocky, your turn is coming!"
    ERR_REASSIGN_FAILED = "Can't reassign {chore} - Even the bot has given up on you lot!"
    ERR_CHANNEL_NOT_FOUND = "Can't find the chores channel {channel_id} - What kind of amateur operation is this?!"
    ERR_NO_ELIGIBLE_FLATMATES = "Nobody's available to take this chore. Absolutely fucking useless, all of you!"
    ERR_NEXT_WEEK_NO_ACTIVE = "No active flatmates for next week - Where the fuck is everyone?!"
    ERR_NEXT_WEEK_INVALID_SELECTION = "That selection doesn't work. Try again and actually use your brain this time!"

    # Embed titles and fields
    EMBED_SCHEDULE_TITLE = "📋 Weekly Cleaning Schedule - Stop Being Disgusting Pigs!"
    EMBED_SCHEDULE_FOOTER = "Last updated"
    EMBED_TASK_ASSIGNED = "🧹 Assigned to: {mention} - Don't fuck this up!"
    EMBED_HOW_TO_RESPOND = "How to respond (if your brain can handle it)"
    EMBED_REACTIONS_GUIDE = (
        "✅ - It's done! (actually done, not your bullshit version of 'done')\n"
        "❌ - I'm too incompetent to handle this simple task"
    )

    # Admin messages
    ADMIN_CONFIG_RELOADED = "✅ Config reloaded - Hopefully you didn't break everything this time!"
    ADMIN_CONFIG_FAILED = "❌ Config reload failed: {error} - OF COURSE you fucked it up!"
    ADMIN_TEST_NOTIFICATION = "🔔 **TEST NOTIFICATION - This is a test, you muppets!** 🔔"

    # Flatmate management
    FLATMATE_ADDED = "Flatmate added - Welcome to the team of incompetent idiots!"
    FLATMATE_EXISTS = "This flatmate already exists, you thick plank!"
    FLATMATE_ID_EXISTS = "This Discord ID is already registered - Are you blind or just stupid?"
    FLATMATE_REMOVED = "Flatmate removed - One less disappointment to deal with!"
    FLATMATE_NOT_FOUND = "Can't find this flatmate - Did you make them up, you muppet?"

    # Chore management
    CHORE_ADDED = "Chore added - More work for you lazy bastards!"
    CHORE_EXISTS = "This chore already exists - Wake up!"
    CHORE_REMOVED = "Chore removed - One less thing for you to fuck up!"
    CHORE_NOT_FOUND = "Can't find this chore anywhere - Did you pull that out of your arse?"

    # Settings
    SETTING_UPDATED = "✅ Setting `{setting}` updated to `{value}` - Try not to break it immediately!"
    SETTING_CRITICAL_WARNING = "⚠️ This is a critical setting! Restart the bot or everything will be fucked!"
    SETTING_INVALID = "❌ Invalid setting: {setting}. Valid settings are: {valid_settings} - Learn to read!"
    SETTING_INVALID_VALUE = "❌ Invalid value for {setting}. {reason} - Use your fucking brain!"
    SETTING_CURRENT = "Current value for `{setting}`: `{value}`"

    # Vacation mode
    VACATION_ENABLED = "✅ {name} is on vacation and excluded from chores - Must be nice to be a lazy sod!"
    VACATION_DISABLED = "✅ {name} is back! Hope you enjoyed your break, now get back to work you donkey!"
    VACATION_ENABLED_OTHER = "✅ {setter} put {name} on vacation - Lucky bastard!"
    VACATION_DISABLED_OTHER = "✅ {setter} brought {name} back from vacation - Welcome back to reality!"

    # Statistics
    STATS_HEADER = "📊 **{name}'s Stats - Let's see how shit you are** 📊"
    STATS_COMPLETED = "Actually completed: {count} chores"
    STATS_HELPED = "Helped others: {count} times - You're less useless than the rest!"
    STATS_REASSIGNED = "Had to be reassigned: {count} times"
    STATS_SKIPPED = "Skipped like a coward: {count} chores"
    STATS_COMPLETION_RATE = "Completion rate: {rate}%"
    STATS_HELPFULNESS = "Help score: {helped} extra chores! {'Actually useful!' if helped > 2 else 'Not bad!' if helped > 0 else 'Useless as usual!'}"

    # Reminders
    REMINDER_HEADER = "⏰ **REMINDER - Stop Being Lazy Fucks!** ⏰"
    REMINDER_MESSAGE = "Oi {mention}! Finish your fucking chore: **{chore}** - Or do I need to come over there?!"
    REMINDER_SETTINGS_UPDATED = "✅ Reminder settings updated - Maybe this will get your lazy arses moving!"
    REMINDER_ENABLED = "Reminders enabled for {day} at {time} - I'll be screaming at you then!"
    REMINDER_DISABLED = "Reminders disabled - You're on your own now, you muppets!"

    # Difficulty ratings
    DIFFICULTY_SET = "✅ **{chore}** difficulty set to {level}/5 - Not that any of you care!"
    DIFFICULTY_VOTE_HEADER = "🗳️ **Vote on Chore Difficulty - If you can count that high** 🗳️"
    DIFFICULTY_VOTE_INSTRUCTIONS = "React with how difficult you think **{chore}** is (though your opinion is probably worthless):"
    DIFFICULTY_VOTE_SCALE = "1️⃣ = Easy for a toddler, 5️⃣ = Might actually require effort"
    DIFFICULTY_VOTE_RESULT = "**{chore}** difficulty set to {level}/5 based on your votes - Democracy in action, you donkeys!"

    # Next week planning
    NEXT_WEEK_INCLUDED = "✅ {name} is in next week's schedule - Time to actually do some work!"
    NEXT_WEEK_EXCLUDED = "❌ {name} excluded from next week - Enjoy being useless elsewhere!"
    NEXT_WEEK_TOGGLE = "{user} changed {name}'s status for next week - Somebody's making decisions!"

    # Multiple completion messages
    TASK_COMPLETED_BY_HELPER = "✅ {mention} did **{chore}** for {assigned_mention} because apparently {assigned_mention} is too fucking incompetent! Good job covering for that useless muppet!"
    TASK_COMPLETED_ADDITIONAL = "✅ {mention} also did **{chore}**! Going above and beyond - Unlike the rest of you lazy bastards!"

    # Frequency related messages
    FREQUENCY_SET = "'{chore}' frequency set to {frequency} ({freq_text}) - Mark your calendars, if you can read!"
    CHORE_ADDED_WITH_FREQUENCY = "'{name}' chore added. Appears {freq_text} - More chances for you to fuck up!"

    ERR_CHORE_ALREADY_COMPLETED = "You already did this chore, you thick donkey!"
    ERR_ONLY_OWN_CHORE_UNAVAILABLE = "You can only mark YOUR OWN chore unavailable - Are you stupid?"
    ERR_DIFFICULTY_RANGE = "Difficulty must be 1-5, you absolute muppet!"
    ERR_FREQUENCY_MINIMUM = "Frequency must be at least 1 - Can you count?!"
    ERR_VOTE_MESSAGE_DELETED = "Vote message for **{chore}** was deleted - Who's the idiot responsible?"
    ERR_VOTE_PROCESSING = "Error processing vote for **{chore}** - Even the bot can't handle your incompetence!"
    ERR_NO_VOTES_CAST = "Nobody voted on **{chore}** - Useless, all of you!"

    # Next week planning
    NEXT_WEEK_PLANNING_TITLE = "🗓️ Next Week's Schedule Planning - Try Not to Fuck This Up"
    NEXT_WEEK_PLANNING_DESC = "Below are the flatmates for next week.\nReact with numbers to toggle who's in or out (if your brain can handle it)."
    NEXT_WEEK_STATUS_EXCLUDED = "❌ Excluded from next schedule"
    NEXT_WEEK_STATUS_INCLUDED = "✅ In next schedule"
    NEXT_WEEK_INSTRUCTIONS_TITLE = "Instructions"
    NEXT_WEEK_INSTRUCTIONS_DESC = "React with the number next to a flatmate to toggle them.\nChanges apply when schedule generates."
    NEXT_WEEK_INCLUDED_MSG = "{user} included {flatmate} in next schedule - Welcome back, donkey!"
    NEXT_WEEK_EXCLUDED_MSG = "{user} excluded {flatmate} from next schedule - Good riddance!"

    # Difficulty voting
    DIFFICULTY_VOTE_MESSAGE = "Vote on **{chore}** difficulty - Show us how useless you are:"
    DIFFICULTY_VOTE_RESULT_SUCCESS = "**{chore}** difficulty now set to {level}/5 based on {votes} votes - Democracy, you muppets!"

    # Multiple completion messages (updated)
    TASK_COMPLETED_BY_HELPER_ALT = "✅ {mention} did **{chore}** for {assigned_mention}! Thanks for picking up the slack from that lazy bastard!"
    TASK_COMPLETED_ADDITIONAL_ALT = "✅ {mention} also did **{chore}**! Above and beyond - Unlike you other useless sods!"

    # Frequency messages
    FREQUENCY_UPDATED = "'{chore}' frequency set to {frequency} ({freq_text}) - Plan accordingly, if you have a brain!"
    CHORE_ADDED_SUCCESS = "'{name}' chore added. Appears {freq_text} - More opportunities for failure!"