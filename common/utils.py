from bs4 import BeautifulSoup
import requests
import lxml
import json
import re
import pandas as pd
from pathlib import Path

verbose = True

dorisPattern = re.compile(r"\d\d\d\d-\d+-\d+")
dorisExtPattern = re.compile(r"\d\d\d\d-\d+")

# Resolve the directory where *this* file lives
_module_dir = Path(__file__).parent
# Build an absolute path to sources.csv in the same folder
_prefix_path = _module_dir / 'sources.csv'
prefixes = pd.read_csv(_prefix_path)

# source: https://jackwhitworth.com/python/get-xml-sitemap-using-python/

def get_urls_from_sitemap(url) -> list:
    print("Getting Sitemap for " + url)
    #Send our GET requests and parse the response with BS4
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        return([])
    soup = BeautifulSoup(r.text, 'xml')
    #Set up list for all links
    website_links = []
    #Find all <loc> tags that have a .xml extension
    for item in soup.find_all('loc'):
        try:
            if '.xml' in item.text:
                #Send another GET request to the .xml link
                r = requests.get(item.text)
                new_soup = BeautifulSoup(r.text, 'xml')
                for new_item in new_soup.find_all('loc'):
                    website_links.append(new_item.text)
            #If the link doesn't have a .xml extension, add it to the list
            else:
                website_links.append(item.text)
        except TypeError:
            pass
    if verbose:
        print("Found " + str(len(website_links)) + " links in sitemap")
    return(website_links)

def classify_url(id=None, url=None):
    """
    Classify a url as DORIS or OTHER
    """
    if id is None and url is not None:
      id = url[45:]
    
    if (dorisPattern.match(id)):
        return "DORIS"
    if (dorisExtPattern.match(id)):
        return "DORIS (only metadata)"
    for r in prefixes.itertuples(index=False):
        if id.startswith(r.prefix):
            return r.SourceRepository
    return "UNKNOWN"


def jsonl_load(filename):
    data = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # skip empty lines
                data.append(json.loads(line))
    return data

def longestCommonPrefix_binary(strs):
    """
    Find  the Longest Common Prefix in Strings strs
    Source: https://medium.com/@reza.shokrzad/decoding-commonalities-finding-the-longest-common-prefix-in-strings-python-code-ff1e496d32be
    """
    if not strs:
        return ""

    # Helper function to check if all strings have the given prefix
    def is_common_prefix(length):
        str0, count = strs[0][:length], len(strs)
        return all(strs[i][:length] == str0 for i in range(1, count))

    # Binary search for the smallest length at which not all strings match
    min_length = min(len(s) for s in strs)
    low, high = 1, min_length
    
    while low <= high:
        mid = (low + high) // 2
        if is_common_prefix(mid):
            low = mid + 1
        else:
            high = mid - 1
            
    return strs[0][:(low + high) // 2]