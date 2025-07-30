import requests
import time
import os
import json
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
SUMMONER_NAME = os.getenv("SUMMONER_NAME")
TAG_LINE = os.getenv("TAG_LINE")
REGION = os.getenv("REGION")
SAVE_DIR = "matches"
MAX_MATCHES = 2000
DELAY_BETWEEN_REQUESTS = 1.5  # in seconds
SLEEP_TIMER_IF_RATE_LIMITED = 120 # in seconds
QUEUE_IDS_TO_INCLUDE = [400]  # 400 for normal draft pick, this changes if doing ranked


# header for key
HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}

# check save target dir
os.makedirs(SAVE_DIR, exist_ok=True)

# handle api rate limiting - sleeps program if rate limited
def safe_request(url):
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 429:
            print("rate limit hit - sleeping...")
            time.sleep(SLEEP_TIMER_IF_RATE_LIMITED)
        elif response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return None
        else:
            return response.json()

# get puuid
def get_puuid():
    encoded_name = urllib.parse.quote(SUMMONER_NAME)
    encoded_tag = urllib.parse.quote(TAG_LINE)
    url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_name}/{encoded_tag}"
    data = safe_request(url)
    return data["puuid"] if data else None

# get match ids from puuid
def get_match_ids(puuid):
    match_ids = []
    # api limits pagination to 100 (?)
    # this breaks up each request into groups of 100
    start = 0
    count = 100

    while True:
        url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
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
    match_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    timeline_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"

    match_data = safe_request(match_url)
    if not match_data:
        print(f"failed to fetch match data: {match_id}")
        return

    # filter matches not in allowed list
    queue_id = match_data["info"].get("queueId")
    if queue_id not in QUEUE_IDS_TO_INCLUDE:
        print(f"skipped: {match_id} (queueId {queue_id})")
        return

    timeline_data = safe_request(timeline_url)
    if not timeline_data:
        print(f"failed to fetch timeline: {match_id}")
        return

    with open(os.path.join(SAVE_DIR, f"{match_id}_match.json"), "w") as f:
        json.dump(match_data, f)
    with open(os.path.join(SAVE_DIR, f"{match_id}_timeline.json"), "w") as f:
        json.dump(timeline_data, f)
    print(f"saved: {match_id}")

# main
def main():
    print("getting puuid...")
    puuid = get_puuid()
    if not puuid:
        print("error - check env files")
        return

    print("getting match ids...")
    match_ids = get_match_ids(puuid)
    print(f"found {len(match_ids)} matches")

    for i, match_id in enumerate(match_ids):
        print(f"[{i+1}/{len(match_ids)}] downloading {match_id}...")
        download_match_data(match_id)
        time.sleep(DELAY_BETWEEN_REQUESTS)

if __name__ == "__main__":
    main()
