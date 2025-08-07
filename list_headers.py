import pandas as pd
import os

INPUT_DIR = "./preprocessing"
OUTPUT_DIR = "./headers"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# extracts the headers from the match and timeline csvs into .txt files
# timeline header extraction takes awhile because there are over half a million features
# TODO: parallelize this?
def save_headers(csv_file: str, output_txt: str):
    path = os.path.join(INPUT_DIR, csv_file)
    df = pd.read_csv(path, nrows=0) # only read the header of the file
    headers = df.columns.tolist()
    
    with open(os.path.join(OUTPUT_DIR, output_txt), 'w', encoding='utf-8') as f:
        for col in headers:
            f.write(col + '\n')
    
    print(f"extracted {len(headers)} headers from {csv_file} into {output_txt}.")

save_headers("match_data.csv", "match_headers.txt")
save_headers("timeline_data.csv", "timeline_headers.txt")
