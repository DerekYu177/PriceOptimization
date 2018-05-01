import os
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
        self.products = Searcher(args.product).search(args.pages)

        if args.output:
            self.write_to_screen()

        self.write_to_file()
        #TODO: now that we have the products, we have to decide what to do with
        #them

    def write_to_file(self):
        pass

    def write_to_screen(self):
        tp.banner('Looking up: {}'.format(self.args.product))
        item_width, price_width = self._fit_screen()
        tp.dataframe(self.products, width=(item_width, price_width))

    def _fit_screen(self):
        screen_width = os.get_terminal_size(0)[0]
        price_width = self.products['price'] \
                .apply(lambda x: len(str(x))).max()

        padding = 7

        # we want to stretch the name out to edge of the screen
        # with proper spacing for the price

        available_width = screen_width - price_width - padding

        self.products['item'] = self.products['item'] \
                .apply(lambda x: self._conditional_trucation(available_width, x))

        return available_width, price_width

    def _conditional_trucation(self, width, line):
        return line if len(line) < width else line[:width-3] + '...'

    def report(self):
        pass

class Searcher(object):
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

    def _get_products(self, number_of_pages):
        #TODO: take number_of_pages into account
        raw_html = request.urlopen(self.site).read()
        document = html.document_fromstring(raw_html)
        items = document.xpath("//a[contains(@class, 'item-title')]")
        prices = document.xpath("//li[contains(@class, 'price-current')]")
        return zip(items, prices)

    def search(self, number_of_pages):
        products = self._get_products(number_of_pages)
        self.products = [Product(item, price) for item, price in products]
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

    def clean_price(self, price):
        price_information = [e.text for e in price]
        useful_information = price_information[1:-1]
        # pricing is the first two, the last is the offers
        price = ''.join(useful_information[0:1])

        try:
            offers = useful_information[2]
        except IndexError as exception: # there was no offer information
            offers = None

        return float(price.replace(",", ""))

    def data(self):
        return { attr:getattr(self, attr) for attr in self.__dict__.keys() }

    def __repr__(self):
        return "Product({})".format(
            str(self.data()).strip("{}").replace(": ", "=").replace("'", "")
        )

    def __init__(self, item, price):
        self.item = str(item.text_content())
        self.price = self.clean_price(price)
