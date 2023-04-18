# etdscraper

This project is meant to scrape metadata using scrapy output the data into a json file and then compare those files to check certain fields and will report if they do not match 

Setup:

Make sure you are running in your virtual environment and to install scrapy 

pip install scrapy

The main files that are the curvespider.py and the hyraxspider.py both of which will scrape the data we are looking for. 

Both the hyrax and curve spider can be configured to pull all thesis and all the data if you change the parse method to callback parse_all_pages and this will grab all thesis on curve or hyrax. The other two parse methods are for a single page or with a provided JSON file. You can run it by using this command and it will output it to a json file 

scrapy crawl curvespider -o curve_output.json
scrapy crawl hyraxspdier -o hyrax_output.json

The last part of it is the cuirator_compare.py

This will compare all the fields and dump out any errors in a json files afterwards.
