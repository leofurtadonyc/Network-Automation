# config/config_loader.py
import os
import yaml

class Config:
    # If no config_file is specified, assume config.yaml is in this folder.
    def __init__(self, config_file="config/config.yaml"):
        if not os.path.isfile(config_file):
            raise Exception(f"Configuration file {config_file} not found.")
        with open(config_file, "r") as f:
            self.config_data = yaml.safe_load(f)

    def get(self, key, default=None):
        return self.config_data.get(key, default)

    def get_preferred_language(self):
        return self.config_data.get("preferred_language", "en")

# For testing purposes:
if __name__ == "__main__":
    config = Config()
    print("Preferred language:", config.get_preferred_language())
