import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

class HauntCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store active haunting tasks
        self.haunting_tasks = {}
        # List of creepy messages to send
        self.creepy_messages = [
            "I'm behind you...",
            "Did you hear that sound?",
            "I can see you...",
            "Look over your shoulder...",
            "I'm getting closer...",
            "Don't turn around...",
            "I'm in the room with you...",
            "Can you feel my presence?",
            "I'm watching you...",
            "There's nowhere to hide...",
            "The shadows are moving...",
            "Did you lock all the doors?",
            "I'll find you eventually...",
            "Your fear makes me stronger...",
            "I'm under your bed...",
            "Check your closet...",
            "I know where you live...",
            "Sweet dreams tonight...",
            "I'm just a whisper away...",
            "Are you alone right now?",
        ]
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event that fires when the cog is loaded and ready"""
        print(f"Haunt commands cog loaded. Make sure to sync commands with /sync")
    
    # === Slash Commands ===
    @app_commands.command(name="haunt", description="Haunt a user with creepy messages")
    @app_commands.describe(
        user="The user to haunt",
        minutes="How many minutes to haunt them for (max 30)"
    )
    async def haunt(self, interaction: discord.Interaction, user: discord.Member, minutes: int):
        """Haunt a user with random creepy messages for a specified duration"""
        if minutes > 30:
            await interaction.response.send_message("That's too long! Maximum haunting time is 30 minutes.", ephemeral=True)
            return

        if interaction.channel.id in self.haunting_tasks:
            await interaction.response.send_message("Already haunting in this channel! Use `/stophaunt` to end it.", ephemeral=True)
            return
            
        # Convert minutes to seconds
        duration = minutes * 60
        end_time = asyncio.get_event_loop().time() + duration

        await interaction.response.send_message(f"Starting to haunt {user.mention} for {minutes} minutes... 👻", ephemeral=False)

        async def haunt_task():
            try:
                while asyncio.get_event_loop().time() < end_time:
                    # Pick a random creepy message
                    message = random.choice(self.creepy_messages)
                    
                    # Send the message mentioning the user
                    await interaction.channel.send(f"{user.mention} {message} 👻")
                    
                    # Random delay between 15-120 seconds
                    delay = random.randint(15, 120)
                    await asyncio.sleep(delay)
            except asyncio.CancelledError:
                await interaction.channel.send(f"The haunting of {user.mention} has ended... for now. 👻")
            else:
                await interaction.channel.send(f"The haunting of {user.mention} is complete... or is it? 👻")
            finally:
                self.haunting_tasks.pop(interaction.channel.id, None)

        task = asyncio.create_task(haunt_task())
        self.haunting_tasks[interaction.channel.id] = task

    @app_commands.command(name="stophaunt", description="Stop the haunting in this channel")
    async def stophaunt(self, interaction: discord.Interaction):
        """Stop any ongoing haunting in the current channel"""
        task = self.haunting_tasks.get(interaction.channel.id)
        if task:
            task.cancel()
            await interaction.response.send_message("The haunting has been stopped... for now. 👻")
        else:
            await interaction.response.send_message("There's no active haunting in this channel.", ephemeral=True)
    
    @app_commands.command(name="sync", description="Sync slash commands")
    async def slash_sync(self, interaction: discord.Interaction):
        """Force synchronize slash commands with Discord (slash version)"""
        # Check if user is owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("Only the bot owner can use this command.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # This will register the commands globally (for all guilds)
            synced = await self.bot.tree.sync()
            await interaction.followup.send(f"Synced {len(synced)} command(s)!")
        except Exception as e:
            await interaction.followup.send(f"Failed to sync commands: {e}")
            
    # === Prefix Commands ===
    @commands.command(name="haunt", help="Haunt a user with creepy messages")
    async def prefix_haunt(self, ctx, user: discord.Member, minutes: int):
        """Haunt a user with random creepy messages for a specified duration (prefix version)"""
        if minutes > 30:
            await ctx.send("That's too long! Maximum haunting time is 30 minutes.")
            return

        if ctx.channel.id in self.haunting_tasks:
            await ctx.send("Already haunting in this channel! Use `!stophaunt` to end it.")
            return
            
        # Convert minutes to seconds
        duration = minutes * 60
        end_time = asyncio.get_event_loop().time() + duration

        await ctx.send(f"Starting to haunt {user.mention} for {minutes} minutes... 👻")

        async def haunt_task():
            try:
                while asyncio.get_event_loop().time() < end_time:
                    # Pick a random creepy message
                    message = random.choice(self.creepy_messages)
                    
                    # Send the message mentioning the user
                    await ctx.channel.send(f"{user.mention} {message} 👻")
                    
                    # Random delay between 15-120 seconds
                    delay = random.randint(15, 120)
                    await asyncio.sleep(delay)
            except asyncio.CancelledError:
                await ctx.channel.send(f"The haunting of {user.mention} has ended... for now. 👻")
            else:
                await ctx.channel.send(f"The haunting of {user.mention} is complete... or is it? 👻")
            finally:
                self.haunting_tasks.pop(ctx.channel.id, None)

        task = asyncio.create_task(haunt_task())
        self.haunting_tasks[ctx.channel.id] = task
        
    @commands.command(name="stophaunt", help="Stop the haunting in this channel")
    async def prefix_stophaunt(self, ctx):
        """Stop any ongoing haunting in the current channel (prefix version)"""
        task = self.haunting_tasks.get(ctx.channel.id)
        if task:
            task.cancel()
            await ctx.send("The haunting has been stopped... for now. 👻")
        else:
            await ctx.send("There's no active haunting in this channel.")
    
    @commands.command(name="sync", help="Sync slash commands")
    @commands.is_owner()  # Only the bot owner can use this
    async def sync(self, ctx):
        """Force synchronize slash commands with Discord"""
        await ctx.send("Syncing commands...")
        
        try:
            # This will register the commands globally (for all guilds)
            synced = await self.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} command(s)!")
        except Exception as e:
            await ctx.send(f"Failed to sync commands: {e}")

async def setup(bot):
    # Add the cog to the bot
    await bot.add_cog(HauntCommands(bot))
    # Re-added the sync logic in the cog setup function.
    await bot.tree.sync()