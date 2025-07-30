import requests
from dotenv import load_dotenv
import os

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
SUMMONER_NAME = os.getenv("SUMMONER_NAME")
TAG_LINE = os.getenv("TAG_LINE")
REGION = os.getenv("REGION")

print("API Key Loaded:", bool(RIOT_API_KEY))  # confirm key load

url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{SUMMONER_NAME}/{TAG_LINE}"

headers = {
    "X-Riot-Token": RIOT_API_KEY
}

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)
print("Response Body:", response.text)