# llm_interface.py
from config import Config
from langchain_ollama import OllamaLLM

def get_llm():
    config = Config()
    ollama_config = config.get_ollama_config()
    host = ollama_config.get("host", "192.168.0.213")
    port = ollama_config.get("port", 11434)
    base_url = f"http://{host}:{port}"  # no explicit /api/ here
    llm = OllamaLLM(model="llama3.1:8b", base_url=base_url)
    return llm

if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke("Hello, world!")
    print(response)
