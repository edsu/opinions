#!/usr/bin/env python

import requests

from urlparse import urljoin
from bs4 import BeautifulSoup

def crawl():
    for term_page_url in get_term_pages():
        table = get_table(term_page_url)
        return

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
    
if __name__ == "__main__":
    crawl()
