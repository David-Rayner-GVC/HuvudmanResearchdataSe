import sys
import pandas as pd
import json

# Import from the common folder
import os, sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
common_path = Path(__file__).resolve().parent.parent / "common"
# Add to sys.path if not already there
if str(common_path) not in sys.path:
    sys.path.insert(0, str(common_path))  # insert(0) so it takes precedence

from update_metadata import fix_date

def read_metadata(infile_path, outfile_path):
    df = pd.DataFrame(columns=["DatasetIdentifier","DatasetIdentifierV1","Publisher", "SourceRepository", "YearPublished"])
    with open(infile_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            else:
                j = json.loads(line)
                new_row = [j['datasetIdentifier'],j['datasetIdentifier'],j['principal']['name']['en'],j['source']['name']['en'],fix_date(j)]
                df.loc[len(df)] = new_row
    df.to_csv(outfile_path,index=False, float_format='%.3f') 


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python read_metadata.py in_data/metadata.jsonl ../dashboard/data/metadata.csv")
        sys.exit(1)

    read_metadata(sys.argv[1], sys.argv[2])
