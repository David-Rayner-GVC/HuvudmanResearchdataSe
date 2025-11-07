from bs4 import BeautifulSoup
import requests
import lxml
import json
import re

dorisPattern = re.compile(r"\d\d\d\d-\d+[-\d+]?")

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
    print("Found " + str(len(website_links)) + " links")
    return(website_links)

def classify_url(id=None, url=None):
    """
    Classify a url as DORIS or OTHER
    """
    if id is None and url is not None:
      id = url[45:]
    
    if (id[0:3]=='snd'):
        return "DORIS"
    if (id[0:4]=='ecds'):
        return "DORIS"
    if (dorisPattern.match(id)):
        return "DORIS"
    if (id[0:3]=='ext'):
        return "DORIS (only metadata)"
    if (dorisPattern.match(id)):
        return "DORIS"
    if (id[0:4]=="icos"):
        return("ICOS Sweden data portal")
    if id.startswith('doi-10-23695'): return('Språkbanken Text')
    if id.startswith('doi-10-17044-scilifelab'): return('SciLifeLab Data Repository')
    return "OTHER"

def jsonl_load(filename):
    data = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # skip empty lines
                data.append(json.loads(line))
    return data
