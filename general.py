import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commands", aliases=["cmds"])
    async def show_commands(self, ctx):
        """Displays a clean list of all available bot commands."""
        
        # Create a visually appealing embed
        embed = discord.Embed(
            title="📜 ClashForces Command List",
            description="Here is everything you can do with the bot:",
            color=discord.Color.blue()
        )
        
        # Category 1: Accounts
        embed.add_field(
            name="👤 Profile & Accounts",
            value=(
                "`!link <handle>` - Link your Discord to your Codeforces account.\n"
                "`!profile [@user]` - See the linked Codeforces handle for yourself or a friend."
            ),
            inline=False
        )
        
        # Category 2: Matchmaking
        embed.add_field(
            name="⚔️ Matchmaking (1v1)",
            value=(
                "`!duel <@user> [rating]` - Challenge someone to a race (default is 1200).\n"
                "`!accept` - Type this within 2 minutes to accept an incoming challenge.\n"
                "`!end` - Propose a mutual cancellation of an ongoing duel."
            ),
            inline=False
        )
        
        embed.set_footer(text="May the fastest coder win!")
        
        # Send it to the chat
        await ctx.send(embed=embed)

# Register the extension
async def setup(bot):
    await bot.add_cog(General(bot))