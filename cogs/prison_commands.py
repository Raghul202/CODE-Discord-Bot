import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

class PrisonCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store prisoner data
        self.prisoners = {}  # {guild_id: {user_id: {original_roles: [], original_nick: ""}}}
        # Mock responses when prisoners try to speak
        self.prison_mockery = [
            "📢 **{}** tried to speak: ~~\"{}\"~~",
            "🔒 **{}** mumbled behind bars: ~~\"{}\"~~",
            "⛓️ **{}** attempted to say: ~~\"{}\"~~",
            "🚔 **{}** was overheard saying: ~~\"{}\"~~",
            "🔐 **{}** whispered: ~~\"{}\"~~",
            "👮 **{}** tried communicating: ~~\"{}\"~~",
            "🏢 **{}** muttered: ~~\"{}\"~~",
            "⚖️ **{}** complained: ~~\"{}\"~~",
            "🔗 **Inmate #{}** had their message confiscated: ~~\"{}\"~~",
            "🚓 **Prisoner #{}** shouted into the void: ~~\"{}\"~~"
        ]
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event that fires when the cog is loaded and ready"""
        print(f"Prison commands cog loaded. Make sure to sync commands with /sync")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Intercept messages from prisoners and mock them"""
        # Ignore bot messages
        if message.author.bot:
            return
            
        # Check if this is a prisoner
        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return
            
        # Check if this user is imprisoned
        guild_prisoners = self.prisoners.get(guild_id, {})
        prisoner_data = guild_prisoners.get(message.author.id)
        
        if prisoner_data:
            # This is a prisoner! Delete their message and mock them
            try:
                await message.delete()
                
                # Get prisoner name or use mention
                prisoner_name = message.author.mention
                
                # Choose a random mockery format
                if "Inmate #{}" in random.choice(self.prison_mockery) or "Prisoner #{}" in random.choice(self.prison_mockery):
                    # For formats with numbers, generate a random prisoner number
                    prisoner_num = random.randint(1000, 9999)
                    mock_format = random.choice([m for m in self.prison_mockery if "#" in m])
                    mock_message = mock_format.format(prisoner_num, message.content)
                else:
                    mock_format = random.choice([m for m in self.prison_mockery if "#" not in m])
                    mock_message = mock_format.format(prisoner_name, message.content)
                
                # Try to use webhook to mimic user's avatar
                try:
                    # Check for existing webhooks
                    webhooks = await message.channel.webhooks()
                    webhook = discord.utils.get(webhooks, name="PrisonWebhook")
                    
                    if webhook is None:
                        webhook = await message.channel.create_webhook(name="PrisonWebhook")
                    
                    # Send with webhook to mimic avatar
                    await webhook.send(
                        content=mock_message,
                        username=f"Prisoner ({message.author.display_name})",
                        avatar_url=message.author.display_avatar.url
                    )
                except (discord.Forbidden, discord.HTTPException):
                    # Fall back to regular message if webhooks not available
                    await message.channel.send(mock_message)
            except discord.HTTPException:
                # If we can't delete the message, just mock them
                pass
    
    async def get_or_create_prisoner_role(self, guild):
        """Get the prisoner role or create it if it doesn't exist"""
        # Look for an existing prisoner role
        for role in guild.roles:
            if role.name.lower() == "prisoner":
                return role
                
        # Create a new prisoner role with limited permissions
        try:
            # Create basic permissions - deny most things
            permissions = discord.Permissions()
            permissions.update(
                read_messages=True,
                read_message_history=True,
                connect=True,  # Can connect to voice channels
                speak=False,   # Cannot speak in voice channels
                send_messages=True,  # Allow sending messages (we'll intercept them)
                embed_links=False,
                attach_files=False,
                add_reactions=False,
                external_emojis=False,
                mention_everyone=False,
                manage_messages=False,
                manage_channels=False,
                manage_roles=False,
                kick_members=False,
                ban_members=False
            )
            
            # Create the role - orange color like a prison jumpsuit
            prisoner_role = await guild.create_role(
                name="Prisoner",
                color=discord.Color.orange(),
                permissions=permissions,
                reason="Created for the prison command system"
            )
            
            return prisoner_role
        except discord.Forbidden:
            return None
    
    # === Slash Commands ===
    @app_commands.command(name="prison", description="Arrest a member and put them in prison")
    @app_commands.describe(
        member="The member to imprison",
        reason="Why they're being imprisoned (optional)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def prison(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Arrest a member and put them in prison"""
        # Check if bot has necessary permissions
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("I need 'Manage Roles' permission to imprison members!", ephemeral=True)
            return
            
        # Check if user is already imprisoned
        guild_prisoners = self.prisoners.get(interaction.guild.id, {})
        if member.id in guild_prisoners:
            await interaction.response.send_message(f"{member.display_name} is already imprisoned!", ephemeral=True)
            return
            
        # Get prisoner role
        prisoner_role = await self.get_or_create_prisoner_role(interaction.guild)
        if not prisoner_role:
            await interaction.response.send_message("Failed to create prisoner role. Please check my permissions.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Save original roles and nickname
            original_roles = [role for role in member.roles if role != interaction.guild.default_role]
            original_nick = member.display_name
            
            # Update the prisoners dictionary
            if interaction.guild.id not in self.prisoners:
                self.prisoners[interaction.guild.id] = {}
                
            self.prisoners[interaction.guild.id][member.id] = {
                "original_roles": [role.id for role in original_roles],
                "original_nick": original_nick
            }
            
            # Remove all roles
            for role in original_roles:
                try:
                    await member.remove_roles(role, reason=f"Imprisoned by {interaction.user.display_name}")
                except discord.HTTPException:
                    continue
            
            # Add prisoner role
            await member.add_roles(prisoner_role, reason=f"Imprisoned by {interaction.user.display_name}")
            
            # Change nickname
            try:
                await member.edit(nick=f"Prisoner ({original_nick[:20]})")
            except discord.HTTPException:
                # If we can't change nickname, continue without it
                pass
            
            # Send success message
            if reason:
                await interaction.followup.send(f"👮 **{member.display_name}** has been imprisoned by **{interaction.user.display_name}**!\nReason: {reason}")
            else:
                await interaction.followup.send(f"👮 **{member.display_name}** has been imprisoned by **{interaction.user.display_name}**!")
                
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to manage that user's roles.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="jail", description="Arrest a member and put them in prison (alias for prison)")
    @app_commands.describe(
        member="The member to imprison",
        reason="Why they're being imprisoned (optional)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def jail(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Alias for the prison command"""
        await self.prison(interaction, member, reason)
    
    @app_commands.command(name="release", description="Release a member from prison")
    @app_commands.describe(
        member="The member to release from prison"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def release(self, interaction: discord.Interaction, member: discord.Member):
        """Release a member from prison"""
        # Check if bot has necessary permissions
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("I need 'Manage Roles' permission to release members!", ephemeral=True)
            return
            
        # Check if user is imprisoned
        guild_prisoners = self.prisoners.get(interaction.guild.id, {})
        prisoner_data = guild_prisoners.get(member.id)
        if not prisoner_data:
            await interaction.response.send_message(f"{member.display_name} is not imprisoned!", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Get prisoner role
            prisoner_role = None
            for role in interaction.guild.roles:
                if role.name.lower() == "prisoner":
                    prisoner_role = role
                    break
            
            # Remove prisoner role
            if prisoner_role and prisoner_role in member.roles:
                await member.remove_roles(prisoner_role, reason=f"Released by {interaction.user.display_name}")
            
            # Restore original roles
            for role_id in prisoner_data["original_roles"]:
                role = interaction.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role, reason=f"Released from prison by {interaction.user.display_name}")
                    except discord.HTTPException:
                        continue
            
            # Restore nickname
            try:
                await member.edit(nick=prisoner_data["original_nick"])
            except discord.HTTPException:
                pass
            
            # Remove from prisoners dictionary
            del self.prisoners[interaction.guild.id][member.id]
            if not self.prisoners[interaction.guild.id]:
                del self.prisoners[interaction.guild.id]
            
            # Send success message
            await interaction.followup.send(f"🔓 **{member.display_name}** has been released from prison by **{interaction.user.display_name}**!")
                
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to manage that user's roles.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    # === Prefix Commands ===
    @commands.command(name="prison", help="Arrest a member and put them in prison")
    @commands.has_permissions(manage_roles=True)
    async def prefix_prison(self, ctx, member: discord.Member, *, reason: str = None):
        """Arrest a member and put them in prison (prefix version)"""
        # Check if bot has necessary permissions
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send("I need 'Manage Roles' permission to imprison members!")
            return
            
        # Check if user is already imprisoned
        guild_prisoners = self.prisoners.get(ctx.guild.id, {})
        if member.id in guild_prisoners:
            await ctx.send(f"{member.display_name} is already imprisoned!")
            return
            
        # Get prisoner role
        prisoner_role = await self.get_or_create_prisoner_role(ctx.guild)
        if not prisoner_role:
            await ctx.send("Failed to create prisoner role. Please check my permissions.")
            return
            
        try:
            # Save original roles and nickname
            original_roles = [role for role in member.roles if role != ctx.guild.default_role]
            original_nick = member.display_name
            
            # Update the prisoners dictionary
            if ctx.guild.id not in self.prisoners:
                self.prisoners[ctx.guild.id] = {}
                
            self.prisoners[ctx.guild.id][member.id] = {
                "original_roles": [role.id for role in original_roles],
                "original_nick": original_nick
            }
            
            # Remove all roles
            for role in original_roles:
                try:
                    await member.remove_roles(role, reason=f"Imprisoned by {ctx.author.display_name}")
                except discord.HTTPException:
                    continue
            
            # Add prisoner role
            await member.add_roles(prisoner_role, reason=f"Imprisoned by {ctx.author.display_name}")
            
            # Change nickname
            try:
                await member.edit(nick=f"Prisoner ({original_nick[:20]})")
            except discord.HTTPException:
                # If we can't change nickname, continue without it
                pass
            
            # Send success message
            if reason:
                await ctx.send(f"👮 **{member.display_name}** has been imprisoned by **{ctx.author.display_name}**!\nReason: {reason}")
            else:
                await ctx.send(f"👮 **{member.display_name}** has been imprisoned by **{ctx.author.display_name}**!")
                
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage that user's roles.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    
    @commands.command(name="jail", help="Arrest a member and put them in prison (alias for prison)")
    @commands.has_permissions(manage_roles=True)
    async def prefix_jail(self, ctx, member: discord.Member, *, reason: str = None):
        """Alias for the prison command (prefix version)"""
        await self.prefix_prison(ctx, member, reason=reason)
    
    @commands.command(name="release", help="Release a member from prison")
    @commands.has_permissions(manage_roles=True)
    async def prefix_release(self, ctx, member: discord.Member):
        """Release a member from prison (prefix version)"""
        # Check if bot has necessary permissions
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send("I need 'Manage Roles' permission to release members!")
            return
            
        # Check if user is imprisoned
        guild_prisoners = self.prisoners.get(ctx.guild.id, {})
        prisoner_data = guild_prisoners.get(member.id)
        if not prisoner_data:
            await ctx.send(f"{member.display_name} is not imprisoned!")
            return
            
        try:
            # Get prisoner role
            prisoner_role = None
            for role in ctx.guild.roles:
                if role.name.lower() == "prisoner":
                    prisoner_role = role
                    break
            
            # Remove prisoner role
            if prisoner_role and prisoner_role in member.roles:
                await member.remove_roles(prisoner_role, reason=f"Released by {ctx.author.display_name}")
            
            # Restore original roles
            for role_id in prisoner_data["original_roles"]:
                role = ctx.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role, reason=f"Released from prison by {ctx.author.display_name}")
                    except discord.HTTPException:
                        continue
            
            # Restore nickname
            try:
                await member.edit(nick=prisoner_data["original_nick"])
            except discord.HTTPException:
                pass
            
            # Remove from prisoners dictionary
            del self.prisoners[ctx.guild.id][member.id]
            if not self.prisoners[ctx.guild.id]:
                del self.prisoners[ctx.guild.id]
            
            # Send success message
            await ctx.send(f"🔓 **{member.display_name}** has been released from prison by **{ctx.author.display_name}**!")
                
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage that user's roles.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(bot):
    # Add the cog to the bot
    await bot.add_cog(PrisonCommands(bot))