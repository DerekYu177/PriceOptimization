from urllib import request, parse
from lxml import html

import pandas as pd

class Searcher(object):
    def __init__(self, name, verbose=True):
        self.name = name
        self.verbose = verbose

    def _url(self, page_number):
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

    def _max_page_number(self, document):
        pagination = document.xpath("//span[contains(@class, 'list-tool-pagination-text')]")

        # there will be an even number of elements
        # half for the top, and half for the bottom
        # each half of elements has:
        #   the current number of elements on the screen
        #   the total number of elements
        #   the current page
        #   the total number of pages

        half = pagination[:int(len(pagination)/2)]

        current_elements, all_elements = [e.text for e in half[0].xpath('strong')]
        pages = [e.text for e in half[1].xpath('strong')][0]

        current_page, total_pages = pages.split('/')
        return int(total_pages)

    def _page(self, page_number):
        url = self._url(page_number)
        raw_html = request.urlopen(url).read()
        return html.document_fromstring(raw_html)

    def _get_products(self, number_of_pages):
        product_list = []

        # search one page by default
        primary_page = self._page(1)
        first_page_products = primary_page.xpath("//div[contains(@class, 'item-container')]")
        product_list.extend(first_page_products)

        # early return
        if number_of_pages == 1:
            return product_list

        # scrape all pages
        if number_of_pages == 0:
            number_of_pages = self._max_page_number(primary_page)

        # scrape remaining pages
        for page_number in range(2, 1+number_of_pages):
            document = self._page(page_number)
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

