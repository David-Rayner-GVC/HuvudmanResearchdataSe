import extruct
import requests
from w3lib.html import get_base_url
import os.path


def extract_metadata(url):
    """Extract json-ld metadata from the scheme.org in a page and return as a dictionary. 
    
    Args:
        url (string): URL of page from which to extract metadata. 
    
    Returns: 
        metadata (dict): json-ld
        url: the url that url redirects to.   
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

    # test code!!
    #url_try_order = [url]
    #

    for u in url_try_order:
      r = requests.get(u)
      try:
        base_url = get_base_url(r.text, r.url)
        metadata = extruct.extract(r.text, 
                                  base_url=base_url,
                                  uniform=True,
                                  syntaxes=['json-ld'])
        metadata = metadata['json-ld']    
        assert len(metadata)==1, "expected 1 json-ld dict, got %i"%len(metadata)
        metadata = metadata[0]
        return metadata
      except:
        continue
    raise


def download_json_metadata(url):
    """
    Download the json metadata file for a SND url VERSION 1and return as a dictionary. 
    
    Args:
    url (string): URL of page from which to extract metadata. 
        
    Returns: 
    metadata (dict): json contents.  
    url: the url that url redirects to.  
    
    Tries various urls for the json file, does not read them from the url  
    """
    id = os.path.basename(os.path.normpath(url))
    if "snd" in id or "ext" in id:
      json_location_try_order = ['/1.0/export/json', '/1/export/json']
    else:
      json_location_try_order = ['/1/export/json','/1.0/export/json' ]
    
    metadata=dict()
    try:
      json_url = url + json_location_try_order[0]
      resp = requests.get(json_url)
      metadata =resp.json()
    except:
      json_url = url + json_location_try_order[1]
      resp = requests.get(json_url)
      metadata =resp.json()
    
    assert 'creatorPerson' in metadata, "expected metadata to contain creatorPerson"
    assert 'publishedDate' in metadata, "expected metadata to contain publishedDate"
    return metadata

