#This future price_optimizer is planned to be more modular than current
#by using objects instead of multi-dimensional lists, I hope we future-proof ourself. 

'''
Created on Feb 11, 2016

@author: derekyu
'''

from lxml import html

class Product:

	""" Each product will be a object who's properties we will add to. """
	def __init__(self, name):
		#the name of the product is what is listed
		self.name = name

	def convertCurr():
		#looks up the most up-to-date USD-CAD conversion to ensure accuracy
		page = requests.get("https://www.google.ca/finance?q=usdcad")
		tree = html.fromstring(page.content)
		exchange_rate = tree.xpath('//span[@class="bld"]/text()')
		usdcad = ((exchange_rate[0]).split())[0]
		cadusd = (1/float(usdcad))
		return [float(usdcad),float(cadusd)]

	def addValue(self, native_currency, native_price):
		self.native_currency = native_currency
		self.native_price = native_price
		usdcad = convertCurr()[0]
		cadusd = convertCurr()[1]
		if native_currency.upper() == "US":
			self.nonnative_currency = "CA"
			self.nonnative_price = usdcad*native_price
		elif native_currency.upper() == "CA":
			self.nonnative_currency = "US"
			self.nonnative_price = cadusd*native_price

	def addStore(self, store, link):
		self.store = store
		self.link = link

	def addGenre(self, genre):
		#genre is in which the product fits
		#i.e. CPU, Motherboard
		self.genre = genre

class Search:
	""" Call upon this class when we want to do the web scraping """

	#the site that we search
	#Q: p1 only?
	global base_search 
	base_search = {
	"microcenter" : "http://www.microcenter.com/search/search_results.aspx?Ntt=",
	"ncix" : "http://search.ncix.com/search/ajaxsearch.cfm?q=",
	"newegg" : "http://www.newegg.ca/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description="
	}

	#the xpath we take to scrape the product names 
	global product_xpath
	product_xpath = {
	"microcenter" : '//div[@class="normal"]/h2/a/text()',
	"ncix" : '//span[@class="listing"]/a/text()',
	"newegg" : '//span[@style="display:inline"]/text()'
	}

	#the xpath to scrape the price from the site
	#if there is a mismatch, this is where the problem will most likely be
	#vulnerable to site HTML tag 
	global price_xpath
	price_xpath = {
	"microcenter" : '//div[@class="price"]/span[@itemprop="price"]/text()',
	"ncix" : '//font[@class="listing"]/strong/text()',
	"newegg" : '//li[@class="price-current "]/strong/text() | //li[@class="price-current is-price-current-list"][1]/strong/text()'
	}

	global storeCurrency
	storeCurrency = {
	"microcenter" : "US"
	"ncix" : "CA"
	"newegg" : "CA"

	}

	global masterList
	masterList = []

	def __init__(self, site, search_term):
		term = search_term.replace(" ", "+")
		self.site = "N/A"
		for sites in base_search.keys():
			if site == sites:
				self.site = site
				self.link = base_search[site] + term
 				#the exception to the rule
				if self.site == "newegg":
					self.site = self.site.append(str(search_term) + "&N=-1&isNodeId=1")

	def scrape(self, site, target_site, target_search_term):
		#this produces a product list and a price list. 
		page = requests.get(target_site)
		tree = html.fromstring(page.content)
		self.product = tree.xpath(product_xpath[site])
		self.price = tree.xpath(price_xpath[site])
		self.col_length = max(len(self.product), len(self.price))

	def productList(self):
		#here we expect to create a list of length col_length populated by product objects
		for i in self.col_length
			p = Product(self.product[i])
			p.addValue()
			masterList.append()
		

	def zipUp(self, product, product_name, product_price):
		#appends the products with the appropriate product name and price list
		pass

class Visualizer:
	"""We pass our list of product objects here where they will be visualized"""
	def __init__(self):
		pass

s = Search("newegg", "Xeon E3")
print s.site, s.link




