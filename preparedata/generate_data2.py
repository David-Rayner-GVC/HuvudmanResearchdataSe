from extract_metadata import download_json_metadata, extract_metadata
import config
import utils
import json
from pathlib import Path
import os
import pprint
import concurrent.futures
import pandas as pd

"""
Get list of datasets and names of PIs, write to config.SND_DATA_FILENAME

generate_data2.py

This version reads url/json rather than scraping the schema.org

If a dataset is version > 1, it recursively backs to the first available version.
This should give a (slightly) better indication of publication date.

Also, the json has field "given name" for PIs!
"""
def get_metadata_for_url(url) -> dict():
  """
  Get DOI, External, YearPublished, GivenNames, Organizations for an SND dataset
  
  Test with
  url="https://snd.se/sv/catalogue/dataset/2024-9" get_metadata_for_url(url)                                        {'url': 'https://snd.se/sv/catalogue/dataset/2024-9', '@id': 'https://doi.org/10.48723/k9wd-9j90', 'YearPublished': 2024, 'Persons': ['Hans Forssberg', 'Angelina Kakooza Mwesige'], 'Organizations': ['Karolinska Institutet, Department Womens and Childrens Health']} 
  """
  data=dict()

  if (config.USE_SCHEMA):
    metadata = extract_metadata(url)
    try:
      data.update(get_data_from_schema(metadata))
    except:
      pprint.pp(metadata)
      raise
  else:
    metadata = download_json_metadata(url)
    try:
      data.update(get_data_from_json_ld(metadata))
    except:
      pprint.pp(metadata)
      raise

  return data

def get_data_from_schema(metadata) -> dict():
  """
  Get DOI, External, YearPublished, GivenNames, Organizations for an SND dataset
  
  Test with
  url="https://snd.se/sv/catalogue/dataset/2024-9" get_metadata_for_url(url)
  {'url': 'https://snd.se/sv/catalogue/dataset/2024-9', 'ID: 'https://doi.org/10.48723/k9wd-9j90', 'YearPublished': 2024, 'Persons': ['Hans Forssberg', 'Angelina Kakooza Mwesige'], 'Organizations': ['Karolinska Institutet, Department Womens and Childrens Health']} 
  """

  data_for_url=dict()
  data_for_url['YearPublished'] = int(metadata['datePublished'][0:4])
  
  if isinstance(metadata['publisher'], dict):
    data_for_url['Publisher1'] = metadata['publisher']['name'].replace("'","")
  elif isinstance(metadata['publisher'], list):
    for idx,p in enumerate(metadata['publisher']):
      data_for_url[f'Publisher{idx}'] = p['name'].replace("'","")
  else:
    data_for_url['Publisher1'] = None

  return(data_for_url)

def get_data_from_json_ld(metadata) -> dict():
  """
  Get DOI, External, YearPublished, GivenNames, Organizations for an SND dataset
  
  Test with
  url="https://snd.se/sv/catalogue/dataset/2024-9" get_metadata_for_url(url)
  {'url': 'https://snd.se/sv/catalogue/dataset/2024-9', '@id': 'https://doi.org/10.48723/k9wd-9j90', 'YearPublished': 2024, 'Persons': ['Hans Forssberg', 'Angelina Kakooza Mwesige'], 'Organizations': ['Karolinska Institutet, Department Womens and Childrens Health']} 
  """
  pass

####################

def get_new_sitemap_links(sitemap_url=None):
  """
  Update local metadatafile from sitemap
  """
  
  if (not sitemap_url):
    sitemap_url = "https://researchdata.se/en/sitemap.xml"

  sitemap_links = set(utils.get_urls_from_sitemap(sitemap_url))

  # remove the collection urls
  collection_links = set()
  for url in sitemap_links:
    if url.startswith("https://researchdata.se/en/catalogue/collection") or url.startswith("https://researchdata.se/sv/catalogue/collection"):
      collection_links.add(url)
  sitemap_links = sitemap_links.difference(collection_links)
  print("sitemap.xml contains %d links after removing collections" % len(sitemap_links))

  my_file = Path(config.SND_DATA_FILENAME)
  if my_file.is_file() and os.stat(my_file).st_size > 0:
    # file exists
    print("Appending to output file "+str(my_file))
    data = []
    with open(config.SND_DATA_FILENAME,"r", encoding="utf-8") as f:
      for line in f:
        if line:  # skip empty lines
          data.append(json.loads(line))
      processed_links = set([x['URL'] for x in data])
      print("Found %d links in existing output file..." % len(processed_links))
      sitemap_links = sitemap_links.difference(processed_links)
      print("... so %d links in the sitemap.xml are new" % len(sitemap_links))
  else:
    print("Creating new output file "+str(my_file))
    with open(config.SND_DATA_FILENAME,"w") as out_file:
      pass
  return sitemap_links

def process_link(url):
  print("Processing %s"%(url))
  data=dict()
  data['URL'] = url  
  data['SourceRepository'] = utils.classify_url(url)
  data.update(get_metadata_for_url(url))
  return data


def update_datafile(sitemap_links):
  len_links=len(sitemap_links)
  
  #args = list(enumerate(sorted(sitemap_links), start=1))
  args = list(sorted(sitemap_links))
  
  with open(config.SND_DATA_FILENAME,"a") as out_file:
    for url in args:
      data = process_link(url)
      print(json.dumps(data, ensure_ascii=False),file=out_file)

def update_datafile_threaded(sitemap_links):
  len_links=len(sitemap_links)
  
  #args = list(enumerate(sorted(sitemap_links), start=1))
  args = list(sorted(sitemap_links))


  with open(config.SND_DATA_FILENAME,"a") as out_file:
    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(process_link, url): url for url in args}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print(json.dumps(data, ensure_ascii=False),file=out_file)

def convert_to_csv():
  snd_data = utils.jsonl_load(config.SND_DATA_FILENAME)
  df = pd.DataFrame(columns=snd_data[0].keys())
  for dataset in snd_data:
    df.loc[len(df)] = dataset
  new_p = config.SND_DATA_FILENAME.with_suffix(".csv")
  df.to_csv(new_p, index=False, float_format='%.3f') 

if __name__ == '__main__':
    sitemap_links=get_new_sitemap_links()
    len_links=len(sitemap_links)
    if (len_links==0):
      print("No links to process, exiting")
    else:
      update_datafile_threaded(sitemap_links)
    convert_to_csv()