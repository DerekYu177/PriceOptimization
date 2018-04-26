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

        write_to_file()
        #TODO: now that we have the products, we have to decide what to do with
        #them

    def write_to_file(self):
        import pdb; pdb.set_trace()

    def write_to_screen(self):
        tp.banner('Looking up: {}'.format(self.args.product))
        import pdb; pdb.set_trace()
        max_width = max(self.products)
        tp.table(self.products, ['items', 'prices'], width)

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
        products = [Product(item, price) for item, price in products]
        return

class Product(object):

    def clean_price(self, price):
        price_information = [e.text for e in price]
        useful_information = price_information[1:-1]
        # pricing is the first two, the last is the offers
        price = ''.join(useful_information[0:1])

        try:
            offers = useful_information[2]
        except IndexError as exception: # there was no offer information
            offers = None

        return price

    def __repr__(self):
        return {
            'Item': str(self.item),
            'Price': float(self.price),
            'Item Name Length': len(self.item)
        }

    def __init__(self, item, price):
        self.item = item.text_content()
        self.price = self.clean_price(price)
