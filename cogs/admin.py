import discord
from discord import app_commands
from discord.ext import commands
from loader import Loader

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        """Check if the user is the bot owner"""
        return await self.bot.is_owner(ctx.author)
    
    # === Slash Commands ===
    @app_commands.command(name="reload", description="Reload bot extensions")
    @app_commands.describe(extension="The extension to reload (leave blank for all)")
    async def slash_reload(self, interaction: discord.Interaction, extension: str = None):
        """Reload bot extensions"""
        # Check if user is owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("Only the bot owner can use this command.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        if extension:
            success, message = await Loader.reload_extension(self.bot, extension)
            await interaction.followup.send(message, ephemeral=True)
        else:
            results = await Loader.reload_all(self.bot)
            message = "\n".join(results)
            await interaction.followup.send(f"Reload results:\n```\n{message}\n```", ephemeral=True)
    
    # === Prefix Commands ===
    @commands.command(name="reload", help="Reload bot extensions")
    async def prefix_reload(self, ctx, extension=None):
        """Reload bot extensions"""
        if extension:
            success, message = await Loader.reload_extension(self.bot, extension)
            await ctx.send(message)
        else:
            results = await Loader.reload_all(self.bot)
            message = "\n".join(results)
            await ctx.send(f"Reload results:\n```\n{message}\n```")
    
    @commands.command(name="shutdown", help="Shutdown the bot")
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        await ctx.send("Shutting down...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Admin(bot))