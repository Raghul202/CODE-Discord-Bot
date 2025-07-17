import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

class PossessCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store active possession webhooks
        self.active_possessions = {}
        
        # Creepy possession responses - expanded list
        self.possession_messages = [
            "I feel... different...",
            "Something's taking over my mind...",
            "I can't control my thoughts anymore...",
            "Help me... something's inside me...",
            "I'm losing control of myself...",
            "The darkness is consuming me...",
            "I'm not alone in my head anymore...",
            "Something's speaking through me...",
            "I can feel it crawling inside my brain...",
            "My thoughts aren't my own anymore...",
            "There's a shadow where my soul should be...",
            "It's whispering terrible things to me...",
            "I can see through different eyes now...",
            "My reflection doesn't move when I do...",
            "The voices won't stop...",
            "I'm trapped inside my own body...",
            "I can feel my consciousness fading...",
            "Something ancient has awakened within me...",
            "The thing inside me is hungry...",
            "I feel like a puppet on strings...",
            "It knows all my secrets now...",
            "Cold fingers wrapping around my mind...",
            "Every heartbeat pushes it deeper inside me...",
            "The darkness behind my eyes is alive...",
            "I can't tell where I end and it begins...",
            "Something old and terrible lives in me now...",
            "My blood feels like ice in my veins...",
            "I'm becoming something else entirely...",
            "It's rewriting my memories one by one...",
            "I don't recognize myself anymore...",
            "The shadows move when I'm not looking...",
            "My dreams aren't mine anymore...",
            "There's something watching through my eyes...",
            "I can feel it feeding on my fear...",
            "My body moves without my permission...",
        ]
        
        # Meme possession responses - expanded list
        self.meme_possession_messages = [
            "My brain has been hacked lol",
            "404: Soul not found",
            "New personality, who dis?",
            "Possession go brrrr",
            "When the demon possesses you just right 👌",
            "Help I've been possessed and I can't get up!",
            "Instructions unclear, got possessed by ghost",
            "Me: *gets possessed* Also me: This is fine",
            "When someone takes 'be yourself' too literally",
            "Demon's first day on the possession job",
            "POV: You're the demon inside me",
            "Is this possession or am I just vibing?",
            "Ghost typed this, no cap fr fr",
            "I'm just a vessel, don't @ me",
            "This isn't even my final form",
            "Demon possession speedrun any%",
            "Being possessed is my personality trait now",
            "You wouldn't download a soul",
            "Possession? In this economy?",
            "Felt cute, might get exorcised later idk",
            "My FBI agent watching me get possessed: 👁️👄👁️",
            "New demonic entity, same old me",
            "If you can't handle me possessed, you don't deserve me exorcised",
            "Not me playing host to an otherworldly entity",
            "Bestie, is it normal when your soul leaves the chat?",
            "*record scratch* *freeze frame* Yep, that's me. You're probably wondering how I got possessed",
            "When the ghost catches these hands but possesses your body instead",
            "No talk me, I'm demon now",
            "Current status: possessed but make it fashion",
            "My therapist: 'The demon inside you isn't real'. The demon inside me:",
            "Tell the void I said hi",
            "This possession is sponsored by NordVPN",
            "I've been trying to reach you about your soul's extended warranty",
            "My last two brain cells fighting the demon for control",
            "When you get possessed but the demon has to deal with your problems now"
        ]
        
        # Possession end messages
        self.possession_end_messages = [
            "**What... happened to me?** *I feel normal again...*",
            "**I... I'm back?** *That was terrifying...*",
            "**The darkness... it's gone...** *I can think clearly again...*",
            "**Am I free?** *I remember... horrible things...*",
            "**My mind is my own again...** *What did it make me say?*",
            "**The presence has left me...** *I feel empty but relieved...*"
        ]
        
        # Possession forced end messages
        self.possession_forced_end_messages = [
            "**The spirit has been exorcised from me!**",
            "**It's gone! I'm free!**",
            "**The darkness has been banished!**",
            "**I can feel it leaving my body!**",
            "**The entity has been cast out!**",
            "**My soul is my own again!**"
        ]
        
        # First possession messages
        self.possession_start_messages = [
            "**I've been possessed!** 👻",
            "**Something's taking control of me!** 👻",
            "**I feel a presence inside me!** 👻",
            "**My body is no longer my own!** 👻",
            "**Help! Something's inside me!** 👻",
            "**I can feel myself slipping away!** 👻"
        ]
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event that fires when the cog is loaded and ready"""
        print(f"Possession commands cog loaded. Make sure to sync commands with /sync")
    
    # === Slash Commands ===
    @app_commands.command(name="possess", description="Possess a user and speak as them")
    @app_commands.describe(
        user="The user to possess",
        style="The style of possession messages",
        duration="How many minutes to possess them for (max 10)"
    )
    @app_commands.choices(style=[
        app_commands.Choice(name="Creepy", value="creepy"),
        app_commands.Choice(name="Meme", value="meme")
    ])
    async def possess(self, interaction: discord.Interaction, user: discord.Member, style: str = "creepy", duration: int = 5):
        """Possess a user and send messages as them"""
        # Check permissions
        if not interaction.channel.permissions_for(interaction.guild.me).manage_webhooks:
            await interaction.response.send_message("I need 'Manage Webhooks' permission to possess users!", ephemeral=True)
            return
        
        # Check duration limits
        if duration > 10:
            await interaction.response.send_message("That's too long! Maximum possession time is 10 minutes.", ephemeral=True)
            return
            
        # Check if there's already an active possession in this channel
        if interaction.channel.id in self.active_possessions:
            await interaction.response.send_message("Already possessing someone in this channel! Use `/unpossess` to end it.", ephemeral=True)
            return
        
        # Acknowledge the command
        await interaction.response.defer(ephemeral=True)
        
        # Create a webhook for the possession
        webhook = await interaction.channel.create_webhook(name=f"Possessed_{user.id}")
        
        # Convert minutes to seconds
        duration_seconds = duration * 60
        end_time = asyncio.get_event_loop().time() + duration_seconds
        
        # Store possession info
        self.active_possessions[interaction.channel.id] = {
            "webhook": webhook,
            "user": user,
            "style": style,
            "task": None,
            "used_messages": set()  # Track used messages to avoid repetition
        }
        
        async def possession_task():
            try:
                # Initial message - random starter
                start_message = random.choice(self.possession_start_messages)
                await webhook.send(
                    content=start_message,
                    username=user.display_name,
                    avatar_url=user.display_avatar.url
                )
                
                # Send messages periodically
                used_messages = set()  # Track used messages for this session
                
                while asyncio.get_event_loop().time() < end_time:
                    # Select message based on style
                    if style == "creepy":
                        message_pool = [msg for msg in self.possession_messages if msg not in used_messages]
                        # If we've used all messages, reset the pool
                        if not message_pool:
                            used_messages.clear()
                            message_pool = self.possession_messages
                        
                        message = random.choice(message_pool)
                        used_messages.add(message)
                    else:  # meme style
                        message_pool = [msg for msg in self.meme_possession_messages if msg not in used_messages]
                        # If we've used all messages, reset the pool
                        if not message_pool:
                            used_messages.clear()
                            message_pool = self.meme_possession_messages
                        
                        message = random.choice(message_pool)
                        used_messages.add(message)
                    
                    # Send as the possessed user
                    await webhook.send(
                        content=message,
                        username=user.display_name,
                        avatar_url=user.display_avatar.url
                    )
                    
                    # Random delay between 20-90 seconds
                    delay = random.randint(20, 90)
                    await asyncio.sleep(delay)
                    
                # Final message when possession ends normally
                end_message = random.choice(self.possession_end_messages)
                await webhook.send(
                    content=end_message,
                    username=user.display_name,
                    avatar_url=user.display_avatar.url
                )
                
            except asyncio.CancelledError:
                # Final message when possession is stopped
                forced_end_message = random.choice(self.possession_forced_end_messages)
                await webhook.send(
                    content=forced_end_message,
                    username=user.display_name,
                    avatar_url=user.display_avatar.url
                )
            finally:
                # Clean up webhook and remove from active possessions
                try:
                    await webhook.delete()
                except discord.HTTPException:
                    pass
                self.active_possessions.pop(interaction.channel.id, None)
        
        # Start the possession task
        task = asyncio.create_task(possession_task())
        self.active_possessions[interaction.channel.id]["task"] = task
        
        # Confirm to the command user
        await interaction.followup.send(f"You've possessed {user.mention} for {duration} minutes in {style} style! 👻", ephemeral=True)
    
    @app_commands.command(name="unpossess", description="Stop possessing the user in this channel")
    async def unpossess(self, interaction: discord.Interaction):
        """Stop any ongoing possession in the current channel"""
        possession_data = self.active_possessions.get(interaction.channel.id)
        
        if possession_data:
            # Cancel the task
            if possession_data["task"]:
                possession_data["task"].cancel()
            
            await interaction.response.send_message("The possession has been ended!", ephemeral=True)
        else:
            await interaction.response.send_message("There's no active possession in this channel.", ephemeral=True)
    
    # === Prefix Commands ===
    @commands.command(name="possess", help="Possess a user and speak as them")
    async def prefix_possess(self, ctx, user: discord.Member, style: str = "creepy", duration: int = 5):
        """Possess a user and send messages as them (prefix version)"""
        # Check if style is valid
        if style.lower() not in ["creepy", "meme"]:
            await ctx.send("Invalid style! Choose either 'creepy' or 'meme'.")
            return
            
        # Check permissions
        if not ctx.channel.permissions_for(ctx.guild.me).manage_webhooks:
            await ctx.send("I need 'Manage Webhooks' permission to possess users!")
            return
        
        # Check duration limits
        if duration > 10:
            await ctx.send("That's too long! Maximum possession time is 10 minutes.")
            return
            
        # Check if there's already an active possession in this channel
        if ctx.channel.id in self.active_possessions:
            await ctx.send("Already possessing someone in this channel! Use `!unpossess` to end it.")
            return
        
        # Create a webhook for the possession
        webhook = await ctx.channel.create_webhook(name=f"Possessed_{user.id}")
        
        # Convert minutes to seconds
        duration_seconds = duration * 60
        end_time = asyncio.get_event_loop().time() + duration_seconds
        
        # Store possession info
        self.active_possessions[ctx.channel.id] = {
            "webhook": webhook,
            "user": user,
            "style": style.lower(),
            "task": None,
            "used_messages": set()  # Track used messages to avoid repetition
        }
        
        async def possession_task():
            try:
                # Initial message - random starter
                start_message = random.choice(self.possession_start_messages)
                await webhook.send(
                    content=start_message,
                    username=user.display_name,
                    avatar_url=user.display_avatar.url
                )
                
                # Send messages periodically
                used_messages = set()  # Track used messages for this session
                
                while asyncio.get_event_loop().time() < end_time:
                    # Select message based on style
                    if style.lower() == "creepy":
                        message_pool = [msg for msg in self.possession_messages if msg not in used_messages]
                        # If we've used all messages, reset the pool
                        if not message_pool:
                            used_messages.clear()
                            message_pool = self.possession_messages
                        
                        message = random.choice(message_pool)
                        used_messages.add(message)
                    else:  # meme style
                        message_pool = [msg for msg in self.meme_possession_messages if msg not in used_messages]
                        # If we've used all messages, reset the pool
                        if not message_pool:
                            used_messages.clear()
                            message_pool = self.meme_possession_messages
                        
                        message = random.choice(message_pool)
                        used_messages.add(message)
                    
                    # Send as the possessed user
                    await webhook.send(
                        content=message,
                        username=user.display_name,
                        avatar_url=user.display_avatar.url
                    )
                    
                    # Random delay between 20-90 seconds
                    delay = random.randint(20, 90)
                    await asyncio.sleep(delay)
                    
                # Final message when possession ends normally
                end_message = random.choice(self.possession_end_messages)
                await webhook.send(
                    content=end_message,
                    username=user.display_name,
                    avatar_url=user.display_avatar.url
                )
                
            except asyncio.CancelledError:
                # Final message when possession is stopped
                forced_end_message = random.choice(self.possession_forced_end_messages)
                await webhook.send(
                    content=forced_end_message,
                    username=user.display_name,
                    avatar_url=user.display_avatar.url
                )
            finally:
                # Clean up webhook and remove from active possessions
                try:
                    await webhook.delete()
                except discord.HTTPException:
                    pass
                self.active_possessions.pop(ctx.channel.id, None)
        
        # Start the possession task
        task = asyncio.create_task(possession_task())
        self.active_possessions[ctx.channel.id]["task"] = task
        
        # Confirm to the command user
        await ctx.send(f"You've possessed {user.mention} for {duration} minutes in {style} style! 👻")
    
    @commands.command(name="unpossess", help="Stop possessing the user in this channel")
    async def prefix_unpossess(self, ctx):
        """Stop any ongoing possession in the current channel (prefix version)"""
        possession_data = self.active_possessions.get(ctx.channel.id)
        
        if possession_data:
            # Cancel the task
            if possession_data["task"]:
                possession_data["task"].cancel()
            
            await ctx.send("The possession has been ended!")
        else:
            await ctx.send("There's no active possession in this channel.")

async def setup(bot):
    # Add the cog to the bot
    await bot.add_cog(PossessCommands(bot))