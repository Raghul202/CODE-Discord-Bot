import discord

def setup(bot):
    @bot.event
    async def on_ready():
        """Event called when the bot is ready"""
        # Set the bot's status
        activity = discord.Game(name=bot.config.status)
        await bot.change_presence(activity=activity)
        
        # Print some information
        print(f"{'-' * 30}")
        print(f"Bot ready as: {bot.user} (ID: {bot.user.id})")
        print(f"Using command prefix: {bot.config.prefix}")
        print(f"Owner ID: {bot.config.owner_id}")
        print(f"Status: {bot.config.status}")
        print(f"Debug mode: {bot.config.debug}")
        print(f"{'-' * 30}")