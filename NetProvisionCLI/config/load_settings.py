import yaml
import os

def load_settings():
    settings_path = 'settings/settings.yaml'
    if not os.path.exists(settings_path):
        raise FileNotFoundError("Settings file not found. Run netprovisioncli_settings.py to configure.")
    with open(settings_path, 'r') as file:
        return yaml.safe_load(file)
