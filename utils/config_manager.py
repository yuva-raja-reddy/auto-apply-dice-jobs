# dice_auto_apply/utils/config_manager.py

import os
import json
from pathlib import Path

class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        self.config_file = os.path.join(self.config_dir, "settings.json")
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from file."""
        # Ensure config directory exists
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Create default config if it doesn't exist
        if not os.path.exists(self.config_file):
            default_config = {
                "search_queries": ["AI ML", "Gen AI", "Agentic AI", "Data Engineer", "Data Analyst", "Machine Learning"],
                "exclude_keywords": ["Manager", "Director",".net", "SAP","java","w2 only","only w2","no c2c",
        "only on w2","w2 profiles only","tester","f2f"],
                "include_keywords": ["AI", "Artificial","Inteligence","Machine","Learning", "ML", "Data", "NLP", "ETL",
        "Natural Language Processing","analyst","scientist","senior","cloud", 
        "aws","gcp","Azure","agentic","python","rag","llm"],
                "headless_mode": False,
                "job_application_limit": 50,
                "save_logs": True
            }
            
            # Write default config to file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
        self.save_config()
