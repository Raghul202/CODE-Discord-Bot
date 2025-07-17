import os
import importlib
from pathlib import Path

class Loader:
    """Handles loading of extensions (cogs) and events"""
    
    @staticmethod
    async def load_all(bot):
        """Load all cogs and events"""
        await Loader._load_cogs(bot)
        await Loader._load_events(bot)
    
    @staticmethod
    async def _load_cogs(bot):
        """Load all cogs from the cogs directory"""
        cogs_dir = Path("cogs")
        cogs_dir.mkdir(exist_ok=True)
        
        # Get all Python files in the cogs directory
        cog_files = [f for f in cogs_dir.glob("*.py") if f.is_file() and not f.name.startswith("_")]
        
        if not cog_files and bot.config.debug:
            print("No cog files found in the cogs directory.")
            return
        
        # Load each cog
        for cog_file in cog_files:
            cog_name = cog_file.stem
            cog_path = f"cogs.{cog_name}"
            
            try:
                await bot.load_extension(cog_path)
                if bot.config.debug:
                    print(f"Loaded cog: {cog_path}")
            except Exception as e:
                print(f"Failed to load cog {cog_path}: {e}")
    
  # In loader.py, update the _load_cogs method:

@staticmethod
async def _load_cogs(bot):
    """Load all cogs from the cogs directory"""
    cogs_dir = Path("cogs")
    cogs_dir.mkdir(exist_ok=True)
    
    # Get all Python files in the cogs directory
    cog_files = [f for f in cogs_dir.glob("*.py") if f.is_file() and not f.name.startswith("_")]
    
    if not cog_files and bot.config.debug:
        print("No cog files found in the cogs directory.")
        return
    
    # Load each cog
    for cog_file in cog_files:
        cog_name = cog_file.stem
        cog_path = f"cogs.{cog_name}"
        
        try:
            await bot.load_extension(cog_path)
            if bot.config.debug:
                print(f"Loaded cog: {cog_path}")
        except Exception as e:
            print(f"Failed to load cog {cog_path}: {e}")
    
    @staticmethod
    async def reload_extension(bot, extension_name):
        """Reload a specific extension"""
        try:
            await bot.reload_extension(extension_name)
            return True, f"Successfully reloaded {extension_name}"
        except Exception as e:
            return False, f"Failed to reload {extension_name}: {e}"
    
    @staticmethod
    async def reload_all(bot):
        """Reload all extensions"""
        results = []
        
        # Reload cogs
        for extension in list(bot.extensions):
            success, message = await Loader.reload_extension(bot, extension)
            results.append(message)
        
        # Reload events (this is more complex as they're not typical extensions)
        events_dir = Path("events")
        for event_file in events_dir.glob("*.py"):
            event_name = event_file.stem
            event_path = f"events.{event_name}"
            
            try:
                # Reload the module
                event_module = importlib.import_module(event_path)
                importlib.reload(event_module)
                
                # Re-setup if possible
                if hasattr(event_module, "setup"):
                    event_module.setup(bot)
                
                results.append(f"Successfully reloaded event {event_path}")
            except Exception as e:
                results.append(f"Failed to reload event {event_path}: {e}")
        
        return results