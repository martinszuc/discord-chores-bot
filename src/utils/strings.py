"""
Centralized string repository for Discord Chores Bot - Hungarian Style, tesó!
All user-facing messages should be defined here for easy customization.
Csináljátok meg a házimunkát és ne picsázzatok!
"""


class BotStrings:
    # General messages
    SCHEDULE_HEADER = "🔔 **Heti HÁZI Beosztás - Ideje kitakarítani!** 🔔"
    TASK_ASSIGNMENT = "Szia {mention}! A te feladatod erre a hétre: **{chore}** - Csináld meg, haver!"
    TASK_COMPLETED = "✅ Respect {mention}! Megcsináltad a feladatod: **{chore}** - Király munka!"
    TASK_COMPLETED_FOR_OTHER = "✅ A kutyafáját! {helper_mention} megcsinálta a **{chore}** feladatot {assignee_mention} helyett! Igazi hős vagy! 🦸"
    TASK_UNAVAILABLE = "❌ {mention} nem tudja megcsinálni a feladatát ezen a héten, világos?"
    TASK_REASSIGNED = "**{chore}** most {mention} fogja megcsinálni - új terv, tesó!"
    TASK_REASSIGNED_FULL = "{original_mention} nem bírja megcsinálni.\n**{chore}** átadva {new_mention}-nak/nek - sok sikert!"

    # Usage instructions
    REACTION_INSTRUCTIONS = (
        "**Hogyan reagálj, haver:**\n"
        "✅ - Jelöld meg késznek amikor befejezted\n"
        "❌ - Szólj ha nem tudod megcsinálni ezen a héten (akkor átadjuk másnak)"
    )

    # Command responses
    CMD_NEW_SCHEDULE = "Új házi beosztás felkerült! Itt az idő dolgozni!"
    CMD_NO_SCHEDULE = "Még nincs házi beosztás felállítva, tesó. Használd a `/chores next` parancsot hogy csinálj egyet."
    CMD_RESET_SCHEDULE = "Beosztás visszaállítva! Tiszta lappal indulunk!"

    # Error messages
    ERR_NO_ASSIGNMENTS = "Nincsenek házi feladatok beosztva, haver."
    ERR_NO_FLATMATE_CHORE = "Nincs neked házi feladat erre a hétre - szerencsés vagy!"
    ERR_REASSIGN_FAILED = "Nem sikerült átadni a feladatot: {chore} - valami nem működik"
    ERR_CHANNEL_NOT_FOUND = "Házi csatorna nem található, tesó: {channel_id}"
    ERR_NO_ELIGIBLE_FLATMATES = "Senki sem elérhető hogy átvállalja ezt a feladatot, világos?"
    ERR_NEXT_WEEK_NO_ACTIVE = "Nincsenek aktív lakótársak a következő heti beosztáshoz - hol van mindenki?"
    ERR_NEXT_WEEK_INVALID_SELECTION = "Ez a választás nem működik. Próbáld újra, haver."

    # Embed titles and fields
    EMBED_SCHEDULE_TITLE = "📋 Heti Házi Beosztás - Takarítsunk!"
    EMBED_SCHEDULE_FOOTER = "Utolsó frissítés ideje"
    EMBED_TASK_ASSIGNED = "🧹 Beosztva: {mention} - Most te következel!"
    EMBED_HOW_TO_RESPOND = "Hogyan reagálj, világos"
    EMBED_REACTIONS_GUIDE = (
        "✅ - Kész van!\n"
        "❌ - Nem tudom megcsinálni ezen a héten (találunk mást)"
    )

    # Admin messages
    ADMIN_CONFIG_RELOADED = "✅ Konfiguráció sikeresen újratöltve - minden rendben!"
    ADMIN_CONFIG_FAILED = "❌ Konfiguráció újratöltése sikertelen: {error} - valami nem jó"
    ADMIN_TEST_NOTIFICATION = "🔔 **TESZT ÉRTESÍTÉS - Csak tesztelünk, haver!** 🔔"

    # Flatmate management
    FLATMATE_ADDED = "Lakótárs sikeresen hozzáadva - üdv a takarító csapatban!"
    FLATMATE_EXISTS = "Ezzel a névvel már van lakótárs a rendszerben"
    FLATMATE_ID_EXISTS = "Ezzel a Discord ID-vel már van lakótárs regisztrálva"
    FLATMATE_REMOVED = "Lakótárs sikeresen eltávolítva - már nincs itt"
    FLATMATE_NOT_FOUND = "Nem találom ezt a lakótársat sehol"

    # Chore management
    CHORE_ADDED = "Házi feladat sikeresen hozzáadva - több munka mindenkinek!"
    CHORE_EXISTS = "Ez a házi feladat már benne van a listában"
    CHORE_REMOVED = "Házi feladat sikeresen eltávolítva - eggyel kevesebb dolog"
    CHORE_NOT_FOUND = "Nem találom ezt a házit sehol"

    # Settings
    SETTING_UPDATED = "✅ Beállítás `{setting}` frissítve erre: `{value}` - szuper!"
    SETTING_CRITICAL_WARNING = "⚠️ Ez egy kritikus beállítás, világos? Fontold meg a bot újraindítását hogy a változások életbe lépjenek."
    SETTING_INVALID = "❌ Érvénytelen beállítás: {setting}. Érvényes beállítások: {valid_settings}"
    SETTING_INVALID_VALUE = "❌ Érvénytelen érték ehhez: {setting}. {reason} - próbáld újra, haver"
    SETTING_CURRENT = "Jelenlegi érték ehhez: `{setting}`: `{value}`"

    # Vacation mode
    VACATION_ENABLED = "✅ {name} most szabadságon van és ki van zárva a beosztásból - élvezd a szünetet!"
    VACATION_DISABLED = "✅ {name} visszatért a beosztásba! Remélem jól pihentél!"
    VACATION_ENABLED_OTHER = "✅ {setter} szabadságra tette {name}-t. Ki van zárva a beosztásból."
    VACATION_DISABLED_OTHER = "✅ {setter} visszahozta {name}-t a szabadságról. Üdv vissza a melóban!"

    # Statistics
    STATS_HEADER = "📊 **{name} Statisztikái - Hogy teljesít** 📊"
    STATS_COMPLETED = "Befejezett (saját): {count} házi"
    STATS_HELPED = "Segített másoknak: {count} házi - király vagy! 🦸"
    STATS_REASSIGNED = "Átadva neki: {count} házi"
    STATS_SKIPPED = "Kihagyott: {count} házi"
    STATS_COMPLETION_RATE = "Teljesítési arány: {rate}%"
    STATS_HELPFULNESS = "Segítőkészség: {helped} extra házi! {'Legenda vagy! 🌟' if helped > 2 else 'Respect!' if helped > 0 else 'Segíts másoknak is!'}"

    # Reminders
    REMINDER_HEADER = "⏰ **Házi Emlékeztető - Ne felejtsd el!** ⏰"
    REMINDER_MESSAGE = "Hé {mention}! Ne felejtsd el befejezni a házid: **{chore}** - itt az idő dolgozni!"
    REMINDER_SETTINGS_UPDATED = "✅ Emlékeztető beállítások sikeresen frissítve - figyelni fogunk rád!"
    REMINDER_ENABLED = "Emlékeztetők most engedélyezve vannak {day}-en/án {time}-kor - nem hagyjuk hogy elfelejtsd!"
    REMINDER_DISABLED = "Emlékeztetők most letiltva - most már egyedül vagy, haver."

    # Difficulty ratings
    DIFFICULTY_SET = "✅ **{chore}** nehézsége beállítva {level}/5-re - tudd mibe mész bele!"
    DIFFICULTY_VOTE_HEADER = "🗳️ **Szavazz a házi nehézségére - Mondd el!** 🗳️"
    DIFFICULTY_VOTE_INSTRUCTIONS = "Reagálj azzal a számmal ami mutatja mennyire nehéznek gondolod a **{chore}**-t:"
    DIFFICULTY_VOTE_SCALE = "1️⃣ = Könnyű mint a vasárnap reggeli, 5️⃣ = Keményebb mint a beton!"
    DIFFICULTY_VOTE_RESULT = "A **{chore}** nehézsége beállítva {level}/5-re mindenki szavazata alapján - demokrácia működik!"

    # Next week planning
    NEXT_WEEK_INCLUDED = "✅ {name} benne van a következő házi beosztásban - itt az idő dolgozni!"
    NEXT_WEEK_EXCLUDED = "❌ {name} ki van zárva a következő házi beosztásból - élvezd a szünetet!"
    NEXT_WEEK_TOGGLE = "{user} átváltotta {name} szerepeltetését a következő házi beosztásban - változtatás!"

    # Multiple completion messages
    TASK_COMPLETED_BY_HELPER = "✅ Respect {helper_mention}! Megcsinálta a **{chore}** feladatot ami {assignee_mention}-nak/nek volt beosztva! Köszönjük hogy tisztán tartod a lakást! 🦸"
    TASK_COMPLETED_ADDITIONAL = "✅ {mention} szintén megcsinálta a **{chore}** feladatot! Köszönjük hogy többet tettél! 🙌"

    # Frequency related messages
    FREQUENCY_SET = "'{chore}' gyakorisága beállítva {frequency}-re ({freq_text}) - tervezd meg rendesen!"
    CHORE_ADDED_WITH_FREQUENCY = "'{name}' házi feladat sikeresen hozzáadva. Meg fog jelenni {freq_text} - nem felejtjük el!"

    ERR_CHORE_ALREADY_COMPLETED = "Már megcsináltad ezt a házit, haver."
    ERR_ONLY_OWN_CHORE_UNAVAILABLE = "Csak a saját házid tudod elérhetetlennek jelölni, világos?"
    ERR_DIFFICULTY_RANGE = "A nehézség 1 és 5 között kell legyen, tesó."
    ERR_FREQUENCY_MINIMUM = "A gyakoriság legalább 1 kell legyen, haver."
    ERR_VOTE_MESSAGE_DELETED = "A szavazási üzenet a **{chore}**-hoz törölve lett, világos."
    ERR_VOTE_PROCESSING = "Valami baj van a szavazás feldolgozásával a **{chore}**-nál, haver."
    ERR_NO_VOTES_CAST = "Senki sem szavazott a **{chore}**-ra - hol van mindenki?"

    # Next week planning
    NEXT_WEEK_PLANNING_TITLE = "🗓️ Következő heti házi beosztás tervezése - Tervezz holnapra!"
    NEXT_WEEK_PLANNING_DESC = "Alább a lakótársak akik benne lesznek a következő heti házi beosztásban.\nReagálj a lakótárs melletti számmal hogy átváltsd a szerepeltetését/kizárását."
    NEXT_WEEK_STATUS_EXCLUDED = "❌ Kizárva a következő beosztásból"
    NEXT_WEEK_STATUS_INCLUDED = "✅ Benne van a következő beosztásban"
    NEXT_WEEK_INSTRUCTIONS_TITLE = "Útmutató"
    NEXT_WEEK_INSTRUCTIONS_DESC = "Reagálj a lakótárs melletti számmal hogy átváltsd a szerepeltetését/kizárását.\nA változások a következő beosztás generálásnál lépnek életbe."
    NEXT_WEEK_INCLUDED_MSG = "{user} bevette {flatmate}-t a következő házi beosztásba - üdv vissza!"
    NEXT_WEEK_EXCLUDED_MSG = "{user} kizárta {flatmate}-t a következő házi beosztásból - pihenj egy kicsit!"

    # Difficulty voting
    DIFFICULTY_VOTE_MESSAGE = "Szavazz a **{chore}** nehézségére - mondd el mennyire nehéz:"
    DIFFICULTY_VOTE_RESULT_SUCCESS = "A **{chore}** nehézsége most {level}/5-re van állítva {votes} szavazat alapján - demokrácia működik!"

    # Multiple completion messages (updated)
    TASK_COMPLETED_BY_HELPER_ALT = "✅ Respect {mention}! Megcsinálta a **{chore}** feladatot ami {assigned_mention}-nak/nek volt kiosztva! Köszönjük hogy tisztán tartod a lakást! 🦸"
    TASK_COMPLETED_ADDITIONAL_ALT = "✅ {mention} szintén megcsinálta a **{chore}** feladatot! Köszönjük hogy többet tettél! 🙌"

    # Frequency messages
    FREQUENCY_UPDATED = "'{chore}' gyakorisága beállítva {frequency}-re ({freq_text}) - tervezd meg jól!"
    CHORE_ADDED_SUCCESS = "'{name}' házi feladat sikeresen hozzáadva. Meg fog jelenni {freq_text} - nem felejtjük el!"