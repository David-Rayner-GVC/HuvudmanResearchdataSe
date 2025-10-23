import extruct
import requests
from w3lib.html import get_base_url
import json
import os.path
import utils

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
    three = url[45:48]
    if (three.isdigit() or three=='ext'):
        url_try_order = [url+'/1', url+'/1.0', url]
    elif (three=='ecd' or three=='snd'):
        url_try_order = [url+'/1.0', url+'/1', url]
    else:
        url_try_order = [url]
    
    r = requests.get(url)

    base_url = get_base_url(r.text, r.url)
    metadata = extruct.extract(r.text, 
                               base_url=base_url,
                               uniform=True,
                               syntaxes=['json-ld'])
    metadata = metadata['json-ld']    
    assert len(metadata)==1, "expected 1 json-ld dict, got %i"%len(metadata)
    return metadata[0]


def get_new_sitemap_links(data):
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
    # ==> now create data from the ids! 
    data = []
  else:   
    old_ids = set(data['DatasetIdentifier'])
    old_ids_to_keep = old_ids.intersection(new_ids)
    boolean_mask = data['DatasetIdentifier'].isin(old_ids_to_keep)
    data = data.loc[boolean_mask]

    new_ids = sitemap_ids.difference(old_ids)
    # ==> now create new_data from the new_ids! 
    # then combine with data and return!

  return data
  