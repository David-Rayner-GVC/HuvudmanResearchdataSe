import requests
import sys
import pandas as pd
from pathlib import Path

# Resolve the directory where *this* file lives
_module_dir = Path(__file__).parent
# Build an absolute path to sources.csv in the same folder
_prefix_path = _module_dir / 'zenodo_ids.csv'
zenodo_mappings = pd.read_csv(_prefix_path)
zenodo_mappings['SourceRepository'].str.strip()

def get_zenodo_community_id(recid):
    """
    Get the actual zenodo community name using the zenodo recid
    """
    url = f"https://zenodo.org/api/records/{recid}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    communities = data["metadata"].get("communities", [])
    community_ids = [c["id"] for c in communities]

    return community_ids

def get_zenodo_community(id, ignore_timeouts=False):
    """
    Get the SourceRepository for a researchdata.se zenodo entry
    id is like doi-10-5281-zenodo-17193077
    """
    assert(id.startswith("doi-10-5281-zenodo-"))
    recid = id[19:]
    community_ids = get_zenodo_community_id(recid)
    for c in community_ids:
        try:
            SourceRepository = get_zenodo_SourceRepository(c)
        except:
            if not ignore_timeouts: raise
        if not SourceRepository is None:
            return SourceRepository
    return "UNKNOWN"
     

def get_zenodo_SourceRepository(zenodo_id):
    r=zenodo_mappings.loc[zenodo_mappings['zenodo_id'] == zenodo_id]
    if len(r)==0:
        return None
    else:
        return r['SourceRepository'].values[0]

if __name__ == "__main__":
    if not ((len(sys.argv) == 2)):
        print("Usage: python get_zenodo_community.py researchdata_id")
        sys.exit(1)
    community_ids= get_zenodo_community(sys.argv[1])
    print("SourceRepository:", community_ids)

