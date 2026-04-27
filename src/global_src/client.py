import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
load_dotenv()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")