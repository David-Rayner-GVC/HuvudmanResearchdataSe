# HuvudmanResarchdataSe 
A publisher / source perspective on who publishes datasets that are indexed in the Researchdata.se research data portal.

## Folder commmon
Stuff useful for both predata and dashboard!

## Folder prepdata
Code for creating a lite csv file that can be used in the dashboard.
Now with create_aggregated.py that creates a json file (dashboard/data/stats.json) with pre-aggregated counts! But you have to run this AFTER you have updated the metadata, wherever that happens!

### read_metadata.py
currently reads the mega json dump from file (specified on command line) and writes a csv file with "Publisher", "SourceRepository", "YearPublished".
Outfile is also specified on the command line, but target out_data/metadata.csv - keep this as the "raw" csv file.
Problem here is that there is no URL, so we can't back off to version 1 to see when first published!

### create_sources.py 
Usage: python create_sources.py out_data/metadata.csv out_data/sources_RAW.csv
This creates a file with the shortest id prefix for each data source. This can be used to make a guess at the data source for updates that we get from sitemap/json-ld
==> However, the raw output isn't useful, as some SourceRepositories use multiple prefixes!
And a lot just use a common prefix (the Zenodo prefix)
So you need to do some customization of the output before you can make it into a format that common/update_metadata.py can use.
The "fixed" sources.csv file should be put in folder common

### jsonl_to_json.py
Just a utility script, not sure why it is still here.
Converting jsonl to json is useful if your pretty-printer doesn't like jsonl....

## Folder common
### update_metadata.py
Use this both for making an update to the pre-loaded metadata 
python update_metadata.py ../prepdata/out_data/metadata.csv => ../dashboard/data/metadata.csv
But it is (intended to be) also used by dashboard to get a final update too! Note that even when we get SourceRepository in the json-ld, we will still need to have a static dashboard/data/metadata.csv that is updated, or else the UI will be too slow. Unless SND IT make a specific endpoint to support the tool, of course, that would be nice!

## Folder dashboard
shiny app to show results.
cd dashboard
shiny run app.py


## Deployment
https://david-rayner.shinyapps.io/resarchdatase_publisher_dashboard_demo/


## Futher ideas

Note that you don't need to actually ship the full dataset listing (metadata.csv) with the dashboard, you only need the pivot information from makeplot1.py!

Ideas for the interactive dashboard!


  - list publisher by popularity or alphabetical, or search.

  - show as total (ie not by year)

  - line plots by source as alternative to stacked bar chart

  - radio-buttons to select/deslect which Repositories are shown.



<!--Comment-->
<!--Supposedly you can use this markdown style to include other text! Would be useful if you want to include statistics.-->
<!--```{include} subfolder/file_to_include.md-->
<!--```-->
