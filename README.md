# HuvudmanResarchdataSe 
A publisher / source perspective on who publishes datasets that are indexed in the Researchdata.se research data portal.

## Folder commmon
Stuff useful for both predata and dashboard!

## Folder prepdata
Code for creating a lite csv file that can be used in the dashboard.

read_metadata.py - currently reads the mega json dump from file (specified on command line) and writes a csv file with "Publisher", "SourceRepository", "YearPublished".
                  Outfile is also specified on the command line, but target out_data/researchdata_datasets.csv
                  Problem here is that there is no URL, so we can't back off to version 1 to see when first published!

generate_data1.py - this reads data from the schema.org, but there is no info on the source there!! THIS FILE IS NOT UP-TO-DATE

## Folder dashboard
shiny app to show results.

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
