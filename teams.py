import discord
from discord.ext import commands, tasks

class MatchTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Start the background loop when this module loads
        self.live_match_checker.start()

    def cog_unload(self):
        self.live_match_checker.cancel()

    # This loop runs every 10 seconds asynchronously to avoid rate limits
    @tasks.loop(seconds=10.0)
    async def live_match_checker(self):
        # Later, we will pull these handles dynamically from the SQLite database
        handle = "tourist" 
        url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=1"

        try:
            async with self.bot.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data["status"] == "OK" and len(data["result"]) > 0:
                        latest_sub = data["result"][0]
                        problem_name = latest_sub["problem"]["name"]
                        verdict = latest_sub.get("verdict", "TESTING")
                        
                        # In the final version, we will track submission IDs to prevent spam
                        print(f"[LIVE TRACKER] {handle} submitted {problem_name}: {verdict}")
        except Exception as e:
            print(f"Tracking error: {e}")

    @live_match_checker.before_loop
    async def before_checker(self):
        # Wait until the bot is fully logged in before hitting the API
        await self.bot.wait_until_ready()

# This function is required by Discord.py to register the Cog
async def setup(bot):
    await bot.add_cog(MatchTracker(bot))