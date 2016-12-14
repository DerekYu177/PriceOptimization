from lxml import html
import datetime, calendar
from itertools import izip, chain
from prettytable import PrettyTable
import requests
import os, time, fnmatch
from __builtin__ import True

def file_is_empty(path):
    return os.stat(path).st_size == 0

def file_exists(path):
    return os.path.exists(path)

def last_modified(path):
    return os.path.getmtime(path)

def prettyfile(unfiltered_data, filtered_data, vendor, component):
    if (str(component) == "CPU"):
        table = PrettyTable(["Raw Data", "Name","Clock Speed", "Vendor", "price"])
        table.align["Raw Data"] = "l"
        col = table.colcount
        print "FILTERED DATA", filtered_data 
        print "UNFILTERED DATA", unfiltered_data
        for i in range(0, len(filtered_data)-1, col-2):
            table.add_row([unfiltered_data[2*(i/(col-2))], filtered_data[i], filtered_data[i+1], vendor, filtered_data[i+2]])
        print "PRETTY TABLE", table
    else:
        table = PrettyTable(["Raw Data", "price"])
        for i in range(0, len(unfiltered_data), 2):
            table.add_row([unfiltered_data[i], unfiltered_data[i+1]])
    return table

def update_required(path):
    #if the file has been modified more than a day ago then it's time to update
    boundary = 24*60*60
    last_mod = last_modified(path)
    current_time = calendar.timegm(time.gmtime())
    if ((current_time - last_mod) > boundary):
        return True
    return False

def keep_data(path, search_product, number_of_products, update, component):
    #reduces burden on the internet by implementing virtual cache for already recorded data
    if not file_exists(path):
        print "NO FILE EXISTS, CREATING ONE NOW..."
        new_file = open(path, 'w')
    with open(path, 'r+') as test_file:
        if file_is_empty(path) or update_required(path) or update:
            print "WRITING NEW DATA INTO FILE"
            test_file.truncate()
            ncix_data = ncix(search_product, number_of_products)
            amazon_data = amazon_ca(search_product, number_of_products)
            newegg_data = newegg(search_product, number_of_products)
            
            ncix_l = []
            amazon_l = []
            newegg_l = [] 
             
            if (str(component) == "CPU"):
                ncix_l = analysis_CPU(ncix_data)
                amazon_l = analysis_CPU(amazon_data)
                newegg_l = analysis_CPU(newegg_data)

            test_file.write(str(prettyfile(ncix_data, ncix_l, "NCIX", component)))
            test_file.write(str("\n"))
            test_file.write(str(prettyfile(amazon_data, amazon_l, "AMAZON", component)))
            test_file.write(str("\n"))
            test_file.write(str(prettyfile(newegg_data, newegg_l, "NEWEGG", component)))
            test_file.write(str("\n"))
            print "DATA WRITTEN" 
        print "RETRIEVING DATA"
        return test_file.read()

def analysis_CPU(data):
    #takes the data, breaks it up into separate components via CPU_filter
    #which returns the cpu name and clock speed. Therefore it is only valid for CPU tasks. 
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
    return f_data
               

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
    return buyers_prices

def amazon_ca(search_product, number_of_products):
    #searches through amazon.ca, also uses Web Scraping
    product_prices = []
    addr = "http://www.amazon.ca/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
    search_product.replace(" ", "+")
    page = requests.get(addr + search_product)
    tree = html.fromstring(page.text)
    for i in range(0,number_of_products):
        product = tree.xpath('//*[@id="result_' + str(i) + '"]/div/div/div/div[2]/div[1]/a/h2/text()')
        price = tree.xpath('//*[@id="result_' + str(i) + '"]/div/div/div/div[2]/div[2]/div[1]/div[1]/a/span/text()')
        string_product = str(product).translate(None, "''[]")
        string_price = str(price).translate(None, "''[]CND ")
        product_prices.append(string_product)
        product_prices.append(string_price)
        if not string_product:
            return product_prices
    product_prices = filter(None, product_prices)
    return product_prices

def newegg(search_product, number_of_products):
    #a different technique was used here for web scraping due to the different nature of the website architecture for newegg
    #two lists were generated and then stitched together. Prices had to be appended since they did not contain the "$" sign
    search_product.replace(" ", "+")
    addr = "http://www.newegg.ca/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description=" + str(search_product) + "&N=-1&isNodeId=1"
    page = requests.get(addr)
    tree = html.fromstring(page.content)
    buyers = tree.xpath('//span[@style="display:inline"]/text()')
    prices = tree.xpath('//li[@class="price-current "]/strong/text() | //li[@class="price-current is-price-current-list"][1]/strong/text()')
    dprices = []
    for i,value in enumerate(prices):
        dprices.append("$" + value)
    buyers_prices = list(chain.from_iterable(izip(buyers, dprices)))
    return buyers_prices

def CPU_filter(product_description):
    #this attempts to determine the name, clock speed, and retailer from the description alone
    #only accepts one description at a time
    product_description = product_description.upper()
    split_product_description = product_description.split()
    print split_product_description
    cpu_name = search(split_product_description, ["1*V?", "E??1*"], ["E?", "1???", "V?"], ["1150"])
    clk_freq = search(split_product_description, ["?.*GHZ", "?.*G", "?.?GHZ", "?.?"], [], [])
    print [cpu_name, clk_freq]
    return [cpu_name, clk_freq]
    
def search(description, obvious_terms, n_obvious_terms, exceptions):
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
        print "SEARCHING FOR ... ", description[i]
        if description[i] == (fnmatch.filter(description, n_obvious_terms[1]))[0]:
            for j in range(len(exceptions)):
                if description[i] == exceptions[j]:
                    return None
            p = t_filter(description, i, n_obvious_terms)
    return p     
    
def t_filter(description, i, search_terms):
    if (i == len(description)) and (description[i-1] == (fnmatch.filter(description, search_terms[0]))[0]) and (description[i] == (fnmatch.filter(description, search_terms[1]))[0]):
        return str(description[i-1]) + "-" + str(description[i])
    elif (description[i-1] == (fnmatch.filter(description, search_terms[0]))[0]) and (description[i] == (fnmatch.filter(description, search_terms[1]))[0]) and (description[i+1] == (fnmatch.filter(description, search_terms[2]))[0]):
        return str(description[i-1]) + "-" + str(description[i]) + "-" +  str(description[i+1])
    
def search_iterate(item_list):
    for index, item in enumerate(item_list):
        path = str(item_list[item]).replace(" ", "-") + ".csv"
        number_of_products = 30
        update = True
        #print path
        #print str(item_list[item])
        keep_data(path, item_list[item], number_of_products, update, item)
        print "Done"

item_list = {"CPU" : "Intel Xeon E3 LGA1150", "Motherboard" : "Gigabyte 97N", "Case" : "EVGA Hadron Air"}
search_iterate(item_list)

# search_product = "Intel Xeon E3 LGA1150"
# path = "test_data.csv"

update = True
#print keep_data(path, search_product, number_of_products, update)
