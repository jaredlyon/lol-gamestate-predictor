import requests
import time
import os
import json

# config vars
RIOT_API_KEY = "RGAPI-XXX-..."
SUMMONER_NAME = "XXX"
REGION = "na1"
MATCH_REGION = "americas"
SAVE_DIR = "matches"
MAX_MATCHES = 2000
DELAY_BETWEEN_REQUESTS = 1.5  # in seconds

# setup
HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}
os.makedirs(SAVE_DIR, exist_ok=True)

def safe_request(url):
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 429:
            print("Sleeping due to rate limit")
            time.sleep(120) # two minutes
        elif response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        else:
            return response.json()

# puuid search
def get_puuid():
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{SUMMONER_NAME}"
    data = safe_request(url)
    return data["puuid"] if data else None

# match search
def get_match_ids(puuid):
    match_ids = []
    start = 0
    count = 100

    while True:
        url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        batch = safe_request(url)
        if not batch:
            break
        match_ids.extend(batch)
        if len(batch) < count or len(match_ids) >= MAX_MATCHES:
            break
        start += count
        time.sleep(DELAY_BETWEEN_REQUESTS)
    return match_ids

# download match data
def download_match_data(match_id):
    match_url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    timeline_url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"

    match_data = safe_request(match_url)
    timeline_data = safe_request(timeline_url)

    if match_data and timeline_data:
        with open(os.path.join(SAVE_DIR, f"{match_id}_match.json"), "w") as f:
            json.dump(match_data, f)
        with open(os.path.join(SAVE_DIR, f"{match_id}_timeline.json"), "w") as f:
            json.dump(timeline_data, f)
        print(f"Saved {match_id}")
    else:
        print(f"Failed to download {match_id}")

# main def
def main():
    print("searching puuid...")
    puuid = get_puuid()
    if not puuid:
        print("e: check summoner name and api key")
        return

    print("searching matches...")
    match_ids = get_match_ids(puuid)
    print(f"Found {len(match_ids)} matches")

    for i, match_id in enumerate(match_ids):
        print(f"[{i+1}/{len(match_ids)}] downloading {match_id}...")
        download_match_data(match_id)
        time.sleep(DELAY_BETWEEN_REQUESTS)

if __name__ == "__main__":
    main()
