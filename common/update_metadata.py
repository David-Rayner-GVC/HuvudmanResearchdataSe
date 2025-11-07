import extruct
import requests
from w3lib.html import get_base_url
import json
import os.path
import utils
import sys
import pandas as pd

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


def extract_metadata(url):
    """Extract json-ld metadata from the page and return as a dictionary. 
    
    Args:
        url (string): URL of page from which to extract metadata. 
    
    Returns: 
        metadata (dict): json-ld.    
    Source:
        https://practicaldatascience.co.uk/data-science/how-to-scrape-schemaorg-metadata-using-python
    """
    
    r = requests.get(url)

    base_url = get_base_url(r.text, r.url)
    metadata = extruct.extract(r.text, 
                               base_url=base_url,
                               uniform=True,
                               syntaxes=['json-ld'])
    metadata = metadata['json-ld']    
    assert len(metadata)==1, "expected 1 json-ld dict, got %i"%len(metadata)
    return metadata[0]


def add_new_datasets_from_sitemap(data):
  """
  Update metdata by looking for new datasets from sitemap.xml
  data - dataframe from existing metadata.csv
  return dataframe in same format
  """
  
  sitemap_url = "https://researchdata.se/en/sitemap.xml"

  sitemap_links = set(utils.get_urls_from_sitemap(sitemap_url))

  # remove the collection urls
  collection_links = set()
  for url in sitemap_links:
    if url.startswith("https://researchdata.se/en/catalogue/collection") or url.startswith("https://researchdata.se/sv/catalogue/collection"):
      collection_links.add(url)
  sitemap_links = sitemap_links.difference(collection_links)
  sitemap_ids = set(map(lambda x: x.rsplit('/', 1)[-1], sitemap_links))

  print("sitemap.xml contains %d links after removing collections" % len(sitemap_links))

  if data is None or data.empty:
    new_ids = sitemap_ids
    data = []
  else:   
    old_ids = set(data['DatasetIdentifier'])
    old_ids_to_keep = old_ids.intersection(sitemap_ids)
    boolean_mask = data['DatasetIdentifier'].isin(old_ids_to_keep)
    data = data.loc[boolean_mask]

    new_ids = sitemap_ids.difference(old_ids)
    numIds = len(new_ids)
    print(f"found {numIds} new datasaets to process in sitemap")

  df = pd.DataFrame(columns=["DatasetIdentifier","DatasetIdentifierV1","Publisher", "SourceRepository", "YearPublished"])
  for id in list(new_ids):
    url = "https://researchdata.se/en/catalogue/dataset/" + id
    try:
        j = extract_metadata(url)
        new_row = [id,id,j['publisher']['name'],utils.classify_url(id=id),j['datePublished'][0:4]]
        print(new_row)
        df.loc[len(df)] = new_row
    except KeyboardInterrupt:
        exit()
    except:
        print("WARNING! Error processing new URL " + url)
     
  
  data2 = pd.concat([data, df])
  return data2
  
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_metadata.py ../dashboard/data/metadata.csv")
        sys.exit(1)

    data = pd.read_csv(sys.argv[1])
    data2 = add_new_datasets_from_sitemap(data)
    data2.to_csv(sys.argv[1], index=False, float_format='%.3f') 

