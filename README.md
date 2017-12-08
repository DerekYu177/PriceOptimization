##### About Me
This is intended to be a small guide on a very simple web scraper for Electronics.
I have used this personally when building my first computer.
It use to have support for NCIX, but as of last week (Dec 2017)...

I will currently only support Newegg.ca for now.

##### Usage
We call this via the command line interface with the following parameters:

`NAME_OF_PRODUCT` Self explanatory. Don't be too specific. If it is more than one word please enclose in `""`

`-v` Verbose

`-p` Number of pages to scrape. By default this will be 1. Setting this value to 0 will scrape all pages.

`-s` Output result to the screen (prettyTable). By default this will be `True`.

`-f` Name of file to append output to. If the file has not been created, a warning will be made and the corresponding `.txt` file will be created.
By default this will create `searches.txt` in the current directory.

###### Example usage
> python3 price_finder "vega 64" -p 0 -s -f vega_result_searches.txt
