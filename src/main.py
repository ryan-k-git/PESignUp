import atexit
import os

from src.global_src.client import bot, TOKEN
from src.global_src.db import DATABASE


@atexit.register
async def clean_up():
    print("Closing connections")
    await bot.close()
    await DATABASE.con.close()


@bot.event
async def on_ready():
    await DATABASE.initialize()
    cogs_path = "src/core/cogs"
    for filename in os.listdir(cogs_path):
        try:
            if filename.endswith(".py") and filename != "__init__.py":
                cog_name = f"src.core.cogs.{filename[:-3]}"
                await bot.load_extension(cog_name)
                print(f"Loaded {filename[:-3]}")
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
    await bot.tree.sync()
    print("Successfully Ready")

if __name__ == "__main__":

    bot.run(token=TOKEN)