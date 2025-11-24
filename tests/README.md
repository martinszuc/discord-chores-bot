# Chores Bot - Test Suite

---

## Test Scenarios

### 1. **Everyone Completes** (10 weeks)
- All flatmates complete assigned chores
- Tests basic rotation and fairness
- Expected: Priorities stay balanced (145-160 range)

### 2. **Half On Vacation** (10 weeks)
- 3 flatmates on vacation, 3 active
- All active flatmates complete their chores
- Expected: Active flatmates alternate, priorities 175+

### 3. **Nobody Completes** (10 weeks)
- Everyone skips (chores get reassigned)
- Tests skip penalty and reassignment logic
- Expected: Priorities drop below 50

### 4. **Mixed Behavior** (15 weeks)
- Group 1: Always complete (Dominik, Roman)
- Group 2: Always skip (Jakub, Denis)
- Group 3: On vacation (Filip, Martin)
- Expected Week 15:
  - Completers: Priority 215-225, get 1 chore
  - Skippers: Priority 90-100, get 2-3 chores

### 5. **Random Chaos** (15 weeks)
- Random mix: 40% complete, 30% help, 20% skip, 10% late
- Tests "helped" stat bonus and real-world randomness
- Expected: Helpers emerge with 160+ priority

---

## What Gets Tested

✅ Priority calculation (helped, completed, skipped, reassigned)  
✅ Chore assignment fairness  
✅ Vacation handling  
✅ "Helped" stat tracking  
✅ Skip penalties  
✅ Multi-week progression  

---

## Output Format

Each week shows:
- **Priorities**: Score breakdown (C=completed, H=helped, S=skipped, R=reassigned)
- **Assignments**: Who gets which chores
- **Actions**: What happened (completed ✅, skipped ❌, helped 🦸)
- **Final Stats**: Complete table at the end

---

## Priority Formula

```
priority = 100
         + (helped × 8)        # Heavy reward for helping
         + (completed × 3)     # Moderate reward for completing
         - (skipped × 15)      # Heavy penalty for skipping
         - (reassigned × 5)    # Moderate penalty for reassignment
```

---

## Notes

- Test data is isolated (doesn't affect production)
- Temp files auto-cleanup after each test
- Press Enter between tests to review results
- Color-coded output (green=high priority, red=low priority)