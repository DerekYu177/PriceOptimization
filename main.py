import sys
import argparse

from modules.pricer import Reporter

'''
Created on April 21st, 2018

@author: derekyu177
'''

def report_configuration(args):
    product = "Searching for " + args.product
    verbose = "Verbosity level = " + str(args.verbose)

    if args.pages == 0:
        raise NotImplementedError

    plural = " pages" if args.pages > 1 else " page"
    pages_to_scrape = "Will scrape " + str(args.pages) + plural

    output_to_screen = "Output to screen = " + str(args.output)
    filename = "Appending to file: " + str(args.filename)

    for configuration in [product, verbose, pages_to_scrape, output_to_screen, filename]:
        print(configuration)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No product entered, exiting...")
        sys.exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument('product', type=str, help='specify the product to search for')
    parser.add_argument('-v', '--verbose', action='store_true', help='specify if verbose')
    parser.add_argument('-p', '--pages', type=int, default=1, help='specify how many pages to scrape')
    parser.add_argument('-a', '--only_available', action='store_true', help='shows only items in stock')
    parser.add_argument('-s', '--output', default=True, help='specify if you desire output to console')
    parser.add_argument('-f', '--filename', default='searches.txt', help='specify the file to append results to')
    args = parser.parse_args()

    if args.verbose:
        report_configuration(args)

    Reporter(args).report()

