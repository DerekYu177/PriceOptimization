import sys
import argparse

from modules.pricer import Reporter

'''
Created on April 21st, 2018

@author: derekyu177
'''

def _pages(pages):
    if pages == 0:
        return "Will scrape all pages"
    elif pages == 1:
        return "Will scrape 1 page"

    return "Will scrape {} pages".format(pages)

def report_configuration(args):
    """
    Helpful for debugging
    """
    if not args.verbose:
        return

    product = "Searching for " + args.product
    verbose = "Verbosity level = " + str(args.verbose)

    pages_to_scrape = _pages(args.pages)

    output_to_screen = "Output to screen = " + str(args.output)
    filename = "Appending to file: " + str(args.filename)

    for configuration in [product, verbose, pages_to_scrape, output_to_screen, filename]:
        print(configuration)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No product entered, exiting...")
        sys.exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'product', type=str,
        help='specify the product to search for')
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='specify if verbose')
    parser.add_argument(
        '-p', '--pages', type=int, default=1,
        help='specify how many pages to scrape, "0" for all available pages')
    parser.add_argument(
        '-a', '--only_available', action='store_true',
        help='shows only items in stock')
    parser.add_argument(
        '-c', '--sort_cheapest', action='store_true',
        help='sorts items by price, lowest to most expensive')
    parser.add_argument(
        '-s', '--toconsole', default=True,
        help='specify if you desire output to console')
    parser.add_argument(
        '-w', '--tofile', action='store_true',
        help='specify if you desire to output to file. ' \
             'this can be done in tandem with --toconsole')
    parser.add_argument(
        '-f', '--filename', default='searches.txt',
        help='specify the file to append results to')
    ARGS = parser.parse_args()

    report_configuration(ARGS)
    Reporter(ARGS).report()

