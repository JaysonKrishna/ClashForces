import discord
from discord.ext import commands, tasks
import asyncio
import random
import time
import cfapi
from database import get_cf_handle

class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Memory dictionary to track who is dueling in which channel
        self.active_duels = {}
        # Start the referee loop as soon as the module loads
        self.duel_referee.start()

    def cog_unload(self):
        # Stop the referee if the module is unloaded
        self.duel_referee.cancel()

    @commands.command(name="duel")
    async def initiate_duel(self, ctx, opponent: discord.Member, rating: int = 1200):
        """Challenge another user to a Codeforces duel at a specific rating."""
        
        # 1. Check if a duel is already happening here
        if ctx.channel.id in self.active_duels:
            return await ctx.send("❌ There is already an active duel in this channel! Wait for it to finish.")

        # 2. Database Checks
        challenger_handle = get_cf_handle(ctx.author.id)
        opponent_handle = get_cf_handle(opponent.id)

        if not challenger_handle:
            return await ctx.send("❌ You need to link your Codeforces account first! Use `!link <handle>`")
        if not opponent_handle:
            return await ctx.send(f"❌ {opponent.mention} hasn't linked their Codeforces account yet!")
        if ctx.author == opponent:
            return await ctx.send("❌ You cannot duel yourself!")

        # 3. The Challenge
        await ctx.send(
            f"⚔️ {opponent.mention}, you have been challenged to a **{rating}-rated** duel by {ctx.author.mention}!\n"
            f"Type `!accept` in this channel within **2 minutes** to begin."
        )

        def check(message):
            return message.author == opponent and message.channel == ctx.channel and message.content.lower() == "!accept"

        # 4. Wait for the handshake
        try:
            await self.bot.wait_for('message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            return await ctx.send(f"⌛ {opponent.mention} didn't respond within 2 minutes. The duel has been cancelled.")

        # 5. Fetching the Problem
        msg = await ctx.send(f"✅ Duel accepted! Fetching a {rating}-rated problem from Codeforces...")

        url = "https://codeforces.com/api/problemset.problems"
        async with self.bot.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data["status"] == "OK":
                    problems = [p for p in data["result"]["problems"] if p.get("rating") == rating]
                    
                    if not problems:
                        return await msg.edit(content=f"❌ Could not find any problems with a rating of {rating}.")

                    problem = random.choice(problems)
                    contest_id = problem["contestId"]
                    index = problem["index"]
                    name = problem["name"]
                    
                    problem_link = f"https://codeforces.com/contest/{contest_id}/problem/{index}"

                    embed = discord.Embed(
                        title="⚔️ MATCH STARTED ⚔️",
                        description=f"**[{name}]({problem_link})**\nRating: {rating}",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Challenger", value=f"{ctx.author.name}\n(`{challenger_handle}`)", inline=True)
                    embed.add_field(name="Opponent", value=f"{opponent.name}\n(`{opponent_handle}`)", inline=True)
                    embed.set_footer(text="The referee is watching. First to get an 'Accepted' verdict wins!")

                    await msg.edit(content=None, embed=embed)
                    
                    # 6. REGISTER THE DUEL FOR THE REFEREE LOOP
                    self.active_duels[ctx.channel.id] = {
                        "p1_id": ctx.author.id,
                        "p1_handle": challenger_handle,
                        "p2_id": opponent.id,
                        "p2_handle": opponent_handle,
                        "target_problem": name,
                        "start_time": int(time.time())
                    }
            else:
                await msg.edit(content="❌ Failed to connect to the Codeforces API.")



    @commands.command(name="end")
    async def mutually_end_duel(self, ctx):
        """Propose to mutually cancel an ongoing duel."""
        
        # 1. Check if a duel is even happening here
        if ctx.channel.id not in self.active_duels:
            return await ctx.send("❌ There is no active duel in this channel to end.")

        duel = self.active_duels[ctx.channel.id]
        
        # 2. Make sure the person typing !end is actually playing
        if ctx.author.id not in [duel["p1_id"], duel["p2_id"]]:
            return await ctx.send("❌ You are not participating in the current duel.")

        # 3. Figure out who the opponent is
        if ctx.author.id == duel["p1_id"]:
            opponent_id = duel["p2_id"]
        else:
            opponent_id = duel["p1_id"]

        # 4. Ask for confirmation
        await ctx.send(
            f"⚠️ <@{opponent_id}>, {ctx.author.mention} wants to mutually end the match early.\n"
            f"Type `!end` within **60 seconds** to agree and cancel the duel."
        )

        # 5. Wait for the opponent to type !end
        def check(message):
            return message.author.id == opponent_id and message.channel == ctx.channel and message.content.lower() == "!end"

        try:
            await self.bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send(f"⌛ <@{opponent_id}> didn't respond in time. The duel continues!")

        # 6. Safety Check & Cancellation
        # We check if it's still in the dictionary just in case someone solved it 
        # while the bot was waiting for the !end confirmation!
        if ctx.channel.id in self.active_duels:
            del self.active_duels[ctx.channel.id]
            await ctx.send("🛑 **Duel Mutually Cancelled.** The referee has stopped watching.")

    # ==========================================
    # THE LIVE REFEREE ENGINE
    # ==========================================
    @tasks.loop(seconds=10.0)
    async def duel_referee(self):
        """Checks Codeforces every 10 seconds to see if anyone solved their duel problem."""
        
        # We iterate over a copy of the dictionary so we can delete finished matches safely
        for channel_id, duel in list(self.active_duels.items()):
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            try:
                # --- Check Challenger (Player 1) ---
                p1_subs = await cfapi.fetch_recent_submissions(duel["p1_handle"], count=1)
                if p1_subs:
                    latest_p1 = p1_subs[0]
                    
                    # Ensure they solved the right problem, got an OK, AND submitted it AFTER the duel started
                    if (latest_p1["problem"]["name"] == duel["target_problem"] and 
                        latest_p1.get("verdict") == "OK" and 
                        latest_p1["creationTimeSeconds"] >= duel["start_time"]):
                        
                        # Calculate the exact time taken
                        time_taken = latest_p1["creationTimeSeconds"] - duel["start_time"]
                        minutes, seconds = divmod(time_taken, 60)
                        time_string = f"{minutes}m {seconds}s"
                        
                        await channel.send(f"🏆 🏁 **DUEL OVER!** 🏁 🏆\n<@{duel['p1_id']}> (`{duel['p1_handle']}`) solved **{duel['target_problem']}** first!\n⏱️ **Time taken:** {time_string}")
                        del self.active_duels[channel_id]
                        continue

                await asyncio.sleep(1.5)

                # --- Check Opponent (Player 2) ---
                p2_subs = await cfapi.fetch_recent_submissions(duel["p2_handle"], count=1)
                if p2_subs:
                    latest_p2 = p2_subs[0]
                    
                    if (latest_p2["problem"]["name"] == duel["target_problem"] and 
                        latest_p2.get("verdict") == "OK" and 
                        latest_p2["creationTimeSeconds"] >= duel["start_time"]):
                        
                        time_taken = latest_p2["creationTimeSeconds"] - duel["start_time"]
                        minutes, seconds = divmod(time_taken, 60)
                        time_string = f"{minutes}m {seconds}s"
                        
                        await channel.send(f"🏆 🏁 **DUEL OVER!** 🏁 🏆\n<@{duel['p2_id']}> (`{duel['p2_handle']}`) solved **{duel['target_problem']}** first!\n⏱️ **Time taken:** {time_string}")
                        del self.active_duels[channel_id]
                        continue

            except Exception as e:
                print(f"Error checking duel in channel {channel_id}: {e}")

async def setup(bot):
    await bot.add_cog(Duel(bot))