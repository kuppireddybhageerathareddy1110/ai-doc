import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")

URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

resp = requests.get(URL)

print("STATUS:", resp.status_code)
print(resp.text)
