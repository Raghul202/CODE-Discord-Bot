import asyncio
import signal
import sys
import atexit
from config import Config
from loader import Loader

import discord
from discord.ext import commands

# Professional shutdown message function
def display_shutdown_message():
    print("\n")
    print("┌─────────────────────────────────────────────────┐")
    print("│                                                 │")
    print("│               SYSTEM NOTIFICATION               │")
    print("│                                                 │")
    print("│          Discord Bot Shutdown Complete          │")
    print("│                                                 │")
    print("│         All connections closed successfully     │")
    print("│                                                 │")
    print("└─────────────────────────────────────────────────┘")
    print("\n")

# Register shutdown message
atexit.register(display_shutdown_message)

# Clean shutdown signal handler
def handle_exit_signal(sig, frame):
    print("\nInitiating shutdown sequence...")
    sys.exit(0)

# Register exit signals
signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

class Bot(commands.Bot):
    def __init__(self, config):
        self.config = config
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=self.config.prefix,
            intents=intents,
            owner_id=self.config.owner_id,
            help_command=None
        )
        
    # In main.py, modify the setup_hook method in the Bot class:

async def setup_hook(self):
    print("[DEBUG] Starting to load all extensions and events...")
    await Loader.load_all(self)
    print("[DEBUG] Finished loading extensions and events.")

    print("[DEBUG] Attempting to sync slash commands globally...")
    try:
        # Sync commands globally
        synced_global = await self.tree.sync()
        print(f"[DEBUG] Synced {len(synced_global)} global slash command(s) successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to sync slash commands globally: {e}")

    print(f"Logged in as {self.user} (ID: {self.user.id})")
    print(f"Bot is ready to use with prefix: {self.config.prefix}")
async def main():
    # Load configuration (it will handle creating config files if needed)
    config = Config()
    
    # Create bot instance
    bot = Bot(config)
    
    # Run the bot
    token = config.token
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("Invalid token. Please check your token in data/token.txt")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())