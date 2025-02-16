# llm/llm_interface.py
from langchain_ollama import OllamaLLM
import yaml
import os

def load_llm_config(config_file="config.yaml"):
    # Optionally load LLM-related settings from config.yaml.
    if os.path.isfile(config_file):
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            return config.get("ollama", {})  # expect a section named 'ollama'
        except Exception as e:
            print(f"Error loading LLM config: {e}")
    return {}

def get_llm():
    config = load_llm_config()
    # Set default base_url and model if not provided in config.
    base_url = config.get("base_url", "http://192.168.0.213:11434")
    # model = config.get("model", "deepseek-coder:6.7b")
    # model = config.get("model", "deepseek-r1:8b")
    # model = config.get("model", "llama3.2")
    model = config.get("model", "llama3.1:8b")
    llm = OllamaLLM(model=model, base_url=base_url)
    return llm
