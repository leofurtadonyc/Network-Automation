# config/config_loader.py
import os
import yaml

class Config:
    def __init__(self, config_file=None):
        # If no config_file is specified, assume config.yaml is in this folder.
        if config_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(base_dir, "config.yaml")
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        if os.path.isfile(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading configuration: {e}")
                return {}
        else:
            print(f"Configuration file {self.config_file} not found.")
            return {}

def load_config(config_file=None):
    return Config(config_file)
