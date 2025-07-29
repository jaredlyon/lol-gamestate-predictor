import requests

RIOT_API_KEY = "RGAPI-XXX-..."
SUMMONER_NAME = "XXX"
REGION = "na1"

# Encode spaces
encoded_name = SUMMONER_NAME.replace(" ", "%20")
url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{encoded_name}"

headers = {
    "X-Riot-Token": RIOT_API_KEY
}

print("Requesting:", url)
response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response Body:", response.text)
