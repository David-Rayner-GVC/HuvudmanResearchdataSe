import sys
import pandas as pd
import json

def fix_date(j):
    """
    For some data sources it is possible to estimate the first-published date
    """
    source = j['source']['repository']
    if source=="sprakbanken-text":
        dates = list()
        dates.append(int(j['publishedDate'][:4]))
        dates.append(int(j['modifiedDate'][:4]))
        return (min(dates))
    else:
        return(int(j['publishedDate'][:4]))

def read_metadata(infile_path, outfile_path):
    df = pd.DataFrame(columns=["DatasetIdentifier","Publisher", "SourceRepository", "YearPublished"])
    with open(infile_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            else:
                j = json.loads(line)
                new_row = [j['datasetIdentifier'],j['principal']['name']['en'],j['source']['name']['en'],fix_date(j)]
                df.loc[len(df)] = new_row
    df.to_csv(outfile_path,index=False, float_format='%.3f') 


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python read_metadata.py metadata.jsonl metadata.csv")
        sys.exit(1)

    read_metadata(sys.argv[1], sys.argv[2])
