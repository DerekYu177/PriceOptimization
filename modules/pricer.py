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
class Reporter(object):

    def __init__(self, args):
        self.args = args
        searcher = Searcher(args.product, verbose=args.verbose)
        self.products = searcher.search(args.pages)
        self.product_info = searcher.product_info()

    def filter_stock(self):
        self.products = self.products[self.products['in_stock'] == True]

    def write_to_file(self):
        pass

    def write_to_screen(self):
        dtp(self.products).write_to_screen()

    def report(self):
        if self.args.only_available:
            self.filter_stock()

        if self.args.output:
            self.write_to_screen()

        self.write_to_file()

        #TODO: now that we have the products, we have to decide what to do with
        #them
