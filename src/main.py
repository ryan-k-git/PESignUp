import atexit
import os
from pathlib import Path

from core.client import bot, TOKEN
from database import DATABASE


@atexit.register
async def clean_up():
    print("Closing connections")
    await bot.close()
    await DATABASE.close()


@bot.event
async def on_ready():
    await DATABASE.initialize()
    cogs_path = Path(__file__).parent / "cogs"
    for filename in os.listdir(cogs_path):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
    await bot.tree.sync()
    print("Successfully Ready")

if __name__ == "__main__":

    bot.run(token=TOKEN)