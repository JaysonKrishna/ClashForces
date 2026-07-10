import discord
from discord.ext import commands
import cfapi
from database import link_user, get_cf_handle

class CFLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="link")
    async def link_account(self, ctx, handle: str):
        """Links your Discord account to a Codeforces handle."""
        handle = handle.strip()
        
        # Shows "ClashForces is typing..." while waiting for the API
        async with ctx.typing():
            # Use our new centralized API core to verify the user exists
            user_data = await cfapi.fetch_user_info(handle)
            
            if user_data:
                # Codeforces returns the handle exactly as capitalized on the site
                official_handle = user_data["handle"]
                
                # Save it permanently in the SQLite database
                link_user(ctx.author.id, official_handle)
                
                await ctx.send(f"✅ Successfully linked **{ctx.author.name}** to Codeforces handle: `{official_handle}`")
            else:
                await ctx.send(f"❌ Could not find a Codeforces user named `{handle}`. Please check the spelling.")

    @commands.command(name="profile")
    async def show_profile(self, ctx, member: discord.Member = None):
        """Shows the linked Codeforces handle for yourself or another user."""
        # If no user is mentioned, check the person who sent the command
        target = member or ctx.author
        
        # Check the database
        handle = get_cf_handle(target.id)
        
        if handle:
            await ctx.send(f"👤 {target.mention} is currently linked to: `{handle}`")
        else:
            await ctx.send(f"❓ {target.mention} has not linked an account yet. Use `!link <handle>` to get started!")

# This registers the extension with your main bot.py file
async def setup(bot):
    await bot.add_cog(CFLink(bot))