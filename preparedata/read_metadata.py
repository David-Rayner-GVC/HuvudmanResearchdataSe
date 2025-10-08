import sys
import pandas as pd
import json

def read_metadata(infile_path, outfile_path):
    df = pd.DataFrame(columns=["Publisher", "SourceRepository", "YearPublished"])
    with open(infile_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            else:
                j = json.loads(line)
                new_row = [j['principal']['name']['en'],j['source']['name']['en'],int(j['publishedDate'][:4])]
                df.loc[len(df)] = new_row
    df.to_csv(outfile_path,index=False, float_format='%.3f') 


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python read_metadata.py metadata.jsonl metadata.csv")
        sys.exit(1)

    read_metadata(sys.argv[1], sys.argv[2])
