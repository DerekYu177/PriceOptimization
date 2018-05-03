from urllib import request, parse
from lxml import html

import pandas as pd

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

