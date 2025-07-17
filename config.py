import os
import json
from pathlib import Path

class Config:
    """Configuration manager for the bot"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)  # Ensure data directory exists
        self._load_token()
        self._load_config()
    
    def _load_token(self):
        """Load token from environment or file"""
        # Try to get token from environment first
        self.token = os.environ.get("DISCORD_BOT_TOKEN")
        
        # If not in environment, load from file
        if not self.token:
            token_path = self.data_dir / "token.txt"
            if token_path.exists():
                self.token = token_path.read_text().strip()
            else:
                # Hard-coded token (from your code) - not recommended for security reasons
                # but used here as a fallback
                default_token = "YOUR_TOKEN_HERE"  # Replace with your actual token
                
                # Ask user for token if not provided
                token = input(f"Please enter your bot token (press Enter to use default): ") or default_token
                token_path.write_text(token)
                self.token = token
    
    def _load_config(self):
        """Load config values from config.json"""
        config_path = self.data_dir / "config.json"
        
        # Default config values
        default_config = {
            "prefix": "!",
            "owner_id": 0,
            "status": "Tag Spam Bot",
            "debug": False
        }
        
        # If config file exists and is not empty, load it
        if config_path.exists() and config_path.stat().st_size > 0:
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                print("Invalid config file. Using default values.")
                config = default_config
                # Save the default config
                with open(config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
        else:
            # If file doesn't exist or is empty, create it with user input
            print("Creating new configuration file...")
            config = {
                "prefix": input("Enter command prefix (default: !): ") or "!",
                "owner_id": int(input("Enter your Discord user ID: ") or "0"),
                "status": input("Enter bot status message (default: 'Tag Spam Bot'): ") or "Tag Spam Bot",
                "debug": input("Enable debug mode? (y/n, default: n): ").lower() == 'y'
            }
            # Save the new config
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
        
        # Set attributes from config
        self.prefix = config.get("prefix", "!")
        self.owner_id = config.get("owner_id", 0)
        self.status = config.get("status", "Tag Spam Bot")
        self.debug = config.get("debug", False)
        
        # Store the raw config for any other values
        self._config = config
    
    def get(self, key, default=None):
        """Get any config value by key"""
        return self._config.get(key, default)
    
    def save(self):
        """Save current config to file"""
        config_data = {
            "prefix": self.prefix,
            "owner_id": self.owner_id,
            "status": self.status,
            "debug": self.debug
        }
        
        # Add any other custom values from the original config
        for key, value in self._config.items():
            if key not in config_data:
                config_data[key] = value
        
        config_path = self.data_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)