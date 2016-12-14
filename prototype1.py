from lxml import html
from itertools import izip, chain
from prettytable import PrettyTable
import requests
import os
import fnmatch

def file_is_empty(path):
    return os.stat(path).st_size == 0

def file_exists(path):
    return os.path.exists(path)

def prettyfile(unfiltered_data, filtered_data, vendor):
    table = PrettyTable(["Raw Data", "Name","Clock Speed", "Vendor", "price"])
    table.align["Raw Data"] = "l"
    col = table.colcount
    print "FILTERED DATA", filtered_data
    print "UNFILTERED DATA", unfiltered_data
    for i in range(0, len(filtered_data)-1, col-2):
        table.add_row([unfiltered_data[2*(i/(col-2))], filtered_data[i], filtered_data[i+1], vendor, filtered_data[i+2]])
    print "PRETTY TABLE", table
    return table

def keep_data(path, search_product, number_of_products, update):
    if not file_exists(path):
        print "NO FILE EXISTS, CREATING ONE NOW..."
        new_file = open(path, 'w')
    with open(path, 'r+') as test_file:
        if file_is_empty(path) or update:
            print "WRITING NEW DATA INTO FILE"
            test_file.truncate()
            data = ncix(search_product, number_of_products)
            f_data = []
            #data is in form : description, price, description2, price2...
            for i in range(0, len(data), 2):
                print "DATA[" + str(i) + "] :", data[i]
                i_data = CPU_filter(data[i])
                for j in range(len(i_data)):
                    f_data.append(i_data[j])
                    print "APPEND", j, f_data
                #the removal of all non-applicable values. 
                print f_data
                if all(value is None for value in f_data): del f_data[i]
                f_data.append(data[i+1])
            print f_data            
            test_file.write(str(prettyfile(data, f_data, "NCIX")))
            print "DATA WRITTEN" 
        print "RETRIEVING DATA"
        return test_file.read()

def ncix(search_product, number_of_products):
    #This searches through NCIX for the product, and returns an array of the products and its prices
    #uses Web Scraping
    addr = 'http://search.ncix.com/search/ajaxsearch.cfm?q='
    search_product.replace(" ", "+")
    page = requests.get(addr + search_product)
    tree = html.fromstring(page.content)
    buyers = tree.xpath('//a[@style="font-size:10pt"]/text()')
    prices = tree.xpath('//font[@color="#333333"]/strong/text()')
    buyers_prices = list(chain.from_iterable(izip(buyers, prices)))
    print "BUYER_PRICES", buyers_prices
    return buyers_prices

def CPU_filter(product_description):
    #this attempts to determine the name, clock speed, and retailer from the description alone
    #only accepts one description at a time
    product_description = product_description.upper()
    split_product_description = product_description.split()
    print split_product_description
    cpu_name = search(split_product_description, ["1*V?", "E??1*"], ["E?", "1???", "V?"])
    clk_freq = search(split_product_description, ["?.*GHZ", "?.*G", "?.?GHZ", "?.?"], [])
    print [cpu_name, clk_freq]
    return [cpu_name, clk_freq]
    
def search(description, obvious_terms, n_obvious_terms):
    #The goal is to identify all possibilities that a processor could be named:
    #possible options : "E3-1231 v3" or "E3 1231V3" or "E3 1231LV3"
    for s_terms in obvious_terms:
        p = (fnmatch.filter(description, s_terms))
        if p:
            return p[0]
    if not n_obvious_terms:
        print "Search terms not specific enough"
        return 
    #the most difficult option : "E3 1231 V3"
    for i in range(len(description)):
#         print description[i]
#         print (fnmatch.filter(description, n_obvious_terms[1]))
        if not fnmatch.filter(description, n_obvious_terms[1]):
            print "No matches"
            return
        if description[i] == (fnmatch.filter(description, n_obvious_terms[1]))[0]:
            p = t_filter(description, i, n_obvious_terms)
    return p     
    
def t_filter(description, i, search_terms):
    if (description[i-1] == (fnmatch.filter(description, search_terms[0]))[0]) and (description[i] == (fnmatch.filter(description, search_terms[1]))[0]) and (description[i+1] == (fnmatch.filter(description, search_terms[2]))[0]):
        return str(description[i-1]) + "-" + str(description[i]) + "-" +  str(description[i+1])
    
    
    
# print CPU_filter("ASRock Z97 Anniversary ATX LGA1150 1XPCIE3.0X16 3XPCIE2.0X1 3XPCI 6XSATA3 Motherboard")

path = "test_test2.csv"
search_product = "Intel Xeon E3 LGA1150"
number_of_products = 30
update = True
data = keep_data(path, search_product, number_of_products, update)


