from bs4 import BeautifulSoup
import requests
import config
import concurrent.futures

sitemap_url = "https://researchdata.se/en/catalogue/sitemap.xml"

def get_urls_from_sitemap(url) -> list:
    if config.debug > 0:
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
    if config.debug > 0:
        print("Found " + str(len(website_links)) + " links")

    # remove the collection urls
    collection_links = set()
    for url in website_links:
        if url.startswith("https://researchdata.se/en/catalogue/collection") or url.startswith("https://researchdata.se/sv/catalogue/collection"):
          collection_links.add(url)
    website_links = set(website_links).difference(collection_links)
    if config.debug > 0:
        print("sitemap.xml contains %d links after removing collections" % len(website_links))

    return(list(website_links))

def process_link(url):
    if config.debug > 0:  
        print("Processing %s"%(url))
    # Change to API!
    datasetID = url.replace('https://researchdata.se/en/catalogue/','')
    url = 'https://api.researchdata.se/' + datasetID
    if config.debug > 1:  
        print("   reading from %s"%(url))
    try:
        response = requests.get(url)
    except:
        if config.debug > 0:
            print("process_link failed on "+url)
        return([])
    data = response.json()   
    outdata=dict()
    outdata['DatasetIdentifier'] = datasetID
    outdata['URL'] = url  
    outdata['SourceRepository'] = data["dataset"]["source"]["name"]["en"]
    outdata["Publisher"]=data["dataset"]["principal"]["name"]["en"]
    outdata["YearPublished"]=int(data["dataset"]["publishedDate"][:4])
    
    return outdata

def get_api_metadata_threaded(sitemap_links,test=False):
    if config.debug > 1 or test:
        if config.debug > 1:
            print("cofig.debug > 1, ", end='')
        if test:
            print("test is True, ", end='')
        print("stripping sitemap_links to 30 to make it easier to see what is going on")
        sitemap_links = sitemap_links[:30]

    len_links=len(sitemap_links)

    if (len_links==0):
        if config.debug > 0:
          print("No links to process, exiting")
        return
    else:
        if config.debug > 1:
          print("processing %d links" % len_links)  

    sitemap_links = list(sorted(sitemap_links))

    results = []

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:

        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(process_link, url): url
            for url in sitemap_links
        }

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]

            try:
                data = future.result()
            except Exception as exc:
                print(f"{url!r} generated an exception: {exc}")
            else:
                results.append(data)
    return results

def scrapeREDA(format='dict',test=False,debug=None):
    # scrapeREDA as either 'dict' (default) or 'DataFrame'
    # test (default False) - if True, only process first 30 datasets
    # debug (default is from config.debug) - set config.debug. 0 is silent, 1 is messages, 2 is trace
    if debug is not None:
        config.debug = debug
    sitemap_links=get_urls_from_sitemap(sitemap_url)
    if config.debug > 2:
        print(sitemap_links)
    #results =[process_link(sitemap_links[0]),process_link(sitemap_links[1])]
    results=get_api_metadata_threaded(sitemap_links,test)

    if (format.lower()=='dataframe'):
      import pandas as pd
      results = pd.DataFrame(results)

    return results

if __name__ == '__main__':
    scrapeREDA(format='dict',test=True)
    print(results)
