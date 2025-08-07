import os
import json
import pandas as pd

INPUT_DIR = "./matches" # raw match data from download script
OUTPUT_DIR = "./preprocessing" # output dir

# flattens a json object into a single row where each header is an amalgamation of key data
def flatten_json(obj, parent_key='', sep='.'):
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep=sep).items())
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_json(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, obj))
    return dict(items)

# flattens all json files matched to a particular suffix in a directory -> outputs a dataframe of all data
def load_and_flatten_jsons(input_dir: str, suffix: str) -> pd.DataFrame:
    rows = []
    for filename in os.listdir(input_dir):
        if filename.endswith(f"{suffix}.json"):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    print(f"{filename} loaded, top-level keys: {list(data.keys())}")
                    flat = flatten_json(data)
                    print(f"flattened {filename} -> {len(flat)} keys")
                    flat['__source_file'] = filename  # track the original file
                    rows.append(flat)
                    print("flattened " + filename)
                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
    return pd.DataFrame(rows)

# main def
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("flattening matches...")
    match_df = load_and_flatten_jsons(INPUT_DIR, suffix='match') # suffix match for match data
    match_df.to_csv(os.path.join(OUTPUT_DIR, '1_match_data_raw.csv'), index=False)
    print(f"saved match_data.csv with {len(match_df)} rows.")

    print("flattening timelines...")
    timeline_df = load_and_flatten_jsons(INPUT_DIR, suffix='timeline') # suffix timeline for timeline data
    timeline_df.to_csv(os.path.join(OUTPUT_DIR, '1_timeline_data_raw.csv'), index=False)
    print(f"saved timeline_data.csv with {len(timeline_df)} rows.")

if __name__ == '__main__':
    main()
