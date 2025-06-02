import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config_data = {}
        self._load_config()

    def _load_config(self):
        """Loads configuration from the JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                print(f"Configuration loaded from {self.config_file}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {self.config_file}: {e}")
                self.config_data = {} # Reset to empty config on error
            except Exception as e:
                print(f"An unexpected error occurred while loading config: {e}")
                self.config_data = {}
        else:
            print(f"Config file {self.config_file} not found. Starting with empty configuration.")
            self.config_data = {}

    def get_setting(self, key, default=None):
        """Retrieves a setting by key, with an optional default value."""
        return self.config_data.get(key, default)

    def set_setting(self, key, value):
        """Sets a configuration setting."""
        self.config_data[key] = value
        print(f"Setting '{key}' updated to '{value}'.")

    def save_config(self):
        """Saves the current configuration to the JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False

    def display_config(self):
        """Prints all current configuration settings."""
        print("\n--- Current Configuration ---")
        if not self.config_data:
            print("No configuration settings available.")
        else:
            for key, value in self.config_data.items():
                print(f"  {key}: {value}")
        print("-----------------------------\n")

if __name__ == "__main__":
    # Create a dummy config file for testing
    initial_config = {
        "database_url": "sqlite:///app.db",
        "log_level": "INFO",
        "max_connections": 10,
        "features": ["auth", "payments"]
    }
    with open("config.json", "w", encoding='utf-8') as f:
        json.dump(initial_config, f, indent=4, ensure_ascii=False)
    print("Dummy config.json created.")

    manager = ConfigManager()
    manager.display_config()

    print("Updating settings...")
    manager.set_setting("log_level", "DEBUG")
    manager.set_setting("api_key", "sk_test_12345")
    manager.save_config()

    print(f"Retrieved log_level: {manager.get_setting('log_level')}")
    print(f"Retrieved nonexistent_key (default 'N/A'): {manager.get_setting('nonexistent_key', 'N/A')}")

    manager.display_config()
