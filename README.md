# HuvudmanResarchdataSe 
A publisher / source perspective on who publishes datasets that are indexed in the Researchdata.se research data portal.



## Running the analysis
read_metadata.py - currently reads the mega json dump from file (specified on command line) and writes a csv file with "Publisher", "SourceRepository", "YearPublished".
                  Outfile is also specified on the command line, but target out_data/researchdata_datasets.csv
                  Problem here is that there is no URL, so we can't back off to version 1 to see when first published!

generate_data1.py - this reads data from the schema.org, but there is no info on the source there!!
 researchdata_datasets.jsonl file has fields:
  - URL - Researchdata.se landing page.
  - SourceRepository - Determined from the URL(!). "DORIS", "ECDS", "DORIS_EXTERNAL", or "OTHER". 
  - Version - Generally 0 for OTHER, 1 or 1.0 otherwise
  - YearPublished - YYYY 
  - Publisher1 - huvudman

Make web-app first, then start to develop more!

Ideas for the interactive dashboard!
v1 as now, just be able to select publisher. radio-button from list?
v1a - list publisher by popularity or alphabetical, or search.

v2 - total (ie not by year)

v3 - line plots by source as alternative to stacked bar chart



<!--Comment-->
<!--Supposedly you can use this markdown style to include other text! Would be useful if you want to include statistics.-->
<!--```{include} subfolder/file_to_include.md-->
<!--```-->
