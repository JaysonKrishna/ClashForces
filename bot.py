import discord
from discord.ext import commands
import asyncio
import aiohttp
from database import init_db
import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name}")
    print("ClashForces bot is online and ready!")
    print("------------------------------------")

async def load_extensions():
    # Load the specific modules from the current directory
    initial_extensions = ['cflink', 'teams', 'duel', 'general']
    
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension: {extension}.py")
        except Exception as e:
            print(f"Failed to load extension {extension}.py: {e}")

async def main():
    init_db()
    print("Database initialized successfully.")
    
    # We must wrap the startup in the async session!
    async with aiohttp.ClientSession() as session:
        bot.session = session
        await load_extensions()
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())