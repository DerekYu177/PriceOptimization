import os
import copy
import tableprint as tp

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

        if args.only_available:
            self.filter_stock()

        if args.output:
            self.write_to_screen()

        self.write_to_file()
        #TODO: now that we have the products, we have to decide what to do with
        #them

    def filter_stock(self):
        self.products = self.products[self.products['in_stock'] == True]


    def write_to_file(self):
        pass

    def write_to_screen(self):
        screen_width, widths = self._fit_screen()

        tp.banner(
            'Looking up: {}, {} pages of {}'.format(
                self.args.product,
                self.args.pages,
                self.product_info["total_number_pages"]
            ),
            width=screen_width
        )

        if self.products.empty:
            tp.banner(
                'ERROR: No results',
                width=screen_width
            )
        else:
            tp.dataframe(self.products, width=widths)

    def _fit_screen(self):
        screen_width = os.get_terminal_size(0)[0]-2

        # we get the maximum width for each category
        # that is not 'item'

        columns = self.products.columns.values.tolist()

        fixed_columns = copy.copy(columns)
        fixed_columns.remove('item')
        column_widths = { column:self._max_width_for(column) for column in
                fixed_columns }

        item_width = screen_width - sum(column_widths.values()) - 8 # padding
        column_widths.update({ 'item':item_width })

        self.products['item'] = self.products['item'] \
                .apply(lambda x: self._item_trucation(item_width, x))

        widths = tuple([column_widths[column] for column in columns])
        return screen_width, widths

    def _item_trucation(self, width, line):
        return line if len(line) < width else line[:width-3] + '...'

    def _max_width_for(self, item):
        product_width = self.products[item] \
                .apply(lambda x: len(str(x))) \
                .max()

        name_width = len(str(item))
        return max(product_width, name_width)

    def report(self):
        pass

