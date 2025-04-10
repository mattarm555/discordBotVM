import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")


# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
intents.guilds = True
intents.voice_states = True

# Bot Setup
class JengBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        
        
        self.sniped_messages = {}

    async def setup_hook(self):
        # Load all cogs from the cogs/ directory
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    
    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
        print(f"Logged in as {self.user}")
        print("Connected to:")
        print(f"Cogs Loaded: {list(bot.cogs.keys())}")
        for guild in self.guilds:
            print(f" - {guild.name} ({guild.id})")
        await self.tree.sync()
        print("Slash commands synced globally")

bot = JengBot()

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    bot.sniped_messages[message.channel.id] = {
        "content": message.content,
        "author": message.author,
        "time": message.created_at
    }



print(f"🔒 Token: {TOKEN[:5]}********")
bot.run(TOKEN)
