import discord
from discord import app_commands
from discord.ext import commands
import datetime

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event that fires when the cog is loaded and ready"""
        print(f"ServerInfo cog loaded successfully")
    
    # Slash command for server info
    @app_commands.command(name="serverinfo", description="Display detailed information about this server")
    async def serverinfo_slash(self, interaction: discord.Interaction):
        """Displays comprehensive information about the server"""
        guild = interaction.guild
        
        # Get server creation date and calculate age
        created_at = guild.created_at
        server_age = (datetime.datetime.now(datetime.timezone.utc) - created_at).days
        
        # Calculate verification level
        verification_level = str(guild.verification_level).capitalize().replace('_', ' ')
        
        # Get role count - safely
        role_count = len(guild.roles) - 1 if guild.roles else 0  # Subtract @everyone role
        
        # Count channels by type - safely
        text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
        categories = len([c for c in guild.channels if isinstance(c, discord.CategoryChannel)])
        forum_channels = len([c for c in guild.channels if hasattr(c, '__class__') and c.__class__.__name__ == 'ForumChannel'])
        
        # Get emoji and sticker counts - safely
        emoji_count = len(guild.emojis) if hasattr(guild, 'emojis') else 0
        sticker_count = len(guild.stickers) if hasattr(guild, 'stickers') else 0
        
        # Get boost status
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        # Get feature flags - safely
        features = ", ".join(guild.features).replace("_", " ").title() if guild.features else "None"
        
        # Build the embed
        embed = discord.Embed(
            title=f"✨ {guild.name}",
            description=f"{guild.description or 'No description set'}\n\n**Server ID:** `{guild.id}`",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        # Server icon in thumbnail
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Add server banner if available
        if hasattr(guild, 'banner') and guild.banner:
            embed.set_image(url=guild.banner.url)
        
        # General information - safely get owner
        owner_text = "Not available"
        if hasattr(guild, 'owner') and guild.owner:
            owner_text = f"{guild.owner.mention} ({guild.owner.name})"
        
        embed.add_field(
            name="👑 Owner",
            value=owner_text,
            inline=True
        )
        
        embed.add_field(
            name="📆 Created On",
            value=f"<t:{int(created_at.timestamp())}:D>\n{server_age} days ago",
            inline=True
        )
        
        embed.add_field(
            name="🔐 Verification",
            value=verification_level,
            inline=True
        )
        
        # Member information
        try:
            bot_count = len([m for m in guild.members if m.bot])
            human_count = guild.member_count - bot_count if hasattr(guild, 'member_count') else "N/A"
            
            embed.add_field(
                name=f"👥 Members ({guild.member_count})",
                value=f"👤 Humans: {human_count}\n🤖 Bots: {bot_count}",
                inline=True
            )
        except Exception:
            # Fallback if member info can't be calculated
            embed.add_field(
                name="👥 Members",
                value=f"Total: {guild.member_count}" if hasattr(guild, 'member_count') else "Member info unavailable",
                inline=True
            )
        
        # Channel information
        total_channels = text_channels + voice_channels + categories + forum_channels
        channel_value = f"💬 Text: {text_channels}\n🔊 Voice: {voice_channels}\n📁 Categories: {categories}"
        if forum_channels > 0:
            channel_value += f"\n📋 Forums: {forum_channels}"
            
        embed.add_field(
            name=f"📚 Channels ({total_channels})",
            value=channel_value,
            inline=True
        )
        
        # Role information - safely
        highest_role = "None"
        if role_count > 0 and len(guild.roles) > 1:
            try:
                highest_role = guild.roles[-1].name
            except IndexError:
                highest_role = "Could not determine"
        
        embed.add_field(
            name=f"🏷️ Roles ({role_count})",
            value=f"Highest: {highest_role}",
            inline=True
        )
        
        # Emoji and sticker information - safely
        emoji_limit = getattr(guild, 'emoji_limit', '?')
        sticker_limit = getattr(guild, 'sticker_limit', '?')
        
        embed.add_field(
            name="😀 Customization",
            value=f"Emojis: {emoji_count}/{emoji_limit}\nStickers: {sticker_count}/{sticker_limit}",
            inline=True
        )
        
        # Boost status
        embed.add_field(
            name="🚀 Server Boost",
            value=f"Level {boost_level}\n{boost_count} boosts",
            inline=True
        )
        
        # Special features - truncate if needed
        if features and features != "None":
            if len(features) > 1024:
                features = features[:1021] + "..."
        
        embed.add_field(
            name="✅ Features",
            value=features,
            inline=True
        )
        
        # AFK information if available
        if hasattr(guild, 'afk_channel') and guild.afk_channel:
            afk_timeout = getattr(guild, 'afk_timeout', 0)
            embed.add_field(
                name="💤 AFK Channel",
                value=f"{guild.afk_channel.name}\nTimeout: {afk_timeout//60} minutes",
                inline=True
            )
        
        # Content filter - safely
        content_filter = "Unknown"
        if hasattr(guild, 'explicit_content_filter'):
            content_filter = str(guild.explicit_content_filter).replace("_", " ").title()
        
        embed.add_field(
            name="🛡️ Content Filter",
            value=content_filter,
            inline=True
        )
        
        # Set footer with current time
        try:
            footer_text = f"Requested by {interaction.user.name}"
            footer_icon = interaction.user.display_avatar.url if hasattr(interaction.user, 'display_avatar') else None
            embed.set_footer(text=footer_text, icon_url=footer_icon)
        except AttributeError:
            # Fallback footer if user properties can't be accessed
            embed.set_footer(text="Server Information")
        
        await interaction.response.send_message(embed=embed)
    
    # Prefix command for server info
    @commands.command(name="serverinfo", description="Display detailed information about this server")
    async def serverinfo_prefix(self, ctx):
        """Displays comprehensive information about the server (prefix version)"""
        guild = ctx.guild
        
        # Get server creation date and calculate age
        created_at = guild.created_at
        server_age = (datetime.datetime.now(datetime.timezone.utc) - created_at).days
        
        # Calculate verification level
        verification_level = str(guild.verification_level).capitalize().replace('_', ' ')
        
        # Get role count - safely
        role_count = len(guild.roles) - 1 if guild.roles else 0  # Subtract @everyone role
        
        # Count channels by type - safely
        text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
        categories = len([c for c in guild.channels if isinstance(c, discord.CategoryChannel)])
        forum_channels = len([c for c in guild.channels if hasattr(c, '__class__') and c.__class__.__name__ == 'ForumChannel'])
        
        # Get emoji and sticker counts - safely
        emoji_count = len(guild.emojis) if hasattr(guild, 'emojis') else 0
        sticker_count = len(guild.stickers) if hasattr(guild, 'stickers') else 0
        
        # Get boost status
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        # Get feature flags - safely
        features = ", ".join(guild.features).replace("_", " ").title() if guild.features else "None"
        
        # Build the embed
        embed = discord.Embed(
            title=f"✨ {guild.name}",
            description=f"{guild.description or 'No description set'}\n\n**Server ID:** `{guild.id}`",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        # Server icon in thumbnail
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Add server banner if available
        if hasattr(guild, 'banner') and guild.banner:
            embed.set_image(url=guild.banner.url)
        
        # General information - safely get owner
        owner_text = "Not available"
        if hasattr(guild, 'owner') and guild.owner:
            owner_text = f"{guild.owner.mention} ({guild.owner.name})"
        
        embed.add_field(
            name="👑 Owner",
            value=owner_text,
            inline=True
        )
        
        embed.add_field(
            name="📆 Created On",
            value=f"<t:{int(created_at.timestamp())}:D>\n{server_age} days ago",
            inline=True
        )
        
        embed.add_field(
            name="🔐 Verification",
            value=verification_level,
            inline=True
        )
        
        # Member information
        try:
            bot_count = len([m for m in guild.members if m.bot])
            human_count = guild.member_count - bot_count if hasattr(guild, 'member_count') else "N/A"
            
            embed.add_field(
                name=f"👥 Members ({guild.member_count})",
                value=f"👤 Humans: {human_count}\n🤖 Bots: {bot_count}",
                inline=True
            )
        except Exception:
            # Fallback if member info can't be calculated
            embed.add_field(
                name="👥 Members",
                value=f"Total: {guild.member_count}" if hasattr(guild, 'member_count') else "Member info unavailable",
                inline=True
            )
        
        # Channel information
        total_channels = text_channels + voice_channels + categories + forum_channels
        channel_value = f"💬 Text: {text_channels}\n🔊 Voice: {voice_channels}\n📁 Categories: {categories}"
        if forum_channels > 0:
            channel_value += f"\n📋 Forums: {forum_channels}"
            
        embed.add_field(
            name=f"📚 Channels ({total_channels})",
            value=channel_value,
            inline=True
        )
        
        # Role information - safely
        highest_role = "None"
        if role_count > 0 and len(guild.roles) > 1:
            try:
                highest_role = guild.roles[-1].name
            except IndexError:
                highest_role = "Could not determine"
        
        embed.add_field(
            name=f"🏷️ Roles ({role_count})",
            value=f"Highest: {highest_role}",
            inline=True
        )
        
        # Emoji and sticker information - safely
        emoji_limit = getattr(guild, 'emoji_limit', '?')
        sticker_limit = getattr(guild, 'sticker_limit', '?')
        
        embed.add_field(
            name="😀 Customization",
            value=f"Emojis: {emoji_count}/{emoji_limit}\nStickers: {sticker_count}/{sticker_limit}",
            inline=True
        )
        
        # Boost status
        embed.add_field(
            name="🚀 Server Boost",
            value=f"Level {boost_level}\n{boost_count} boosts",
            inline=True
        )
        
        # Special features - truncate if needed
        if features and features != "None":
            if len(features) > 1024:
                features = features[:1021] + "..."
        
        embed.add_field(
            name="✅ Features",
            value=features,
            inline=True
        )
        
        # AFK information if available
        if hasattr(guild, 'afk_channel') and guild.afk_channel:
            afk_timeout = getattr(guild, 'afk_timeout', 0)
            embed.add_field(
                name="💤 AFK Channel",
                value=f"{guild.afk_channel.name}\nTimeout: {afk_timeout//60} minutes",
                inline=True
            )
        
        # Content filter - safely
        content_filter = "Unknown"
        if hasattr(guild, 'explicit_content_filter'):
            content_filter = str(guild.explicit_content_filter).replace("_", " ").title()
        
        embed.add_field(
            name="🛡️ Content Filter",
            value=content_filter,
            inline=True
        )
        
        # Set footer with current time
        try:
            footer_text = f"Requested by {ctx.author.name}"
            footer_icon = ctx.author.display_avatar.url if hasattr(ctx.author, 'display_avatar') else None
            embed.set_footer(text=footer_text, icon_url=footer_icon)
        except AttributeError:
            # Fallback footer if user properties can't be accessed
            embed.set_footer(text="Server Information")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))