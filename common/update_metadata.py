import extruct
import requests
from w3lib.html import get_base_url
import json
import os.path
import utils
import sys
import pandas as pd
from get_zenodo_community import get_zenodo_community
import argparse

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

def getMetadataFromApi(datasetIdentifier):
   """
   Get metdata from 
      https://api.researchdata.se/dataset/sites-gvqym0anpryfrtn2cpeuzzwf
   style link.
   If strip==True, only return essential metadata
   """
   url = "https://api.researchdata.se/dataset/" + datasetIdentifier
   r = requests.get(url)
   assert r.status_code == 200
   dr = json.loads(r.text)
   
   metadata={}
   metadata["DatasetIdentifier"]=dr['dataset']['datasetIdentifier']
   metadata["Publisher"]=dr['dataset']['principal']["name"]["en"]
   metadata["SourceRepository"]=dr['dataset']['source']['name']['en']
   metadata["YearPublished"]=dr['jsonLd']['datePublished'][:4]
   return metadata

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


def add_new_datasets_from_sitemap(data=None):
  """
  Update metdata by looking for new datasets from sitemap.xml
  Inputs:
      data - dataframe from existing metadata.csv. None to load everything from sitemap.xml, takes time!
  Outputs:
  return dataframe in same format:
  columns=["DatasetIdentifier","Publisher", "SourceRepository", "YearPublished"]
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

  if utils.verbose:
    print("sitemap.xml contains %d links after removing collections" % len(sitemap_links))

  if data is None or data.empty:
    new_ids = sitemap_ids
    data = pd.DataFrame(columns=["DatasetIdentifier","Publisher", "SourceRepository", "YearPublished"])

  else:   
    old_ids = set(data['DatasetIdentifier'])
    old_ids_to_keep = old_ids.intersection(sitemap_ids)
    boolean_mask = data['DatasetIdentifier'].isin(old_ids_to_keep)
    data = data.loc[boolean_mask]
    oldNotKept=sum(boolean_mask==False)
    if utils.verbose and (oldNotKept>0):
      print(f"There were {oldNotKept} datasets in the old list that were no longer found in sitemap.xml")

    new_ids = sitemap_ids.difference(old_ids)
    numIds = len(new_ids)
    if utils.verbose:
        print(f"found {numIds} new datasaets to process in sitemap.xml")

  #df = pd.DataFrame(columns=["DatasetIdentifier","Publisher", "SourceRepository", "YearPublished"])
  for id in list(new_ids):
    new_row=getMetadataFromApi(id)
    if utils.verbose:
       print(new_row)
    data.loc[len(data)] = new_row    

  return data

def update_metadata_files(infile=None, outfile=None):
    if infile==None:
        data = None
    else:
        data = pd.read_csv(infile)
    data2 = add_new_datasets_from_sitemap(data)
    if not outfile is None:
        data2.to_csv(outfile, index=False, float_format='%.3f') 
    return data2


  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description ='Create or update the metadata.csv list.')
    parser.add_argument('--infile',
                    default =None,
                    help ='existing metadata.csv file to read and only download updates to it')
    parser.add_argument('--outfile',
                    default =None,
                    help ='file to output to. Suggest ../dashboard/data/metadata_new.csv')
    args = parser.parse_args()
    
    update_metadata_files(args.infile, args.outfile)
