import requests

url = "http://192.168.0.238:11434/api/generate"  # try /api/generate or /api depending on documentation
payload = {
    "model": "llama3.1:8b",  # or your actual model name
    "prompt": "Hello, world!"
}
try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
