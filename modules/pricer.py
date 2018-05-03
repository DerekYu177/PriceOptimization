import os
from itertools import chain
import copy
from urllib import request, parse
from lxml import html
import tableprint as tp
import pandas as pd

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
        self.products = Searcher(args.product, verbose=args.verbose).search(args.pages)

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
            'Looking up: {}'.format(self.args.product),
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

class Searcher(object):
    def __init__(self, name, verbose=True):
        self.name = name
        self.verbose = verbose

    def _search_url(self, page_number):
        site = "https://www.newegg.ca"
        path = "/Product/ProductList.aspx"
        query = "?"
        parameters = {
            "Submit": "ENE",
            "Order": "BESTMATCH",
            "Description": self.name,
            "Page": page_number,
        }
        full_url = site + path + query + parse.urlencode(parameters)

        if self.verbose:
            print('searched site: {}'.format(full_url))

        return full_url

    def _get_products(self, number_of_pages):
        product_list = []

        for page_number in range(1, 1 + number_of_pages):
            site = self._search_url(page_number)

            raw_html = request.urlopen(site).read()
            document = html.document_fromstring(raw_html)

            products = document.xpath("//div[contains(@class, 'item-container')]")
            product_list.extend(products)

        return product_list

    def search(self, number_of_pages):
        products = self._get_products(number_of_pages)
        self.products = [Product(container.__deepcopy__(0)) for container in products]
        self.df = pd.DataFrame([p.data() for p in self.products])

        # sort by cheapest first TODO: make this togglable
        return self.df.sort_values(by=['price'], ascending=True)

class Product(object):

    """
    While the object Product does indeed capture the properties of each
    product, it does not represent the actual product, the representation is
    later transformed into a pandas dataframe

    The products class will take care of which attributes that we represent
    """

    def get_price(self, container):
        price = container.xpath("//li[contains(@class, 'price-current')]")[0]

        price_information = [e.text for e in price]
        useful_information = price_information[1:-1]

        # pricing is the first two, the last is the offers
        price = ''.join(useful_information[0:1])

        # no offer information
        try:
            offers = useful_information[2]
        except IndexError as exception:
            offers = None

        return float(price.replace(",", ""))

    def is_in_stock(self, container):
        stock_info = container.xpath("//p[contains(@class, 'item-promo')]")

        try:
            stock = stock_info[0].text_content() != "OUT OF STOCK"
        except IndexError:
            stock = True

        return stock

    def data(self):
        return { attr:getattr(self, attr) for attr in self.__dict__.keys() }

    def __repr__(self):
        return "Product({})".format(
            str(self.data()).strip("{}").replace(": ", "=").replace("'", "")
        )

    def __init__(self, container):
        item = container.xpath("//a[contains(@class, 'item-title')]")[0]

        self.item = str(item.text_content())
        self.price = self.get_price(container)
        self.in_stock = self.is_in_stock(container)

