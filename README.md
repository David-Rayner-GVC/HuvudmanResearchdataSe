# HuvudmanResarchdataSe 
A publisher / source perspective on who publishes datasets that are indexed in the Researchdata.se research data portal.

## Folder commmon
Stuff useful for both data preparation (creating the metadata.csv base file) and dashboard!

## Folder common
### update_metadata.py
Use this both for creating the metadata.csv and for making an update to the pre-loaded metadata 
To create new:
  python update_metadata.py --outfile  ../dashboard/data/metadata.csv
To update:
  python update_metadata.py  --infile ../dashboard/data/metadata.csv --outfile ../dashboard/data/metadata.csv
But it is (intended to be) also used by dashboard (without actually writing to files) to get a final update too! 

## Folder dashboard
shiny app to show results.
cd dashboard
shiny run app.py


## Deployment
https://david-rayner.shinyapps.io/resarchdatase_publisher_dashboard_demo/


## Futher ideas

Note that you don't need to actually ship the full dataset listing (metadata.csv) with the dashboard, you only need the pivot information from makeplot1.py!

Currently not trying to estimate data-of-first-pubication.

Ideas for the interactive dashboard!


  - list publisher by popularity or alphabetical, or search.

  - show as total (ie not by year)

  - line plots by source as alternative to stacked bar chart

  - radio-buttons to select/deslect which Repositories are shown.



<!--Comment-->
<!--Supposedly you can use this markdown style to include other text! Would be useful if you want to include statistics.-->
<!--```{include} subfolder/file_to_include.md-->
<!--```-->
