# Codestyle for discord-chores-bot

This file is for AI agents working on this codebase. Follow these rules strictly.

---

## Language & Runtime

Python 3.10. discord.py 2.3.2. All async/await patterns. Docker containerized.

---

## Project Structure

src/cogs/ — discord cog classes, one file per feature group (chores, admin, help)
src/utils/ — pure logic classes with no discord dependency where possible (config_manager, schedule_manager, connection_handler, strings)
src/main.py — bot bootstrap only, no business logic
data/ — runtime json files, never commit these
scripts/ — bash maintenance scripts

New features go in a cog if they need discord interaction. Logic that can be tested without discord goes in utils.

---

## Naming

Classes: PascalCase. ChoresCog, ScheduleManager, ConfigManager.
Functions and variables: snake_case. get_active_flatmates, flatmate_name, discord_id.
Constants: UPPER_SNAKE_CASE only in strings.py. Never scatter magic strings through cogs.
Logger: always named 'chores-bot'. Never create new logger names.

```python
logger = logging.getLogger('chores-bot')
```

Avoid abbreviations. flatmate not fm. assignments not assgn. discord_id not did.

---

## Functions

One responsibility per function. If a function does two things, split it.

Return early to avoid nesting. Prefer:

```python
if not flatmate:
    return None
# rest of logic here
```

over deeply nested if/else blocks.

Functions that touch discord (send messages, fetch channels) stay in cogs.
Functions that transform data or read/write files stay in utils.

Keep cog command handlers thin — they call into utils and format responses. Business logic does not live in command handlers.

---

## Comments

Comment the why, never the what. If the code is readable, don't comment it.

```python
# using rotation_index per chore so each chore advances independently
self.schedule_data["rotation_indices"][chore] = (rotation_index + 1) % len(flatmates)

# skip if bot's own reaction to avoid infinite loops
if payload.user_id == self.bot.user.id:
    return
```

Never comment out dead code. Delete it.
lowercase first letter on all comments.

---

## Logging

Every significant action gets logged. Use the right level.

logger.debug — internal state, variable values, "found X flatmates"
logger.info — user-triggered actions, schedule posts, completed chores
logger.warning — unexpected but recoverable states, missing optional data
logger.error — failures that affect functionality, with exc_info=True for exceptions

Log at function entry for anything non-trivial:
```python
logger.info(f"Assigning chore '{chore}' to {flatmate_name}")
```

Never log tokens, discord IDs in sensitive contexts, or raw config dumps.

---

## Error Handling

Always handle FileNotFoundError and json.JSONDecodeError when reading files.
Always use exc_info=True when logging exceptions so the traceback is captured.
Never silently pass on exceptions in commands — at minimum log and send a user-facing error message.

```python
except Exception as e:
    logger.error(f"Failed to load schedule data: {e}", exc_info=True)
    return self._initialize_default_data()
```

Discord interactions that might time out should defer first:
```python
await interaction.response.defer()
```

---

## Config & State

All config reads go through ConfigManager. Never open config.json directly in cogs.
All schedule state reads/writes go through ScheduleManager. Never touch schedule_data.json directly.
After any mutation to config or schedule data, call the appropriate save method immediately.

---

## Strings

All user-facing strings live in src/utils/strings.py as class attributes on BotStrings.
Never hardcode message text in cogs or utils.
Format with .format() at the call site:

```python
await channel.send(BotStrings.TASK_ASSIGNMENT.format(mention=f"<@{discord_id}>", chore=chore))
```

---

## Discord Patterns

Always check if a fetched resource is None before using it (channels, users, messages).
Use followup.send after defer, never response.send_message.
Add reactions with await, never fire and forget.
Cache message IDs in self.message_cache when you need to handle reactions later.

---

## What Not To Do

No business logic in main.py.
No direct file I/O outside of ConfigManager and ScheduleManager.
No hardcoded strings outside of strings.py.
No new logger names — always 'chores-bot'.
No unused imports.
No commented-out code blocks.
No TODO comments — either fix it or open a task.