# from bs4 import BeautifulSoup as bs
from urllib import request, parse
from lxml import html
import argparse
import sys

#This future price_optimizer is planned to be more modular than current
#by using objects instead of multi-dimensional lists, I hope we future-proof ourself.

'''
Created on Feb 11, 2016
Modified on Dec 7th, 2017

@author: derekyu177
'''
class Reporter:
    def report_configuration(self, args):
        product = "Searching for " + args.product
        verbose = "Verbosity level = " + str(args.verbose)

        plural = " pages" if args.pages > 1 else " page"
        pages_to_scrape = "Will scrape " + str(args.pages) + plural

        output_to_screen = "Output to screen = " + str(args.output)
        filename = "Appending to file: " + str(args.filename)

        for configuration in [product, verbose, pages_to_scrape, output_to_screen, filename]:
            print(configuration)

    def __init__(self, args):
        self.args = args
        self.report_configuration(args)
        products = Search(args.product).search(args.pages_to_scrape)
        #TODO: now that we have the products, we have to decide what to do with
        #them

class Search:
	def __init__(self, name):
		self.name = name
        self.site = self._search_url()

	def _search_url(self):
		site = "https://www.newegg.ca"
		path = "/Product/ProductList.aspx"
		query = "?"
		parameters = {
			"Submit": "ENE",
			"Order": "BESTMATCH",
			"Description": self.name,
		}
		return site + path + query + parse.urlencode(parameters)

    def _get_products(self):
		raw_html = request.urlopen(self.site).read()
		document = html.document_fromstring(raw_html)
		element = document.xpath("//div[contains(@class, 'item-container')]")

	def search(self):
        product_elements = self._get_products()

        products = []
        for element in product_elements:
            products.append(Product(element))

        return products

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("No product entered, exiting...")
		sys.exit(0)

	parser = argparse.ArgumentParser()
	parser.add_argument('product', type=str, help='specify the product to search for')
	parser.add_argument('-v', '--verbose', action='store_true', help='specify if verbose')
	parser.add_argument('-p', '--pages', default=1, help='specify how many pages to scrape')
	parser.add_argument('-s', '--output', default=True, help='specify if you desire output to console')
	parser.add_argument('-f', '--filename', default='searches.txt', help='specify the file to append results to')
	args = parser.parse_args()

    Reporter(args).report
