import os
import copy
import tableprint as tp
from dynamictableprint import DynamicTablePrint as dtp

from .product import Searcher

#This future price_optimizer is planned to be more modular than current
#by using objects instead of multi-dimensional lists, I hope we future-proof ourself.

'''
Created on Feb 11, 2016
Modified on Dec 7th, 2017

@author: derekyu177
'''

class Sorter(object):

    """
    The ORDER of the SORTS is important: it is the order in which operations
    are applied
    """
    SORTS = [
        "sort_in_stock",
        "sort_cheapest",
    ]

    def __init__(self, products, args):
        self.products = products
        self.args = args

    def sort(self):
        """
        Runs the products rough the gamut of sorting methods
        should return the modified products
        """
        for sorter in self.SORTS:
            getattr(self, sorter)()

        # when reset the index to 'freeze' the sorted indices in place
        return self.products.reset_index(drop=True)

    def sort_cheapest(self):
        """
        Self explanatory: sorts by the cheapest products
        """
        if self.args.sort_cheapest:
            self.products = self.products.sort_values(by=['price'], ascending=True)

    def sort_in_stock(self):
        """
        Self explanatory: filters by products that are instock
        """
        if self.args.only_available:
            self.products = self.products[self.products['in_stock']]


class Reporter(object):
    """
    The reporter deals with data output: it is the coordinator between sorting
    and printing (the latter is delegated to the dynamic table print)
    """

    def __init__(self, args):
        self.args = args
        searcher = Searcher(args.product, verbose=args.verbose)
        self.unsorted_products = searcher.search(args.pages)
        self.sorted_products = None
        self.product_info = searcher.product_info()
        self.printer = None

    def write_to_file(self):
        """
        Writes the data to file
        """
        if not self.args.tofile:
            return


    def write_to_screen(self):
        """
        Uses DynamicTablePrint to properly format the table for command line
        viewing
        """
        if not self.args.toconsole:
            return

        self.printer.config.banner = \
            'Looking up {}: {} pages of {}'.format(
                self.args.product,
                self.args.pages,
                self.product_info['total_number_pages']
            )
        self.printer.write_to_screen()

    def report(self):
        """
        Runs the sorted_products through to be printed and written to file if
        required by the user
        """
        self.sorted_products = Sorter(self.unsorted_products, self.args).sort()
        self.printer = dtp(self.sorted_products, squish_column='item', angel_column='price')

        self.write_to_screen()
        self.write_to_file()
