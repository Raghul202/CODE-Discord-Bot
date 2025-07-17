def setup(bot):
    @bot.event
    async def on_message(message):
        """Event called when a message is received"""
        # Prevent the bot from responding to itself
        if message.author == bot.user:
            return
            
        # Process commands (required for prefix commands to work)
        await bot.process_commands(message)
        
        # Custom message handling logic can go here...
        if bot.config.debug and message.content.lower() == "debug":
            await message.channel.send("Debug mode is enabled!")