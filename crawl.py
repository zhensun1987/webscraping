"""get US patent information"""

from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import urllib2
import argparse
from bs4 import BeautifulSoup
from lxml import html
import os, re
import unicodecsv, csv

starttime = time.time()

## build the url of the link
def build_url(link):
    url = "https://www.google.com/patents/US" + link
    return url

## send a request to the server
def build_request(url):
    request = urllib2.Request(url)
    request.add_header("Accept", "text/html")
    request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0")
    return request

## open the page
def open_page(request): 
    page = urllib2.urlopen(request).read()
    return page

## parse and get the data using BeautifulSoup
def parse_data_bs(page): 
    ## assign empty strings to the variables in case they are missing from the web
    [inventor, assignee, publication_date, filing_date] = ['', '', '', '']
    ## parse the data in beautifulsoup
    soup = BeautifulSoup(page)
    ## get header information 
    headings = soup.findAll('td', {'class': 'patent-bibdata-heading'})
    for heading in headings:
        if "Inventors" in heading.getText():
            inventor = heading.nextSibling.getText()
        if "Assignee" in heading.getText():
            assignee = heading.nextSibling.getText()
        if "Publication date" in heading.getText():
            publication_date = heading.nextSibling.getText()
        if "Filing date" in heading.getText():
            filing_date = heading.nextSibling.getText()    
    return [inventor, assignee, publication_date, filing_date]

##  parse and get the data using LXML
def parse_data_lxml(page):
    ## assign empty strings to the variables in case they are missing from the web
    [inventor, assignee, publication_date, filing_date] = ['', '', '', '']
    ## parse the data in lxml
    doc = html.fromstring(page)
    ## get header information 
    headings = doc.cssselect('td.patent-bibdata-heading')  # not cssselect returns a list
    for heading in headings:
        if "Inventors" in heading.text_content():
            inventor = heading.getnext().text_content()
        if "Assignee" in heading.text_content():
            assignee = heading.getnext().text_content()
        if "Publication date" in heading.text_content():
            publication_date = heading.getnext().text_content()
        if "Filing date" in heading.text_content():
            filing_date = heading.getnext().text_content()    
    return [inventor, assignee, publication_date, filing_date]

## parse and get the data using one of the parsers, the default parser is lxml
def parse_data(page, flag_bs = False, flag_lxml = True, flag_type = False):
    if flag_bs:
        data = parse_data_bs(page)
    if flag_lxml:
        if flag_type:
            data = parse_data_type(page)
        else:
            data = parse_data_lxml(page)
    return data
    
def save_data(listdata, filename):
    '''
    save listdata to a csv file with name filename
    '''
    with open(filename, 'wb') as csvfile:
        writer_to_csv = unicodecsv.writer(csvfile, delimiter = ',', encoding = 'utf-8')
        writer_to_csv.writerows(listdata)
            
## main function
if __name__ == "__main__":
    ## config argument parser for command line input
    parser = argparse.ArgumentParser(description = "Google Patent Download")
    parser.add_argument("-n", "--patent-number", type = int, dest = "patent_number", help = "the patent number", required = True)
	
    ## mutually exclusive choice of BeautifulSoup or lxml parser
    ## if no parser is specified, use lxml
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-bs", "--BeautifulSoup", action = "store_true", help = "use BeautifulSoup as the parser")
    group.add_argument("-lxml", "--lxml", action = "store_true", help = "use lxml as the parser")
    
    ## get command line input
    args = parser.parse_args()

    ## specify output folder
    datapath = '../data/'
    
    ## create a list to contain all the file names
    header = [["publication_number", "inventor", "assignee", "publication_date", "filing_date"]]
    
    ## generate url and catch the page
    url = build_url(str(args.patent_number))
    request = build_request(url)
    try:
        page = open_page(request)
        if args.BeautifulSoup is False and args.lxml is False:
            args.lxml = True
        data = parse_data(page, args.BeautifulSoup, args.lxml)
        if data:
            data.insert(0, "US" + str(args.patent_number))
            print "US" + str(args.patent_number)
            header.append(data)
    except urllib2.HTTPError:
            print "patent number does not exist"
    filename = datapath + "uspatent_" + str(args.patent_number) + ".csv"
    save_data(header, filename)
print time.time() - starttime
