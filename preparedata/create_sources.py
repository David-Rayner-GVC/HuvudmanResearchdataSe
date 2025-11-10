import pandas as pd

# Import from the common folder
import os, sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
common_path = Path(__file__).resolve().parent.parent / "common"
# Add to sys.path if not already there
if str(common_path) not in sys.path:
    sys.path.insert(0, str(common_path))  # insert(0) so it takes precedence

from utils import longestCommonPrefix_binary

def create_sources(df):
    """
    df with columns including "DatasetIdentifier" and "SourceRepository"
    return a dataframe with columns=["prefix", "SourceRepository"]
    """
    sf = pd.DataFrame(columns=["prefix", "SourceRepository"])
    sources = df['SourceRepository'].unique()
    for s in sources:
        ids = list(df.loc[df['SourceRepository'] == s]['DatasetIdentifier'])
        prefix = longestCommonPrefix_binary(ids)
        new_row = [prefix,s]
        sf.loc[len(sf)] = new_row
    return sf

def create_sources_files(datafile, sourcesfile):
    """
    read a csv datafile with columns including "DatasetIdentifier" and "SourceRepository"
    write a csv file sourcesfile with columns=["prefix", "SourceRepository"]
    """
    df = pd.read_csv(datafile)
    sf = create_sources(df)
    if sourcesfile is None:
        print(sf)
    else:
        sf.to_csv(sourcesfile,index=False, float_format='%.3f') 

    
if __name__ == "__main__":
    if not ((len(sys.argv) == 3) or (len(sys.argv) == 2)):
        print("Usage: python create_sources.py out_data/metadata.csv")
        print("Usage: python create_sources.py out_data/metadata.csv out_data/sources_RAW.csv")
        sys.exit(1)

    if len(sys.argv) == 2:
        create_sources_files(sys.argv[1], None)
    else:
        create_sources_files(sys.argv[1], sys.argv[2]) 
