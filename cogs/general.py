import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # === Slash Commands ===
    @app_commands.command(name="ping", description="Check the bot's latency")
    async def slash_ping(self, interaction: discord.Interaction):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency: {latency}ms")
    
    @app_commands.command(name="info", description="Get information about the bot")
    async def slash_info(self, interaction: discord.Interaction):
        """Get information about the bot"""
        embed = discord.Embed(
            title="Bot Information",
            description="A modular Discord bot using Pycord",
            color=discord.Color.blue()
        )
        embed.add_field(name="Owner", value=f"<@{self.bot.owner_id}>", inline=True)
        embed.add_field(name="Prefix", value=self.bot.command_prefix, inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.set_footer(text="Made with Pycord")
        
        await interaction.response.send_message(embed=embed)
    
    # === Prefix Commands ===
    @commands.command(name="ping", help="Check the bot's latency")
    async def prefix_ping(self, ctx):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency}ms")
    
    @commands.command(name="info", help="Get information about the bot")
    async def prefix_info(self, ctx):
        """Get information about the bot"""
        embed = discord.Embed(
            title="Bot Information",
            description="A modular Discord bot using Pycord",
            color=discord.Color.blue()
        )
        embed.add_field(name="Owner", value=f"<@{self.bot.owner_id}>", inline=True)
        embed.add_field(name="Prefix", value=self.bot.command_prefix, inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.set_footer(text="Made with Pycord")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
    # Properly await the sync command
    await bot.tree.sync()