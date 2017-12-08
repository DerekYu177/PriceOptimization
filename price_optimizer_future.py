#This future price_optimizer is planned to be more modular than current
#by using objects instead of multi-dimensional lists, I hope we future-proof ourself.

'''
Created on Feb 11, 2016
Modified on Dec 7th, 2017

@author: derekyu177
'''

import argparse
import sys

class Search:
	def __init__(self, name, config):
		self.name = name
		self.config = config

def _print_configurations(args):
	product = "Searching for " + args.product
	verbose = "Verbosity level = " + str(args.verbose)

	plural = " pages" if args.pages > 1 else " page"

	pages_to_scrape = "Will scrape " + str(args.pages) + plural

	output_to_screen = "Output to screen = " + str(args.output)
	filename = "Appending to file: " + str(args.filename)

	configurations = [product, verbose, pages_to_scrape, output_to_screen, filename]

	for configuration in configurations:
		print(configuration)

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

	_print_configurations(args)
