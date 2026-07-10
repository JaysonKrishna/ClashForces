# ⚔️ ClashForces Bot

A custom Discord bot designed to bring competitive programming directly into your Discord server. Built with Python and `discord.py`, this bot connects to the official Codeforces API to track live problem-solving and host 1v1 coding duels.

## ✨ Features
* **Account Linking:** Securely link your Discord account to your Codeforces handle using an SQLite database.
* **1v1 Duels (`!duel`):** Challenge server members to a race on a random Codeforces problem at a specific rating. 
* **Live Referee Tracking:** The bot runs an asynchronous background loop checking Codeforces every 15 seconds. It automatically detects when a player gets an "Accepted" verdict, calculates the exact time taken, and crowns the winner.
* **Mutual Cancellation:** Safely cancel an ongoing duel if a problem is too difficult using the `!end` handshake.

## 🛠️ Tech Stack
* Python 3.12
* `discord.py` (Bot Framework)
* `aiohttp` (Asynchronous API Requests)
* `sqlite3` (Database)

## 📜 Commands
* `!link <handle>` - Link your Codeforces account.
* `!profile [@user]` - View linked Codeforces handles.
* `!duel <@user> [rating]` - Start a 1v1 race.
* `!accept` - Accept an incoming challenge (2-minute timeout).
* `!end` - Propose to cancel an active duel.
* `!commands` - Display the help menu.