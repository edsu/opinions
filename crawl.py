#!/usr/bin/env python

import requests

from urlparse import urljoin
from bs4 import BeautifulSoup

def crawl():
    for term_page_url in get_term_pages():
        table = get_table(term_page_url)
        for row in table:
            opinion = []
            opinion_type = _opinion_type(term_page_url)
            if opinion_type == "slip":
                opinion = row
            else:
                opinion = row
            print opinion

def get_term_pages():
    url = "http://www.supremecourt.gov/opinions/opinions.aspx"
    doc = _get(url)
    urls = []
    for a in doc.select('div.dslist2 ul li a'):
        urls.append(urljoin(url, a.get('href')))
    return urls

def get_table(url):
    doc = _get(url)
    table = [[th.string for th in doc.select('.datatables tr th')]]
    for tr in  doc.select('.datatables tr'):
        row = []
        for td in tr.select('td'):
            a = td.select('a')
            if len(a) > 0: 
                row.append(a[0])
            else:
                row.append(td)
        if len(row) > 0:
            table.append(row)
    return table

def _get(url):
    headers = {"User-Agent": "Opinions <http://github.com/edsu/opinions"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return BeautifulSoup(resp.content)
    resp.raise_for_status()

def _opinion_type(url):
    if 'slipopinions' in url:
        return 'slip'
    elif 'relatingtoorders' in url:
        return 'comment'
    elif 'in-chambers' in url:
        return 'in-chambers'
    return None
    
if __name__ == "__main__":
    crawl()
