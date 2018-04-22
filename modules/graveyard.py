
# The product optimizer is designed to find prices from multiple sites and 
# append them to a giant PrettyTable readable by the user
'''
Created on Feb 11, 2016

@author: derekyu
'''

# -*- coding: utf-8 -*-
from lxml import html
from prettytable import PrettyTable
import requests, os, re, sys, getopt

def file_is_empty(path):
    return os.stat(path).st_size == 0

def file_exists(path):
    return os.path.exists(path)

def microcenter_search(type, search_term):
    site = "MicC (US)"
    #take in the search term in the form Xeon-E3 (one word, no spaces)
    #and outputs two n length lists where one of them contains the name and the other contains the price
    base_search = "http://www.microcenter.com/search/search_results.aspx?Ntt="
    terms = search_term.replace(" ", "+")
    page = requests.get(base_search + str(terms))
    tree = html.fromstring(page.content)
    product = tree.xpath('//div[@class="normal"]/h2/a/text()')
    prices = tree.xpath('//div[@class="price"]/span[@itemprop="price"]/text()')
    for i in range(len(prices)):
        prices[i] = "US" + str(prices[i])
    return zipper(type, search_term, product, prices, site)

def amazonca_search(type, search_term):
    site = "amaz (CA)"
    base_search = "http://www.amazon.ca/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
    terms = search_term.replace(" ", "+")
    page = requests.get(base_search + str(terms))
    tree = html.fromstring(page.content)
    product = tree.xpath('//h2[@class="a-size-medium a-color-null s-inline s-access-title a-text-normal"]/text()')
    prices = tree.xpath('//span[@class="a-size-base a-color-price s-price a-text-bold"]/text()')
    for i in range(len(prices)):
        prices[i] = str(prices[i]).replace("CDN$ ", "CA")
    return zipper(type, search_term, product, prices, site)

def ncix_search(type, search_term):
    site = "NCIX (CA)"
    terms = search_term.replace(" ", "+")
    base_search = "http://search.ncix.com/search/ajaxsearch.cfm?q="
    page = requests.get(base_search + terms)
    tree = html.fromstring(page.content)
    product = tree.xpath('//span[@class="listing"]/a/text()')
    prices = tree.xpath('//font[@class="listing"]/strong/text()')
    #We simply strip the "$", and "," from the number, and append a "CA" in front to represent Canadian Dollars
    for i in range(len(prices)):
        prices[i] = "CA" + str(prices[i][1:]).replace(",", "")
    return zipper(type, search_term, product, prices, site)

def newegg_search(type, search_term):
    site = "Negg (CA)"
    terms = search_term.replace(" ", "+")
    base_search = "http://www.newegg.ca/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description=" + str(terms) +  "&N=-1&isNodeId=1"
    page = requests.get(base_search)
    tree = html.fromstring(page.content)
    product = tree.xpath('//span[@style="display:inline"]/text()')
    prices = tree.xpath('//li[@class="price-current "]/strong/text() | //li[@class="price-current is-price-current-list"][1]/strong/text()')

    for i in range(len(prices)):
        prices[i] = "CA" + str(prices[i]).replace(",", "")
    return zipper(type, search_term, product, prices, site)


def zipper(type, search_term, product, prices, site):
    #this takes in the product and prices and puts them
    #into the single table r_data. We do this to increase modularity with other components
    r_data = []
    #This simply ensures that we take the lcd for the length of the data
    if (len(product) == len(prices)) or (len(product) < len(prices)) : length = len(product)
    else : length = len(prices)
    #if the data is related to the search term, we add it to r_data
    for i in range(length):
        #we want to determine whether the product contains the search term
        if filter(product[i], search_term):
            r_data.append([type, product[i], prices[i], site])
    return r_data

def convertcurr():
    #looks up the most up-to-date USD-CAD conversion to ensure accuracy
    page = requests.get("https://www.google.ca/finance?q=usdcad")
    tree = html.fromstring(page.content)
    exchange_rate = tree.xpath('//span[@class="bld"]/text()')
    usdcad = ((exchange_rate[0]).split())[0]
    cadusd = (1/float(usdcad))
    return [float(usdcad),float(cadusd)]

def table(data):
    table = PrettyTable(["Component","$USD","$CAD", "Site","Name"])
#     table.align["Component"] = "l"
    table.align["Name"] = "l"
    table.align["$USD"] = "r"
    table.align["$CAD"] = "r"
#     table.max_width = 50
    usdcad = convertcurr()[0]
    cadusd = convertcurr()[1]
    for i in range(len(data)):
        curr = str(data[i][2])[:2]
        #truncate the currency "tag" on the value, and convert from usd to cad or vice versa as required.
        data[i][2] = float(str(data[i][2][2:]).replace(",", ""))
        if curr == "US":
            usd = (round(int(data[i][2])))
            cad = (round(int(data[i][2])*usdcad))
        elif curr == "CA":
            usd = (round(int(data[i][2]*cadusd)))
            cad = (round(int(data[i][2])))
        #appends the table by row with the new data
        table.add_row([data[i][0], usd, cad, data[i][3], data[i][1]])
    return table

def store(file_name, data, refresh):
    #takes the data and writes it to file_name location. 
    if not file_exists(file_name):
        print "No file exists, creating one now..."
        new_file = open(file_name, 'w')
    with open(file_name, 'r+') as table_file:
        if file_is_empty(file_name) or refresh:
            print "Overwriting data..."
            table_file.truncate()
            table_file.write(str(data))
            print "Done writing to file"

def filter(line, search_terms):
    #returns True if within the description line the search_term occurs. Simple matching. 
    match = False
    try :
        line = str(line).split()
    except UnicodeEncodeError:
        #this exception takes care of Unicode utf-8
        line = re.sub(r'[^\x00-\x7f]',r' ',line)
        line = str(line).split()
    if _debug: 
        print "LINE", line
    search_terms = search_terms.split()
    for item in line:
        for j in range(len(search_terms)):
            if item.upper() == (search_terms[j]).upper():
                match = True
    return match
         
def data_hub(items, file_name, amazon_confirm, ncix_confirm, newegg_confirm, microcenter_confirm):                 
    master_table = []
    for i,x in enumerate(items):
        if amazon_confirm:
            print "Searching Amazon..."
            partial_data4 = amazonca_search(x, items[x])
            for m in range(len(partial_data4)):
                master_table.append(partial_data4[m])
            if _debug: 
                print "DATA4", partial_data4
            print "Done"
        if ncix_confirm:
            print "Searching NCIX..."
            partial_data2 = ncix_search(x, items[x])
            for k in range(len(partial_data2)):
                master_table.append(partial_data2[k])
            if _debug: 
                print "DATA2", partial_data2
            print "Done"
        if newegg_confirm:
            print "Searching Newegg..."
            partial_data3 = newegg_search(x, items[x])
            for l in range(len(partial_data3)):
                master_table.append(partial_data3[l])
            if _debug: 
                print "DATA3", partial_data3    
            print "Done"
        if microcenter_confirm:
            print "Searching MicroCenter..."
            partial_data1 = microcenter_search(x, items[x])
            for j in range(len(partial_data1)):
                master_table.append(partial_data1[j])
            if _debug:
                print "DATA1", partial_data1
            print "Done"

    #if nothing is actually being searched then we do not want to override the previous table
    if not (amazon_confirm or ncix_confirm or newegg_confirm or microcenter_confirm):
        if _debug:
            print "There is no data being written"
        print "No Search, use the command -i for more information, or -d to enable debug (verbose)"
        print "Have you selected a search site?"
        return 
    else:
        #convert the master_table into a more visually appealing table
        master_table = table(master_table)
        master_table.sortby = "$CAD"
        if _debug : 
            print "MAST\n", master_table
        store(file_name, master_table, True)

def main(argv):
    items = {}
    amazon_confirm = False
    ncix_confirm = False
    newegg_confirm = False
    microcenter_confirm = False
    global _debug
    _debug = False
    file_name = "MicroCenter.csv"
    try :
        opts, args = getopt.getopt(argv, "ic:y:e:b:g:t:f:axnmdu:", ["info", "cpu=", "memory=", "case=", "motherboard=", "graphics=", "storage=", "filename=", "unique_search="])
        #c = cpu
        #y = memory
        #e = case
        #b = motherboard
        #g = graphics
        #t = storage
    except getopt.GetoptError:
        print "command not recognized, type -i for info or exit"
        sys.exit()
    for opt, arg in opts:
        if opt == "-i":
            print "Welcome to the Price_Optimizer!"
            print "-c[--cpu] -y[--memory] -e[--case] -b[--motherboard] -g[--graphics] -t[--storage]"
            print "-a for amazon -x for ncix, -n for newegg, -m for microcenter"
            print "-u[--unique_search] if you want to search for something else"
            sys.exit()
        if opt == "-d": 
            print "Entering debug mode..."
            _debug = True
        elif opt == "-a": amazon_confirm = True
        elif opt == "-x": ncix_confirm = True
        elif opt == "-n": newegg_confirm = True
        elif opt == "-m": microcenter_confirm = True
        elif opt in ("-c", "--cpu"): items["CPU"] = arg
        elif opt in ("-y", "--memory"): items["Memory"] = arg
        elif opt in ("-e", "--case"): items["Case"] = arg
        elif opt in ("-b", "--motherboard"): items["Motherboard"] = arg
        elif opt in ("-g", "--graphics"): items["Graphics"] = arg
        elif opt in ("-t", "--storage"): items["Storage"] = arg
        elif opt in ("-f", "--filename"): file_name = arg
        elif opt in ("-u", "--unique_search"): items["Unique"] = arg
    for key in items:
        print key, ":", items[key]
    data_hub(items, file_name, amazon_confirm, ncix_confirm, newegg_confirm, microcenter_confirm)
    print "Thank you for using the Price_Optimizer!"



if __name__ == "__main__":
    main(sys.argv[1:])
