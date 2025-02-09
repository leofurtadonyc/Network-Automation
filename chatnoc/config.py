# config.py
import os
import yaml

class Config:
    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        with open(self.config_file, "r") as f:
            return yaml.safe_load(f)

    def get_ollama_config(self):
        return self.config_data.get("ollama", {})

if __name__ == "__main__":
    config = Config()
    print("Ollama Config:", config.get_ollama_config())
