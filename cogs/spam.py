import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class SpamCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store active spam tasks
        self.spamming_tasks = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event that fires when the cog is loaded and ready"""
        print(f"Spam commands cog loaded. Make sure to sync commands with /sync")
    
    # === Slash Commands ===
    @app_commands.command(name="tagspam", description="Spam tag a user for fun")
    @app_commands.describe(user="The user to tag", count="Number of times to tag (max 999)")
    async def tagspam(self, interaction: discord.Interaction, user: discord.Member, count: int):
        """Spam tag a user a specified number of times"""
        if count > 999:
            await interaction.response.send_message("Bro chill 😅 Max 999 tags allowed!", ephemeral=True)
            return

        if interaction.channel.id in self.spamming_tasks:
            await interaction.response.send_message("Already tagging in this channel! Use `/stopspam` to cancel.", ephemeral=True)
            return

        await interaction.response.send_message(f"Starting to tag {user.mention} {count} times... 😈")

        async def spam_task():
            try:
                for i in range(count):
                    await interaction.channel.send(f"{user.mention} 👀 Tag {i+1}")
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                await interaction.channel.send("Spam cancelled. 😅")
            else:
                await interaction.channel.send("Done tagging! 😎")
            finally:
                self.spamming_tasks.pop(interaction.channel.id, None)

        task = asyncio.create_task(spam_task())
        self.spamming_tasks[interaction.channel.id] = task

    @app_commands.command(name="stopspam", description="Stop the ongoing spam in this channel")
    async def stopspam(self, interaction: discord.Interaction):
        """Stop any ongoing tag spam in the current channel"""
        task = self.spamming_tasks.get(interaction.channel.id)
        if task:
            task.cancel()
            await interaction.response.send_message("Stopping the spam... 🛑")
        else:
            await interaction.response.send_message("There's no active spam in this channel 😇", ephemeral=True)
    
    @app_commands.command(name="pingtest", description="Simple test command")
    async def pingtest(self, interaction: discord.Interaction):
        """Simple test command to verify slash commands are working"""
        await interaction.response.send_message("Pong! Slash commands are working!", ephemeral=True)
            
    # === Prefix Commands ===
    @commands.command(name="tagspam", help="Spam tag a user for fun")
    async def prefix_tagspam(self, ctx, user: discord.Member, count: int):
        """Spam tag a user a specified number of times (prefix version)"""
        if count > 999:
            await ctx.send("Bro chill 😅 Max 999 tags allowed!")
            return

        if ctx.channel.id in self.spamming_tasks:
            await ctx.send("Already tagging in this channel! Use `!stopspam` to cancel.")
            return

        await ctx.send(f"Starting to tag {user.mention} {count} times... 😈")

        async def spam_task():
            try:
                for i in range(count):
                    await ctx.channel.send(f"{user.mention} 👀 Tag {i+1}")
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                await ctx.channel.send("Spam cancelled. 😅")
            else:
                await ctx.channel.send("Done tagging! 😎")
            finally:
                self.spamming_tasks.pop(ctx.channel.id, None)

        task = asyncio.create_task(spam_task())
        self.spamming_tasks[ctx.channel.id] = task
        
    @commands.command(name="stopspam", help="Stop the ongoing spam in this channel")
    async def prefix_stopspam(self, ctx):
        """Stop any ongoing tag spam in the current channel (prefix version)"""
        task = self.spamming_tasks.get(ctx.channel.id)
        if task:
            task.cancel()
            await ctx.send("Stopping the spam... 🛑")
        else:
            await ctx.send("There's no active spam in this channel 😇")
    
    @commands.command(name="sync_spam", help="Sync slash commands for spam cog")
    @commands.is_owner()
    async def sync_spam(self, ctx):
        """Force synchronize slash commands with Discord"""
        await ctx.send("Syncing commands for spam cog...")
        try:
            synced = await self.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} command(s) for spam cog!")
        except Exception as e:
            await ctx.send(f"Failed to sync commands for spam cog: {e}")

async def setup(bot):
    # Add the cog to the bot
    await bot.add_cog(SpamCommands(bot))
    # Re-added the sync logic in the cog setup function.
    await bot.tree.sync()